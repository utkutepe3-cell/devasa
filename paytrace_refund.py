#!/usr/bin/env python3
"""
PayTrace Refund & Void Tool
Settle olmuş işlemler için refund, henüz settle olmamış işlemler için void yapar.

Kullanım:
    python paytrace_refund.py --username API_USER --password API_PASS --transaction-id 12345
    python paytrace_refund.py --username API_USER --password API_PASS --transaction-id 12345 --amount 10.50
    python paytrace_refund.py --username API_USER --password API_PASS --transaction-id 12345 --void
"""

import argparse
import json
import sys
import requests


BASE_URL = "https://api.paytrace.com"
SANDBOX_URL = "https://api.sandbox.paytrace.com"


def get_access_token(base_url: str, username: str, password: str) -> str:
    """PayTrace OAuth2 token al."""
    url = f"{base_url}/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "*/*",
    }
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    resp = requests.post(url, headers=headers, data=data)

    if resp.status_code != 200:
        error_data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        error_msg = error_data.get("error_description", resp.text)
        print(f"[HATA] Giriş başarısız (HTTP {resp.status_code}): {error_msg}")
        sys.exit(1)

    token_data = resp.json()
    return token_data["access_token"]


def refund_by_transaction_id(
    base_url: str,
    access_token: str,
    transaction_id: int,
    integrator_id: str,
    amount: float = None,
) -> dict:
    """Settle olmuş bir işleme refund yap."""
    url = f"{base_url}/v1/transactions/refund/for_transaction"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "transaction_id": transaction_id,
        "integrator_id": integrator_id,
    }
    if amount is not None:
        payload["amount"] = amount

    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()


def void_transaction(
    base_url: str,
    access_token: str,
    transaction_id: int,
    integrator_id: str,
) -> dict:
    """Henüz settle olmamış bir işlemi void (iptal) et."""
    url = f"{base_url}/v1/transactions/void"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "transaction_id": transaction_id,
        "integrator_id": integrator_id,
    }

    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()


def export_transaction(
    base_url: str,
    access_token: str,
    transaction_id: int,
    integrator_id: str,
) -> dict:
    """İşlem detaylarını getir."""
    url = f"{base_url}/v1/transactions/export/by_id"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    payload = {
        "transaction_id": transaction_id,
        "integrator_id": integrator_id,
    }

    resp = requests.post(url, headers=headers, json=payload)
    return resp.json()


def print_result(result: dict, operation: str):
    """Sonucu kullanıcıya göster."""
    print(f"\n{'='*50}")
    print(f"  {operation} Sonucu")
    print(f"{'='*50}")

    if result.get("success"):
        print(f"  Durum: BAŞARILI ✓")
        print(f"  Mesaj: {result.get('status_message', '-')}")
        print(f"  Transaction ID: {result.get('transaction_id', '-')}")
        print(f"  Onay Kodu: {result.get('approval_code', '-')}")
        print(f"  Onay Mesajı: {result.get('approval_message', '-')}")
    else:
        print(f"  Durum: BAŞARISIZ ✗")
        print(f"  Hata Kodu: {result.get('response_code', '-')}")
        print(f"  Mesaj: {result.get('status_message', '-')}")
        errors = result.get("errors", {})
        if errors:
            print(f"  Hatalar:")
            for code, messages in errors.items():
                for msg in messages:
                    print(f"    [{code}] {msg}")

    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description="PayTrace Refund & Void Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Tam refund (settle olmuş işlem):
  python paytrace_refund.py -u USER -p PASS -t 12345 -i INTEGRATOR_ID

  # Kısmi refund (örn: 10.50$):
  python paytrace_refund.py -u USER -p PASS -t 12345 -i INTEGRATOR_ID --amount 10.50

  # Void (henüz settle olmamış işlem):
  python paytrace_refund.py -u USER -p PASS -t 12345 -i INTEGRATOR_ID --void

  # Sandbox ortamında test:
  python paytrace_refund.py -u USER -p PASS -t 12345 -i INTEGRATOR_ID --sandbox

  # İşlem detayını görüntüle:
  python paytrace_refund.py -u USER -p PASS -t 12345 -i INTEGRATOR_ID --info
        """,
    )

    parser.add_argument("-u", "--username", required=True, help="PayTrace API kullanıcı adı")
    parser.add_argument("-p", "--password", required=True, help="PayTrace API şifresi")
    parser.add_argument("-t", "--transaction-id", type=int, required=True, help="İade edilecek Transaction ID")
    parser.add_argument("-i", "--integrator-id", required=True, help="PayTrace Integrator ID")
    parser.add_argument("--amount", type=float, default=None, help="Kısmi iade tutarı (belirtilmezse tam iade yapılır)")
    parser.add_argument("--void", action="store_true", help="Refund yerine void (iptal) yap (settle olmamış işlemler için)")
    parser.add_argument("--sandbox", action="store_true", help="Sandbox ortamını kullan (test)")
    parser.add_argument("--info", action="store_true", help="İşlem detaylarını göster (refund/void yapmadan)")

    args = parser.parse_args()

    base_url = SANDBOX_URL if args.sandbox else BASE_URL

    print(f"\n[*] PayTrace'e bağlanılıyor... ({'Sandbox' if args.sandbox else 'Production'})")
    access_token = get_access_token(base_url, args.username, args.password)
    print(f"[✓] Giriş başarılı, token alındı.")

    if args.info:
        print(f"\n[*] Transaction #{args.transaction_id} bilgileri getiriliyor...")
        result = export_transaction(base_url, access_token, args.transaction_id, args.integrator_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.void:
        print(f"\n[*] Transaction #{args.transaction_id} VOID (iptal) ediliyor...")
        result = void_transaction(base_url, access_token, args.transaction_id, args.integrator_id)
        print_result(result, "VOID (İptal)")

        if not result.get("success"):
            response_code = result.get("response_code")
            if response_code == 818 or "settled" in str(result.get("status_message", "")).lower():
                print("[!] İşlem zaten settle olmuş, void yapılamıyor.")
                print("[!] Bunun yerine refund deneyin (--void parametresini kaldırın).")
    else:
        amount_str = f" (Tutar: ${args.amount})" if args.amount else " (Tam iade)"
        print(f"\n[*] Transaction #{args.transaction_id} REFUND yapılıyor...{amount_str}")
        result = refund_by_transaction_id(
            base_url, access_token, args.transaction_id, args.integrator_id, args.amount
        )
        print_result(result, "REFUND (İade)")

        if not result.get("success"):
            response_code = result.get("response_code")
            status_msg = str(result.get("status_message", "")).lower()
            errors = result.get("errors", {})
            error_817 = "817" in errors or response_code == 817

            if error_817 or "not settled" in status_msg or "unsettled" in status_msg:
                print("[!] İşlem henüz settle olmamış, refund yapılamıyor.")
                print("[!] Bunun yerine void deneyin (--void parametresini ekleyin).")


if __name__ == "__main__":
    main()
