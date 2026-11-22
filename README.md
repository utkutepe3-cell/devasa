# CornerPay Virtual Terminal — Blind Unmatched Credit

Sandbox virtual terminal inspired by **PayTrace** and **Datacap portal.dcap**, branded for **CornerPay.NET**.

Supports **blind unmatched credit**: issue a standalone credit to a card **without** an original sale / RefNo (also called unmatched refund, open credit, or independent credit).

Tabs: **Payment · Blind Credit · Recurring · Gift · Reports · Configure**

## Blind unmatched credit

| Path | What it does |
|------|----------------|
| **Blind Credit** tab | Dedicated unmatched credit flow with reason codes + auth checkbox |
| **Payment → Transaction Type → Blind Unmatched Credit** | Same capability from the one-time payment form |
| **Configure → Allow blind unmatched credit** | Merchant entitlement toggle (on by default in this sandbox) |

Gateway profile helpers live in `src/lib/gateway.ts` (`supports_blind_unmatched_credit: true`).

## Run

```bash
npm install
npm run dev
```

1. Sign in with any username/password (sandbox — nothing is sent remotely)
2. **Configure** → merchant secret + name → keep **Allow blind unmatched credit** checked → Save
3. **Blind Credit** → amount + card `4111111111111111` → confirm → Process

Demo only — not the live [CornerPay portal](https://cornerstonemerchant.com/cornerpay/) or a live PayTrace / Datacap connection.
