#!/usr/bin/env python3
"""
PayTrace Refund Tool - Sale Bölümünden Refund
Satışları listeler ve doğrudan refund yapmanızı sağlar.

Kullanım:
    # Satışları listele ve interaktif refund yap:
    python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID --list-sales

    # Direkt transaction ID ile refund:
    python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID -t 12345

    # Kısmi refund:
    python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID -t 12345 --amount 10.50
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

import requests


BASE_URL = "https://api.paytrace.com"
SANDBOX_URL = "https://api.sandbox.paytrace.com"


class PayTraceClient:
    def __init__(self, base_url: str, username: str, password: str, integrator_id: str):
        self.base_url = base_url
        self.integrator_id = integrator_id
        self.access_token = self._authenticate(username, password)

    def _authenticate(self, username: str, password: str) -> str:
        url = f"{self.base_url}/oauth/token"
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
            try:
                error_data = resp.json()
                error_msg = error_data.get("error_description", resp.text)
            except Exception:
                error_msg = resp.text
            print(f"\n[HATA] Giris basarisiz (HTTP {resp.status_code}): {error_msg}")
            sys.exit(1)

        return resp.json()["access_token"]

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    def list_sales(self, start_date: str, end_date: str, transaction_type: str = "SALE") -> list:
        """Belirli tarih aralığındaki satışları listele."""
        url = f"{self.base_url}/v1/transactions/export/by_date_range"
        payload = {
            "start_date": start_date,
            "end_date": end_date,
            "transaction_type": transaction_type,
            "integrator_id": self.integrator_id,
        }

        resp = requests.post(url, headers=self._headers(), json=payload)
        result = resp.json()

        if result.get("success"):
            return result.get("transactions", [])
        return []

    def get_transaction(self, transaction_id: int) -> dict:
        """Tek bir işlemin detayını getir."""
        url = f"{self.base_url}/v1/transactions/export/by_id"
        payload = {
            "transaction_id": transaction_id,
            "integrator_id": self.integrator_id,
        }

        resp = requests.post(url, headers=self._headers(), json=payload)
        result = resp.json()

        if result.get("success"):
            transactions = result.get("transactions", [])
            if transactions:
                return transactions[0]
        return {}

    def refund(self, transaction_id: int, amount: float = None) -> dict:
        """Transaction ID ile refund yap (sale bölümünden refund)."""
        url = f"{self.base_url}/v1/transactions/refund/for_transaction"
        payload = {
            "transaction_id": transaction_id,
            "integrator_id": self.integrator_id,
        }
        if amount is not None:
            payload["amount"] = amount

        resp = requests.post(url, headers=self._headers(), json=payload)
        return resp.json()

    def void(self, transaction_id: int) -> dict:
        """Transaction void (iptal) yap."""
        url = f"{self.base_url}/v1/transactions/void"
        payload = {
            "transaction_id": transaction_id,
            "integrator_id": self.integrator_id,
        }

        resp = requests.post(url, headers=self._headers(), json=payload)
        return resp.json()


def print_sales_table(transactions: list):
    """Satışları tablo formatında göster."""
    if not transactions:
        print("\n  Belirtilen tarih aralığında satış bulunamadı.")
        return

    print(f"\n{'='*90}")
    print(f"  {'No':<4} {'Transaction ID':<16} {'Tarih':<20} {'Tutar':<12} {'Kart':<20} {'Durum':<12}")
    print(f"{'='*90}")

    for idx, tx in enumerate(transactions, 1):
        tx_id = tx.get("transaction_id", "-")
        created = tx.get("created", {})
        date = created.get("at", "-") if isinstance(created, dict) else "-"
        amount = tx.get("amount", "-")
        card = tx.get("credit_card", {})
        masked = card.get("masked_number", "-") if isinstance(card, dict) else "-"
        status = tx.get("status_message", "-")

        if isinstance(amount, (int, float)):
            amount_str = f"${amount:.2f}"
        else:
            amount_str = str(amount)

        print(f"  {idx:<4} {tx_id:<16} {str(date):<20} {amount_str:<12} {masked:<20} {str(status)[:12]:<12}")

    print(f"{'='*90}")
    print(f"  Toplam: {len(transactions)} satış")
    print()


def print_result(result: dict, operation: str):
    """Sonucu göster."""
    print(f"\n{'='*50}")
    print(f"  {operation} Sonucu")
    print(f"{'='*50}")

    if result.get("success"):
        print(f"  Durum      : BASARILI")
        print(f"  Mesaj      : {result.get('status_message', '-')}")
        print(f"  Yeni Tx ID : {result.get('transaction_id', '-')}")
        print(f"  Onay Kodu  : {result.get('approval_code', '-')}")
        print(f"  Onay Mesaji: {result.get('approval_message', '-')}")
    else:
        print(f"  Durum    : BASARISIZ")
        print(f"  Hata Kodu: {result.get('response_code', '-')}")
        print(f"  Mesaj    : {result.get('status_message', '-')}")
        errors = result.get("errors", {})
        if errors:
            print(f"  Hatalar:")
            for code, messages in errors.items():
                if isinstance(messages, list):
                    for msg in messages:
                        print(f"    [{code}] {msg}")
                else:
                    print(f"    [{code}] {messages}")

    print(f"{'='*50}\n")


def interactive_refund(client: PayTraceClient, days: int):
    """Satışları listele ve interaktif olarak refund yap."""
    end_date = datetime.now().strftime("%m/%d/%Y")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%m/%d/%Y")

    print(f"\n[*] Satislar getiriliyor ({start_date} - {end_date})...")
    sales = client.list_sales(start_date, end_date)
    print_sales_table(sales)

    if not sales:
        return

    while True:
        choice = input("Refund yapilacak islem numarasini girin (No) veya 'q' ile cikin: ").strip()
        if choice.lower() == 'q':
            break

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(sales):
                print("[!] Gecersiz numara. Tekrar deneyin.")
                continue
        except ValueError:
            print("[!] Lutfen bir sayi girin.")
            continue

        tx = sales[idx]
        tx_id = tx.get("transaction_id")
        original_amount = tx.get("amount", 0)

        print(f"\n  Secilen islem: #{tx_id} - ${original_amount}")
        amount_input = input(f"  Iade tutari (tam iade icin Enter): ").strip()

        amount = None
        if amount_input:
            try:
                amount = float(amount_input)
                if amount <= 0:
                    print("[!] Tutar pozitif olmali.")
                    continue
                if amount > float(original_amount):
                    print(f"[!] Tutar orijinal tutari (${original_amount}) asamaz.")
                    continue
            except ValueError:
                print("[!] Gecersiz tutar.")
                continue

        amount_str = f"${amount:.2f}" if amount else f"${original_amount} (tam iade)"
        confirm = input(f"  Transaction #{tx_id} icin {amount_str} iade onayliyor musunuz? (e/h): ").strip().lower()

        if confirm != 'e':
            print("  Iptal edildi.")
            continue

        print(f"\n[*] Refund isleniyor...")
        result = client.refund(int(tx_id), amount)
        print_result(result, "REFUND (Iade)")

        if not result.get("success"):
            response_code = result.get("response_code")
            if response_code == 817 or "817" in str(result.get("errors", {})):
                print("[!] Islem henuz settle olmamis. Void (iptal) denemek ister misiniz?")
                void_confirm = input("  Void yapmak icin 'e' girin: ").strip().lower()
                if void_confirm == 'e':
                    print(f"\n[*] Void isleniyor...")
                    void_result = client.void(int(tx_id))
                    print_result(void_result, "VOID (Iptal)")


def direct_refund(client: PayTraceClient, transaction_id: int, amount: float = None):
    """Direkt transaction ID ile refund."""
    print(f"\n[*] Transaction #{transaction_id} bilgileri getiriliyor...")
    tx = client.get_transaction(transaction_id)

    if tx:
        original_amount = tx.get("amount", "?")
        tx_type = tx.get("transaction_type", "?")
        card = tx.get("credit_card", {})
        masked = card.get("masked_number", "?") if isinstance(card, dict) else "?"
        print(f"  Islem Tipi : {tx_type}")
        print(f"  Tutar      : ${original_amount}")
        print(f"  Kart       : {masked}")
    else:
        print(f"  [!] Islem detayi alinamadi, yine de refund denenecek...")

    amount_str = f"${amount:.2f} (kismi iade)" if amount else "Tam iade"
    print(f"\n[*] REFUND yapiliyor... ({amount_str})")
    result = client.refund(transaction_id, amount)
    print_result(result, "REFUND (Iade)")

    if not result.get("success"):
        response_code = result.get("response_code")
        if response_code == 817 or "817" in str(result.get("errors", {})):
            print("[!] Islem henuz settle olmamis, refund yapilamadi.")
            print("[*] Otomatik olarak VOID deneniyor...")
            void_result = client.void(transaction_id)
            print_result(void_result, "VOID (Iptal)")


def main():
    parser = argparse.ArgumentParser(
        description="PayTrace Refund Tool - Sale Bolumunden Refund",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  # Satislari listele ve interaktif refund yap (son 30 gun):
  python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID --list-sales

  # Son 90 gundeki satislari listele:
  python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID --list-sales --days 90

  # Direkt transaction ID ile tam refund:
  python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID -t 12345

  # Kismi refund:
  python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID -t 12345 --amount 10.50

  # Void (settle olmamis islem icin):
  python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID -t 12345 --void

  # Sandbox ortaminda test:
  python paytrace_refund.py -u USER -p PASS -i INTEGRATOR_ID --list-sales --sandbox
        """,
    )

    parser.add_argument("-u", "--username", required=True, help="PayTrace API kullanici adi")
    parser.add_argument("-p", "--password", required=True, help="PayTrace API sifresi")
    parser.add_argument("-i", "--integrator-id", required=True, help="PayTrace Integrator ID")
    parser.add_argument("-t", "--transaction-id", type=int, help="Refund yapilacak Transaction ID")
    parser.add_argument("--amount", type=float, default=None, help="Kismi iade tutari (belirtilmezse tam iade)")
    parser.add_argument("--void", action="store_true", help="Refund yerine void yap")
    parser.add_argument("--list-sales", action="store_true", help="Satislari listele ve sec")
    parser.add_argument("--days", type=int, default=30, help="Kac gunluk satis getirilsin (varsayilan: 30)")
    parser.add_argument("--sandbox", action="store_true", help="Sandbox ortamini kullan (test)")

    args = parser.parse_args()

    if not args.transaction_id and not args.list_sales:
        parser.error("--transaction-id (-t) veya --list-sales parametresinden birini belirtmelisiniz.")

    base_url = SANDBOX_URL if args.sandbox else BASE_URL
    env_name = "SANDBOX" if args.sandbox else "PRODUCTION"

    print(f"\n[*] PayTrace'e baglaniliyor... ({env_name})")
    client = PayTraceClient(base_url, args.username, args.password, args.integrator_id)
    print(f"[+] Giris basarili!")

    if args.list_sales:
        interactive_refund(client, args.days)
    elif args.void:
        print(f"\n[*] Transaction #{args.transaction_id} VOID ediliyor...")
        result = client.void(args.transaction_id)
        print_result(result, "VOID (Iptal)")
        if not result.get("success"):
            if result.get("response_code") == 818 or "818" in str(result.get("errors", {})):
                print("[!] Islem zaten settle olmus, void yapilamiyor.")
                print("[!] Refund deneyin (--void parametresini kaldirin).")
    else:
        direct_refund(client, args.transaction_id, args.amount)


if __name__ == "__main__":
    main()
