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

`index.php` now sends transactions to TSYS through cURL with environment switch support:

- Sandbox endpoint: `TSYS_SANDBOX_URL`
- Production endpoint: `TSYS_PRODUCTION_URL`
- Auth: `TSYS_API_KEY` and/or `TSYS_API_USERNAME` + `TSYS_API_PASSWORD`

### Required Environment Variables (real gateway)

```bash
export TSYS_SANDBOX_URL="https://stagegw.transnox.com/servlets/transnox_api_server"
export TSYS_PRODUCTION_URL="https://gw.transnox.com/servlets/transnox_api_server"
export TSYS_API_KEY="your_api_key_if_used"
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

## Notes

- Card brands, ACH/EBT/gift capabilities are acquiring-side configurations on TSYS, not UI-only flags.
- Use TSYS-approved PCI flow in production and do not store raw PAN/CVV in logs or databases.
