#!/usr/bin/env python3
"""
TSYS-routed gateway single-card test utility (sandbox-first).

This script targets common `.../api/transact.php` style gateways
(for example NMI/Valor-style integrations that can be processor-routed to TSYS).

IMPORTANT:
- Use TEST credentials and TEST cards only.
- Do NOT use this script for storing/handling real card data in production.
- For production, use tokenization/hosted fields and PCI-compliant flows.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Dict


DEFAULT_ENDPOINT = "https://secure.nmi.com/api/transact.php"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a single test SALE against a TSYS-routed gateway endpoint."
    )
    parser.add_argument(
        "--endpoint",
        default=os.getenv("GATEWAY_ENDPOINT", DEFAULT_ENDPOINT),
        help="Gateway POST endpoint (default: %(default)s)",
    )
    parser.add_argument(
        "--amount",
        default="1.00",
        help='Transaction amount as decimal string (default: "1.00")',
    )
    parser.add_argument(
        "--card-number",
        default=os.getenv("TEST_CARD_NUMBER", "4111111111111111"),
        help="Test card number (default: 4111111111111111)",
    )
    parser.add_argument(
        "--exp",
        default=os.getenv("TEST_CARD_EXP", "1227"),
        help="Card expiration MMYY (default: 1227)",
    )
    parser.add_argument(
        "--cvv",
        default=os.getenv("TEST_CARD_CVV", "123"),
        help="Card CVV (default: 123)",
    )
    parser.add_argument(
        "--orderid",
        default=os.getenv("TEST_ORDER_ID", "TSYS-TEST-001"),
        help="Order ID/reference (default: TSYS-TEST-001)",
    )
    parser.add_argument(
        "--security-key",
        default=os.getenv("GATEWAY_SECURITY_KEY"),
        help="Preferred auth method (security_key)",
    )
    parser.add_argument(
        "--username",
        default=os.getenv("GATEWAY_USERNAME"),
        help="Fallback auth method: gateway username",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("GATEWAY_PASSWORD"),
        help="Fallback auth method: gateway password",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Send as live transaction (default is test mode).",
    )
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> Dict[str, str]:
    payload: Dict[str, str] = {
        "type": "sale",
        "amount": args.amount,
        "ccnumber": args.card_number,
        "ccexp": args.exp,
        "cvv": args.cvv,
        "orderid": args.orderid,
    }

    # Keep default as test-mode for safety.
    if not args.live:
        payload["test_mode"] = "enabled"

    # Auth priority: security_key, else username/password.
    if args.security_key:
        payload["security_key"] = args.security_key
    elif args.username and args.password:
        payload["username"] = args.username
        payload["password"] = args.password
    else:
        raise ValueError(
            "Authentication missing. Provide --security-key OR both --username and --password."
        )

    return payload


def post_form(endpoint: str, payload: Dict[str, str]) -> Dict[str, str]:
    encoded = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")

    # Typical response format is querystring-like:
    # response=1&responsetext=Approved&response_code=100&...
    parsed = urllib.parse.parse_qs(body, keep_blank_values=True)
    normalized = {k: v[0] if isinstance(v, list) and v else "" for k, v in parsed.items()}
    normalized["_raw"] = body
    return normalized


def evaluate(result: Dict[str, str]) -> bool:
    response = result.get("response", "")
    response_code = result.get("response_code", "")
    text = result.get("responsetext", "") or result.get("response_message", "")

    approved = response == "1" and response_code in {"100", "00", "0", ""}
    if approved:
        print("APPROVED")
    else:
        print("NOT APPROVED")

    print(f"response={response!r} response_code={response_code!r} message={text!r}")
    return approved


def main() -> int:
    args = parse_args()
    try:
        payload = build_payload(args)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"POST {args.endpoint}")
    print("Request summary:")
    safe_view = {
        **payload,
        "ccnumber": f"****{payload['ccnumber'][-4:]}",
        "cvv": "***",
    }
    print(json.dumps(safe_view, indent=2))

    try:
        result = post_form(args.endpoint, payload)
    except Exception as exc:
        print(f"REQUEST FAILED: {exc}", file=sys.stderr)
        return 1

    print("\nGateway raw response:")
    print(result.get("_raw", ""))
    print("\nParsed response:")
    print(json.dumps({k: v for k, v in result.items() if k != "_raw"}, indent=2))

    return 0 if evaluate(result) else 3


if __name__ == "__main__":
    raise SystemExit(main())

