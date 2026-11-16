# CornerPay Virtual Terminal

Sandbox virtual terminal inspired by Datacap’s VT layout, branded for **CornerPay.NET** (Cornerstone Merchant Services).

Tabs: **Payment · Recurring · Gift · Reports · Configure**

Also supports demo **ACH** sales on the Payment tab.

## Run

```bash
npm install
npm run dev
```

1. Enter any username/password on the sandbox login (nothing is sent remotely)
2. Configure → merchant secret + name → Save
3. Payment → process a test card (`4111111111111111`)

Demo only — not the live [CornerPay portal](https://cornerstonemerchant.com/cornerpay/).
