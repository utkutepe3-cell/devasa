# TSYS Virtual Terminal (PHP)

Modernized virtual terminal with Charge/Auth/Void/Return flows and TSYS gateway integration.

## Run

```bash
php -S 127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/index.php
```

## TSYS Integration

`index.php` now sends transactions to TSYS Payment Gateway with endpoint + auth format below:

- Sandbox base URL: `TSYS_SANDBOX_URL` (example: `https://api.sandbox.tsys.com/v1`)
- Production base URL: `TSYS_PRODUCTION_URL` (example: `https://api.tsys.com/v1`)
- Auth header:
  - default: `X-TSYS-API-Key: <key>` (`TSYS_AUTH_MODE=x-tsys-api-key`)
  - optional: `Authorization: Bearer <key>` (`TSYS_AUTH_MODE=bearer`)
  - optional basic auth: `TSYS_API_USERNAME` + `TSYS_API_PASSWORD`

### Required Environment Variables (real gateway)

```bash
export TSYS_SANDBOX_URL="https://api.sandbox.tsys.com/v1"
export TSYS_PRODUCTION_URL="https://api.tsys.com/v1"
export TSYS_API_KEY="your_api_key_if_used"
export TSYS_AUTH_MODE="x-tsys-api-key"
export TSYS_API_USERNAME="your_gateway_username"
export TSYS_API_PASSWORD="your_gateway_password"
export TSYS_ENABLE_MOCK="0"
```

> `TSYS_ENABLE_MOCK=1` enables local mock mode (no external TSYS call).

### Merchant profile mapped in payload

The backend payload includes these merchant profile fields (default values can be overridden with env vars):

- DBA: Get Your Life Back LLC (`TSYS_DBA_NAME`)
- Address: 28 Tindall Rd, Middletown, New Jersey 07748
- Customer service: +1 800-993-0929
- Merchant number: 401151759710
- V Number: V6298237
- MCC: 5499
- BIN: 494306
- Chain: 031776
- Agent Bank: 031776
- Store Number: 0001
- Terminal Number: 7000
- Location Number: 00001

### Exact request bodies (implemented)

#### Charge (Sale)
- `POST /transactions/sale`
```json
{
  "merchantId": "401151759710",
  "amount": 100.0,
  "currency": "USD",
  "orderId": "INV-1001",
  "description": "TSYS Virtual Terminal CHARGE",
  "card": {
    "cardNumber": "4111111111111111",
    "expirationDate": "1228",
    "cvv": "123",
    "billingAddress": {
      "zip": "07748",
      "street": "28 Tindall Rd"
    }
  },
  "captureImmediately": true
}
```

#### Auth
- `POST /transactions/authorize`
```json
{
  "merchantId": "401151759710",
  "amount": 100.0,
  "currency": "USD",
  "orderId": "INV-1001",
  "description": "TSYS Virtual Terminal AUTH",
  "card": {
    "cardNumber": "4111111111111111",
    "expirationDate": "1228",
    "cvv": "123",
    "billingAddress": {
      "zip": "07748",
      "street": "28 Tindall Rd"
    }
  }
}
```

#### Void
- `POST /transactions/{transactionId}/void`
- body: `{}`

#### Return (Refund)
- `POST /transactions/{transactionId}/refund`
```json
{
  "amount": 100.0,
  "reason": "customer_request"
}
```

## Notes

- Card brands, ACH/EBT/gift capabilities are acquiring-side configurations on TSYS, not UI-only flags.
- Use TSYS-approved PCI flow in production and do not store raw PAN/CVV in logs or databases.
