#!/usr/bin/env python3
"""
PayTrace Giriş Aracı
Kendi PayTrace hesaplarınızla OAuth 2.0 password grant üzerinden giriş yapar,
access token alır ve isteğe bağlı olarak token'ı dosyaya kaydeder.

Kullanım:
    python3 paytrace_login.py -u KULLANICI -p SIFRE
    python3 paytrace_login.py -u KULLANICI -p SIFRE --sandbox
    python3 paytrace_login.py -f hesaplar.txt
    python3 paytrace_login.py                         # interaktif menü
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

PROD_BASE = "https://api.paytrace.com"
SANDBOX_BASE = "https://api.sandbox.paytrace.com"
VERSION = "1.0.0"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[90m"
RESET = "\033[0m"


def c(text: str, color: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{RESET}"


def banner() -> None:
    print()
    print(c(f"  PayTrace Giriş  v{VERSION}", CYAN + BOLD))
    print(c("  Kendi hesaplarınız için OAuth token alma", DIM))
    print(c(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", DIM))
    print()


def parse_account_line(line: str) -> tuple[str, str] | None:
    """Hesap satırını çözümle: user:pass | user|pass | user pass"""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    for sep in (":", "|", "\t", " "):
        if sep in line:
            user, password = line.split(sep, 1)
            user, password = user.strip(), password.strip()
            if user and password:
                return user, password
    return None


def load_accounts(path: str) -> list[tuple[str, str]]:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Hesap dosyası bulunamadı: {path}")

    accounts: list[tuple[str, str]] = []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            parsed = parse_account_line(raw)
            if parsed is None:
                if raw.strip() and not raw.strip().startswith("#"):
                    print(c(f"  [!] Satır {lineno} atlandı (format hatalı)", YELLOW))
                continue
            accounts.append(parsed)
    return accounts


def login(
    username: str,
    password: str,
    *,
    sandbox: bool = False,
    timeout: int = 30,
) -> dict[str, Any]:
    """
    PayTrace OAuth 2.0 password grant ile giriş.
    Başarıda: {ok, access_token, token_type, expires_in, expires_at, ...}
    Hatalarda: {ok: False, http_code, error}
    """
    base = SANDBOX_BASE if sandbox else PROD_BASE
    url = f"{base}/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json",
    }
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=timeout)
    except requests.exceptions.Timeout:
        return {"ok": False, "http_code": None, "error": "Zaman aşımı"}
    except requests.exceptions.SSLError:
        return {"ok": False, "http_code": None, "error": "SSL sertifika hatası"}
    except requests.exceptions.ConnectionError as exc:
        msg = str(exc)
        if "NameResolution" in msg or "getaddrinfo" in msg:
            return {"ok": False, "http_code": None, "error": "DNS çözülemedi"}
        return {"ok": False, "http_code": None, "error": f"Bağlantı hatası: {msg[:120]}"}
    except requests.RequestException as exc:
        return {"ok": False, "http_code": None, "error": str(exc)[:160]}

    try:
        body = resp.json()
    except ValueError:
        return {
            "ok": False,
            "http_code": resp.status_code,
            "error": f"Yanıt JSON değil: {resp.text[:120]}",
        }

    if resp.status_code == 200 and "access_token" in body:
        expires_in = int(body.get("expires_in") or 7200)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return {
            "ok": True,
            "http_code": 200,
            "username": username,
            "access_token": body["access_token"],
            "token_type": body.get("token_type", "Bearer"),
            "expires_in": expires_in,
            "expires_at": expires_at.isoformat(),
            "created_at": body.get("created_at"),
            "sandbox": sandbox,
        }

    error = body.get("error_description") or body.get("error") or body.get("message")
    if not error:
        error = str(body)[:160]
    return {
        "ok": False,
        "http_code": resp.status_code,
        "error": error,
        "username": username,
    }


def print_login_result(result: dict[str, Any], *, show_token: bool = True) -> None:
    user = result.get("username", "?")
    if result.get("ok"):
        print(c(f"  [OK] Giriş başarılı: {user}", GREEN + BOLD))
        print(f"  Ortam      : {'Sandbox' if result.get('sandbox') else 'Production'}")
        print(f"  Token tipi : {result.get('token_type', 'Bearer')}")
        print(f"  Süre       : {result.get('expires_in')} sn")
        print(f"  Bitiş (UTC): {result.get('expires_at')}")
        if show_token:
            token = result["access_token"]
            preview = f"{token[:24]}...{token[-12:]}" if len(token) > 40 else token
            print(f"  Token      : {preview}")
            print(c("  (Tam token --save veya --json ile alınır)", DIM))
    else:
        code = result.get("http_code") or "-"
        print(c(f"  [HATA] Giriş başarısız: {user}", RED + BOLD))
        print(f"  HTTP       : {code}")
        print(f"  Açıklama   : {result.get('error', 'bilinmeyen hata')}")


def save_token(result: dict[str, Any], path: str) -> None:
    payload = {
        "username": result["username"],
        "sandbox": result.get("sandbox", False),
        "token_type": result.get("token_type", "Bearer"),
        "access_token": result["access_token"],
        "expires_in": result.get("expires_in"),
        "expires_at": result.get("expires_at"),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(c(f"  Token kaydedildi: {path}", GREEN))


def login_one(
    username: str,
    password: str,
    *,
    sandbox: bool,
    timeout: int,
    save_path: str | None,
    as_json: bool,
    show_token: bool,
) -> int:
    result = login(username, password, sandbox=sandbox, timeout=timeout)

    if as_json:
        out = dict(result)
        if out.get("ok") and not show_token:
            out["access_token"] = "<hidden>"
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print_login_result(result, show_token=show_token)

    if result.get("ok") and save_path:
        save_token(result, save_path)

    return 0 if result.get("ok") else 1


def login_many(
    accounts: list[tuple[str, str]],
    *,
    sandbox: bool,
    timeout: int,
    save_dir: str | None,
    as_json: bool,
) -> int:
    results: list[dict[str, Any]] = []
    ok_count = 0

    for idx, (username, password) in enumerate(accounts, 1):
        if not as_json:
            print(c(f"\n  ({idx}/{len(accounts)}) {username}", CYAN))
        result = login(username, password, sandbox=sandbox, timeout=timeout)
        results.append(result)

        if not as_json:
            print_login_result(result, show_token=False)

        if result.get("ok"):
            ok_count += 1
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                safe_name = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in username)
                path = os.path.join(save_dir, f"token_{safe_name}.json")
                save_token(result, path)

    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print()
        print(c(f"  Özet: {ok_count}/{len(accounts)} giriş başarılı", BOLD))

    return 0 if ok_count == len(accounts) and accounts else 1


def interactive_menu(sandbox: bool, timeout: int) -> int:
    banner()
    print("  1) Tek hesap ile giriş")
    print("  2) Dosyadan hesap listesi ile giriş")
    print("  3) Çıkış")
    print()
    choice = input("  Seçim: ").strip()

    if choice == "1":
        username = input("  Kullanıcı adı: ").strip()
        password = getpass.getpass("  Şifre: ")
        if not username or not password:
            print(c("  Kullanıcı adı ve şifre gerekli.", RED))
            return 1
        save = input("  Token dosyaya kaydedilsin mi? [y/N]: ").strip().lower() == "y"
        path = f"token_{username}.json" if save else None
        return login_one(
            username,
            password,
            sandbox=sandbox,
            timeout=timeout,
            save_path=path,
            as_json=False,
            show_token=True,
        )

    if choice == "2":
        path = input("  Hesap dosyası yolu: ").strip() or "hesaplar.txt"
        try:
            accounts = load_accounts(path)
        except FileNotFoundError as exc:
            print(c(f"  {exc}", RED))
            return 1
        if not accounts:
            print(c("  Dosyada geçerli hesap yok.", RED))
            return 1
        save = input("  Başarılı tokenlar kaydedilsin mi? [y/N]: ").strip().lower() == "y"
        return login_many(
            accounts,
            sandbox=sandbox,
            timeout=timeout,
            save_dir="tokens" if save else None,
            as_json=False,
        )

    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="PayTrace OAuth giriş aracı (kendi hesaplarınız için)",
    )
    p.add_argument("-u", "--username", help="PayTrace kullanıcı adı")
    p.add_argument("-p", "--password", help="PayTrace şifresi")
    p.add_argument(
        "-f",
        "--file",
        help="Hesap dosyası (her satır: user:pass, user|pass veya user pass)",
    )
    p.add_argument("--sandbox", action="store_true", help="Sandbox ortamını kullan")
    p.add_argument(
        "--save",
        metavar="PATH",
        help="Başarılı token'ı JSON olarak kaydet (tek hesap)",
    )
    p.add_argument(
        "--save-dir",
        metavar="DIR",
        help="Çoklu girişte tokenların kaydedileceği klasör",
    )
    p.add_argument("--json", action="store_true", help="JSON çıktı")
    p.add_argument(
        "--show-token",
        action="store_true",
        help="JSON çıktıda tam token'ı göster (varsayılan: tek hesap CLI'da gösterilir)",
    )
    p.add_argument("--timeout", type=int, default=30, help="İstek zaman aşımı (sn)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.username and args.password:
        if not args.json:
            banner()
        return login_one(
            args.username,
            args.password,
            sandbox=args.sandbox,
            timeout=args.timeout,
            save_path=args.save,
            as_json=args.json,
            show_token=True if not args.json else args.show_token,
        )

    if args.file:
        if not args.json:
            banner()
        try:
            accounts = load_accounts(args.file)
        except FileNotFoundError as exc:
            print(c(f"  {exc}", RED), file=sys.stderr)
            return 1
        if not accounts:
            print(c("  Dosyada geçerli hesap bulunamadı.", RED), file=sys.stderr)
            return 1
        return login_many(
            accounts,
            sandbox=args.sandbox,
            timeout=args.timeout,
            save_dir=args.save_dir,
            as_json=args.json,
        )

    if args.username or args.password:
        print(c("  Tek hesap için hem -u hem -p gerekli.", RED), file=sys.stderr)
        return 1

    return interactive_menu(sandbox=args.sandbox, timeout=args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
