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

`index.php` now supports two TSYS gateway profiles:

1. `transnox` (default, `/servlets/TransNox_API_Server`)
2. `rest` (`/transactions/*` style API)

- Sandbox base URL: `TSYS_SANDBOX_URL`
- Production base URL: `TSYS_PRODUCTION_URL`
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

### Recommended for your account (TransNox)

```bash
export TSYS_GATEWAY_PROFILE="transnox"
export TSYS_SANDBOX_URL="https://stagegw.transnox.com/servlets/TransNox_API_Server"
export TSYS_PRODUCTION_URL="https://gw.transnox.com/servlets/TransNox_API_Server"
export TSYS_DEVICE_ID="7000"
export TSYS_TRANSACTION_KEY="your_transnox_transaction_key"
export TSYS_DEVELOPER_ID="your_transnox_developer_id"
export TSYS_TRANSNOX_AMOUNT_MINOR="1"
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

#### TransNox profile (default)

**Charge**
```json
{
  "Sale": {
    "deviceID": "7000",
    "transaction_key": "xxx",
    "card_data_source": "INTERNET",
    "transaction_amount": "10000",
    "currency_code": "USD",
    "card_number": "4111111111111111",
    "expiration_date": "12/28",
    "cvv2": "123",
    "terminal_capability": "ICC_CHIP_READ_ONLY",
    "terminal_operating_environment": "ON_MERCHANT_PREMISES_ATTENDED",
    "cardholder_authentication_method": "NOT_AUTHENTICATED",
    "developerID": "xxx",
    "order_number": "INV-1001"
  }
}
```

**Auth**
```json
{
  "Auth": {
    "deviceID": "7000",
    "transaction_key": "xxx",
    "card_data_source": "INTERNET",
    "transaction_amount": "10000",
    "currency_code": "USD",
    "card_number": "4111111111111111",
    "expiration_date": "12/28",
    "cvv2": "123",
    "terminal_capability": "ICC_CHIP_READ_ONLY",
    "terminal_operating_environment": "ON_MERCHANT_PREMISES_ATTENDED",
    "cardholder_authentication_method": "NOT_AUTHENTICATED",
    "developerID": "xxx",
    "order_number": "INV-1001"
  }
}
```

**Void**
```json
{
  "Void": {
    "deviceID": "7000",
    "transaction_key": "xxx",
    "transactionID": "1234567890",
    "developerID": "xxx"
  }
}
```

**Return**
```json
{
  "Return": {
    "deviceID": "7000",
    "transaction_key": "xxx",
    "transaction_amount": "10000",
    "transactionID": "1234567890"
  }
}
```

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
