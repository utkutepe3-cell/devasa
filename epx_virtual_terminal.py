#!/usr/bin/env python3
"""
EPX Virtual Terminal helper (template).

This script is a safe starter template for legitimate merchant usage.
You must replace endpoint/payload fields according to your EPX API docs.

Required env vars:
  EPX_BASE_URL, MERCH_NBR, DBA_NBR, CUST_NBR, TERMINAL_NBR
Optional env var:
  EPX_API_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

import requests


@dataclass
class EpxConfig:
    base_url: str
    api_key: str
    merch_nbr: str
    dba_nbr: str
    cust_nbr: str
    terminal_nbr: str
    timeout_seconds: int = 30
    dry_run: bool = True


def load_config(dry_run: bool) -> EpxConfig:
    base_url = os.getenv("EPX_BASE_URL", "").strip()
    api_key = os.getenv("EPX_API_KEY", "").strip()
    merch_nbr = os.getenv("MERCH_NBR", "").strip()
    dba_nbr = os.getenv("DBA_NBR", "").strip()
    cust_nbr = os.getenv("CUST_NBR", "").strip()
    terminal_nbr = os.getenv("TERMINAL_NBR", "").strip()

    missing = [
        name
        for name, value in (
            ("EPX_BASE_URL", base_url),
            ("MERCH_NBR", merch_nbr),
            ("DBA_NBR", dba_nbr),
            ("CUST_NBR", cust_nbr),
            ("TERMINAL_NBR", terminal_nbr),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return EpxConfig(
        base_url=base_url.rstrip("/"),
        api_key=api_key,
        merch_nbr=merch_nbr,
        dba_nbr=dba_nbr,
        cust_nbr=cust_nbr,
        terminal_nbr=terminal_nbr,
        dry_run=dry_run,
    )


def parse_amount(raw: str) -> str:
    try:
        amount = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount: {raw}") from exc
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return f"{amount:.2f}"


def build_headers(config: EpxConfig) -> Dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    return headers


def build_epx_identifiers(config: EpxConfig) -> Dict[str, str]:
    return {
        "merch_nbr": config.merch_nbr,
        "dba_nbr": config.dba_nbr,
        "cust_nbr": config.cust_nbr,
        "terminal_nbr": config.terminal_nbr,
    }


def post_transaction(config: EpxConfig, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{config.base_url}/transactions"
    if config.dry_run:
        return {
            "dry_run": True,
            "url": url,
            "payload": payload,
        }

    response = requests.post(
        url,
        headers=build_headers(config),
        json=payload,
        timeout=config.timeout_seconds,
    )
    response.raise_for_status()
    return response.json()


def build_sale_payload(args: argparse.Namespace, config: EpxConfig) -> Dict[str, Any]:
    # Replace with exact EPX sale schema from your account documentation.
    return {
        **build_epx_identifiers(config),
        "type": "sale",
        "amount": parse_amount(args.amount),
        "currency": args.currency,
        "card": {
            "number": args.card_number,
            "exp_month": args.exp_month,
            "exp_year": args.exp_year,
            "cvv": args.cvv,
        },
        "billing": {
            "name": args.name,
            "zip": args.zip_code,
        },
        "reference": args.reference,
    }


def build_refund_payload(args: argparse.Namespace, config: EpxConfig) -> Dict[str, Any]:
    # Replace with exact EPX refund/open-credit schema from your processor setup.
    payload: Dict[str, Any] = {
        **build_epx_identifiers(config),
        "type": "refund",
        "amount": parse_amount(args.amount),
        "reference": args.reference,
    }
    if args.original_txn_id:
        payload["original_txn_id"] = args.original_txn_id
    return payload


def add_common(parent: argparse.ArgumentParser) -> None:
    parent.add_argument("--amount", required=True, help="Transaction amount (e.g. 12.50)")
    parent.add_argument("--currency", default="USD", help="ISO currency code (default: USD)")
    parent.add_argument("--reference", default="", help="Internal order/reference ID")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EPX Virtual Terminal template client")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually send request. Default is dry-run.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sale = sub.add_parser("sale", help="Create a sale transaction")
    add_common(sale)
    sale.add_argument("--card-number", required=True)
    sale.add_argument("--exp-month", required=True)
    sale.add_argument("--exp-year", required=True)
    sale.add_argument("--cvv", required=True)
    sale.add_argument("--name", required=True, help="Cardholder full name")
    sale.add_argument("--zip-code", required=True)

    refund = sub.add_parser("refund", help="Create a refund transaction")
    add_common(refund)
    refund.add_argument(
        "--original-txn-id",
        default="",
        help="Original transaction ID for linked refunds",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = load_config(dry_run=not args.execute)
        if args.command == "sale":
            payload = build_sale_payload(args, config)
        elif args.command == "refund":
            payload = build_refund_payload(args, config)
        else:
            parser.error("Unsupported command")
            return 2

        result = post_transaction(config, payload)
        print(json.dumps(result, indent=2))
        return 0
    except requests.HTTPError as exc:
        response_text = exc.response.text if exc.response is not None else str(exc)
        print(f"HTTP error: {response_text}", file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
