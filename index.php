<?php
declare(strict_types=1);

function jsonResponse(array $payload, int $statusCode = 200): void
{
    http_response_code($statusCode);
    header('Content-Type: application/json; charset=UTF-8');
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    exit;
}

function envString(string $key, string $default = ''): string
{
    $value = getenv($key);
    return is_string($value) && $value !== '' ? $value : $default;
}

function normalizeDigits(string $value): string
{
    return preg_replace('/\D+/', '', $value) ?? '';
}

function maskCard(string $cardNumber): string
{
    $digits = normalizeDigits($cardNumber);
    if (strlen($digits) < 10) {
        return '****';
    }
    return substr($digits, 0, 6) . str_repeat('*', max(0, strlen($digits) - 10)) . substr($digits, -4);
}

function isValidLuhn(string $cardNumber): bool
{
    $digits = normalizeDigits($cardNumber);
    if ($digits === '' || strlen($digits) < 12 || strlen($digits) > 19) {
        return false;
    }
    $sum = 0;
    $alt = false;
    for ($i = strlen($digits) - 1; $i >= 0; $i--) {
        $n = (int) $digits[$i];
        if ($alt) {
            $n *= 2;
            if ($n > 9) {
                $n -= 9;
            }
        }
        $sum += $n;
        $alt = !$alt;
    }
    return $sum % 10 === 0;
}

function parseExpiry(string $expiryRaw): ?array
{
    $digits = normalizeDigits($expiryRaw);
    if (strlen($digits) === 3) {
        $digits = '0' . $digits;
    }
    if (strlen($digits) !== 4) {
        return null;
    }
    $month = (int) substr($digits, 0, 2);
    $year = (int) substr($digits, 2, 2);
    if ($month < 1 || $month > 12) {
        return null;
    }
    $fullYear = 2000 + $year;
    $expDate = DateTimeImmutable::createFromFormat('Y-n-j H:i:s', $fullYear . '-' . $month . '-1 00:00:00');
    if (!$expDate) {
        return null;
    }
    if ($expDate->modify('last day of this month')->setTime(23, 59, 59) < new DateTimeImmutable('now')) {
        return null;
    }
    return ['month' => str_pad((string) $month, 2, '0', STR_PAD_LEFT), 'year' => (string) $fullYear];
}

function getGatewayConfig(): array
{
    return [
        'sandbox_url' => rtrim(envString('TSYS_SANDBOX_URL', 'https://stagegw.transnox.com/servlets/TransNox_API_Server'), '/'),
        'production_url' => rtrim(envString('TSYS_PRODUCTION_URL', 'https://gw.transnox.com/servlets/TransNox_API_Server'), '/'),
        'gateway_profile' => strtolower(envString('TSYS_GATEWAY_PROFILE', 'transnox')),
        'api_key' => envString('TSYS_API_KEY'),
        'username' => envString('TSYS_API_USERNAME'),
        'password' => envString('TSYS_API_PASSWORD'),
        'auth_mode' => strtolower(envString('TSYS_AUTH_MODE', 'x-tsys-api-key')),
        'user_agent' => envString('TSYS_USER_AGENT', 'TSYSVirtualTerminal/1.0'),
        'device_id' => envString('TSYS_DEVICE_ID', envString('TSYS_TERMINAL_NUMBER', '7000')),
        'transaction_key' => envString('TSYS_TRANSACTION_KEY'),
        'developer_id' => envString('TSYS_DEVELOPER_ID'),
        'transnox_amount_minor' => envString('TSYS_TRANSNOX_AMOUNT_MINOR', '1') === '1',
        'timeout_seconds' => (int) envString('TSYS_TIMEOUT_SECONDS', '45'),
        'enable_mock' => envString('TSYS_ENABLE_MOCK', '0') === '1',
        'merchant' => [
            'dba' => envString('TSYS_DBA_NAME', 'Get Your Life Back LLC'),
            'streetAddress' => envString('TSYS_STREET_ADDRESS', '28 Tindall Rd'),
            'city' => envString('TSYS_CITY', 'Middletown'),
            'state' => envString('TSYS_STATE', 'New Jersey'),
            'zip' => envString('TSYS_ZIP', '07748'),
            'customerServicePhone' => envString('TSYS_CUSTOMER_SERVICE_PHONE', '+1 800-993-0929'),
            'merchantNumber' => envString('TSYS_MERCHANT_NUMBER', '401151759710'),
            'vNumber' => envString('TSYS_V_NUMBER', 'V6298237'),
            'mcc' => envString('TSYS_MCC', '5499'),
            'bin' => envString('TSYS_BIN', '494306'),
            'chain' => envString('TSYS_CHAIN', '031776'),
            'agentBank' => envString('TSYS_AGENT_BANK', '031776'),
            'storeNumber' => envString('TSYS_STORE_NUMBER', '0001'),
            'terminalNumber' => envString('TSYS_TERMINAL_NUMBER', '7000'),
            'locationNumber' => envString('TSYS_LOCATION_NUMBER', '00001'),
        ],
    ];
}

function getInputPayload(): array
{
    $rawInput = file_get_contents('php://input') ?: '';
    $contentType = $_SERVER['CONTENT_TYPE'] ?? '';
    if (str_contains(strtolower($contentType), 'application/json')) {
        $decoded = json_decode($rawInput, true);
        return is_array($decoded) ? $decoded : [];
    }
    $payload = $_POST;
    if (!$payload && $rawInput !== '') {
        parse_str($rawInput, $payload);
    }
    return is_array($payload) ? $payload : [];
}

function removeNullAndEmpty(array $input): array
{
    $output = [];
    foreach ($input as $key => $value) {
        if (is_array($value)) {
            $nested = removeNullAndEmpty($value);
            if ($nested !== []) {
                $output[$key] = $nested;
            }
            continue;
        }
        if ($value === null) {
            continue;
        }
        if (is_string($value) && trim($value) === '') {
            continue;
        }
        $output[$key] = $value;
    }
    return $output;
}

function validatePayload(array $payload): array
{
    $txType = strtolower(trim((string) ($payload['txType'] ?? 'charge')));
    $allowedTxTypes = ['charge', 'auth', 'void', 'return'];
    if (!in_array($txType, $allowedTxTypes, true)) {
        return ['_global' => 'Geçersiz işlem tipi.'];
    }

    $cardNumber = trim((string) ($payload['cardNumber'] ?? ''));
    $expiry = trim((string) ($payload['expiry'] ?? ''));
    $cvv = trim((string) ($payload['cvv'] ?? ''));
    $amountRaw = trim((string) ($payload['amount'] ?? ''));
    $referenceNo = trim((string) ($payload['referenceNo'] ?? ''));
    $errors = [];

    if (in_array($txType, ['charge', 'auth'], true)) {
        if (!isValidLuhn($cardNumber)) {
            $errors['cardNumber'] = 'Kart numarası geçerli görünmüyor.';
        }
        if (parseExpiry($expiry) === null) {
            $errors['expiry'] = 'Son kullanma tarihi MMYY formatında ve geçerli olmalı.';
        }
        if (!preg_match('/^\d{3,4}$/', normalizeDigits($cvv))) {
            $errors['cvv'] = 'CVV 3 veya 4 hane olmalı.';
        }
    }

    if (in_array($txType, ['charge', 'auth', 'return'], true)) {
        if ($amountRaw === '' || !is_numeric($amountRaw) || (float) $amountRaw <= 0) {
            $errors['amount'] = 'Tutar 0’dan büyük bir sayı olmalı.';
        }
    }

    if (in_array($txType, ['void', 'return'], true) && $referenceNo === '') {
        $errors['referenceNo'] = 'Void / Return için orijinal referans numarası zorunlu.';
    }

    return $errors;
}

function buildTsysRequest(string $txType, array $payload, array $config): array
{
    if (($config['gateway_profile'] ?? '') === 'transnox') {
        return buildTransnoxRequest($txType, $payload, $config);
    }
    return buildRestGatewayRequest($txType, $payload, $config);
}

function buildRestGatewayRequest(string $txType, array $payload, array $config): array
{
    $expiry = parseExpiry((string) ($payload['expiry'] ?? ''));
    $amount = trim((string) ($payload['amount'] ?? ''));
    $merchantId = $config['merchant']['merchantNumber'] ?? '';
    $invoice = trim((string) ($payload['invoice'] ?? ''));
    $referenceNo = trim((string) ($payload['referenceNo'] ?? ''));
    $formattedAmount = $amount !== '' ? (float) number_format((float) $amount, 2, '.', '') : null;

    $method = 'POST';
    $path = '/transactions/sale';
    $body = removeNullAndEmpty([
        'merchantId' => $merchantId,
        'amount' => $formattedAmount,
        'currency' => 'USD',
        'orderId' => $invoice,
        'description' => 'TSYS Virtual Terminal CHARGE',
        'card' => [
            'cardNumber' => normalizeDigits((string) ($payload['cardNumber'] ?? '')),
            'expirationDate' => $expiry ? ($expiry['month'] . substr($expiry['year'], -2)) : null,
            'cvv' => normalizeDigits((string) ($payload['cvv'] ?? '')),
            'billingAddress' => [
                'zip' => trim((string) ($payload['zipCode'] ?? '')),
                'street' => $config['merchant']['streetAddress'] ?? '',
            ],
        ],
        'captureImmediately' => true,
    ]);
    if ($txType === 'auth') {
        $path = '/transactions/authorize';
        $body = removeNullAndEmpty([
            'merchantId' => $merchantId,
            'amount' => $formattedAmount,
            'currency' => 'USD',
            'orderId' => $invoice,
            'description' => 'TSYS Virtual Terminal AUTH',
            'card' => [
                'cardNumber' => normalizeDigits((string) ($payload['cardNumber'] ?? '')),
                'expirationDate' => $expiry ? ($expiry['month'] . substr($expiry['year'], -2)) : null,
                'cvv' => normalizeDigits((string) ($payload['cvv'] ?? '')),
                'billingAddress' => [
                    'zip' => trim((string) ($payload['zipCode'] ?? '')),
                    'street' => $config['merchant']['streetAddress'] ?? '',
                ],
            ],
        ]);
    } elseif ($txType === 'void') {
        $path = '/transactions/' . rawurlencode($referenceNo) . '/void';
        $body = new stdClass();
    } elseif ($txType === 'return') {
        $path = '/transactions/' . rawurlencode($referenceNo) . '/refund';
        $body = removeNullAndEmpty([
            'amount' => $formattedAmount,
            'reason' => 'customer_request',
        ]);
    }

    return [
        'method' => $method,
        'path' => $path,
        'body' => $body,
        'txType' => $txType,
        'referenceNo' => $referenceNo,
        'merchant' => $config['merchant'],
        'meta' => [
            'source' => 'tsys-virtual-terminal-web',
            'requestedAt' => (new DateTimeImmutable())->format(DATE_ATOM),
        ],
    ];
}

function amountAsMinorUnit(string $amount): string
{
    return (string) (int) round(((float) $amount) * 100);
}

function buildTransnoxRequest(string $txType, array $payload, array $config): array
{
    $expiry = parseExpiry((string) ($payload['expiry'] ?? ''));
    $amountRaw = trim((string) ($payload['amount'] ?? '0'));
    $invoice = trim((string) ($payload['invoice'] ?? ''));
    $referenceNo = trim((string) ($payload['referenceNo'] ?? ''));
    $deviceId = (string) ($config['device_id'] ?? '');
    $transactionKey = (string) ($config['transaction_key'] ?? '');
    $developerId = (string) ($config['developer_id'] ?? '');
    $amountValue = ($config['transnox_amount_minor'] ?? true)
        ? amountAsMinorUnit($amountRaw)
        : number_format((float) $amountRaw, 2, '.', '');

    $base = removeNullAndEmpty([
        'deviceID' => $deviceId,
        'transaction_key' => $transactionKey,
    ]);

    $body = [];
    if ($txType === 'charge' || $txType === 'auth') {
        $saleOrAuth = array_merge($base, removeNullAndEmpty([
            'card_data_source' => 'INTERNET',
            'transaction_amount' => $amountValue,
            'currency_code' => 'USD',
            'card_number' => normalizeDigits((string) ($payload['cardNumber'] ?? '')),
            'expiration_date' => $expiry ? ($expiry['month'] . '/' . substr($expiry['year'], -2)) : null,
            'cvv2' => normalizeDigits((string) ($payload['cvv'] ?? '')),
            'terminal_capability' => 'ICC_CHIP_READ_ONLY',
            'terminal_operating_environment' => 'ON_MERCHANT_PREMISES_ATTENDED',
            'cardholder_authentication_method' => 'NOT_AUTHENTICATED',
            'developerID' => $developerId,
            'order_number' => $invoice !== '' ? $invoice : 'INV-' . (new DateTimeImmutable())->format('YmdHis'),
        ]));
        $body = $txType === 'charge' ? ['Sale' => $saleOrAuth] : ['Auth' => $saleOrAuth];
    } elseif ($txType === 'void') {
        $body = [
            'Void' => array_merge($base, removeNullAndEmpty([
                'transactionID' => $referenceNo,
                'developerID' => $developerId,
            ])),
        ];
    } elseif ($txType === 'return') {
        $body = [
            'Return' => array_merge($base, removeNullAndEmpty([
                'transaction_amount' => $amountValue,
                'transactionID' => $referenceNo,
            ])),
        ];
    }

    return [
        'method' => 'POST',
        'path' => '',
        'body' => $body,
        'txType' => $txType,
        'referenceNo' => $referenceNo,
        'merchant' => $config['merchant'],
        'meta' => [
            'source' => 'tsys-virtual-terminal-web',
            'requestedAt' => (new DateTimeImmutable())->format(DATE_ATOM),
            'profile' => 'transnox',
        ],
    ];
}

function callTsysGateway(string $environment, array $requestPayload, array $config): array
{
    $baseUrl = $environment === 'production' ? $config['production_url'] : $config['sandbox_url'];
    $path = (string) ($requestPayload['path'] ?? '');
    if ($baseUrl === '') {
        throw new RuntimeException('TSYS endpoint boş. TSYS_SANDBOX_URL / TSYS_PRODUCTION_URL tanımlayın.');
    }
    $isTransnox = ($config['gateway_profile'] ?? '') === 'transnox';
    if ($path === '' && !$isTransnox) {
        throw new RuntimeException('İstek path bilgisi boş.');
    }
    $url = $isTransnox ? $baseUrl : $baseUrl . $path;
    if (!function_exists('curl_init')) {
        throw new RuntimeException('PHP cURL extension bulunamadı.');
    }

    $headers = [
        'Content-Type: application/json',
        'Accept: application/json',
        'User-Agent: ' . $config['user_agent'],
    ];
    if ($config['api_key'] !== '' && in_array($config['auth_mode'], ['x-tsys-api-key', 'bearer'], true)) {
        $headers[] = $config['auth_mode'] === 'bearer'
            ? 'Authorization: Bearer ' . $config['api_key']
            : 'X-TSYS-API-Key: ' . $config['api_key'];
    }

    $curl = curl_init($url);
    if ($curl === false) {
        throw new RuntimeException('cURL başlatılamadı.');
    }

    curl_setopt_array($curl, [
        CURLOPT_CUSTOMREQUEST => strtoupper((string) ($requestPayload['method'] ?? 'POST')),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_POSTFIELDS => json_encode($requestPayload['body'] ?? new stdClass(), JSON_UNESCAPED_UNICODE),
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_TIMEOUT => max(15, (int) $config['timeout_seconds']),
    ]);

    if ($config['username'] !== '' || $config['password'] !== '') {
        curl_setopt($curl, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
        curl_setopt($curl, CURLOPT_USERPWD, $config['username'] . ':' . $config['password']);
    }

    $raw = curl_exec($curl);
    $errorNo = curl_errno($curl);
    $errorMessage = curl_error($curl);
    $statusCode = (int) curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);

    if ($raw === false || $errorNo !== 0) {
        throw new RuntimeException('Gateway bağlantı hatası: ' . $errorMessage);
    }
    if ($statusCode >= 400) {
        throw new RuntimeException('Gateway HTTP hatası: ' . $statusCode);
    }

    $decoded = json_decode($raw, true);
    if (is_array($decoded)) {
        return $decoded;
    }
    return ['rawResponse' => $raw];
}

function firstValue(array $source, array $keys): mixed
{
    foreach ($keys as $key) {
        if (array_key_exists($key, $source) && $source[$key] !== '' && $source[$key] !== null) {
            return $source[$key];
        }
    }
    return null;
}

function normalizeGatewayResponse(array $gatewayResponse, string $txType, array $requestPayload, string $environment): array
{
    if ((($requestPayload['meta']['profile'] ?? '') === 'transnox')) {
        return normalizeTransnoxResponse($gatewayResponse, $txType, $requestPayload, $environment);
    }

    $flat = $gatewayResponse;
    if (isset($gatewayResponse['transaction']) && is_array($gatewayResponse['transaction'])) {
        $flat = array_merge($flat, $gatewayResponse['transaction']);
    }

    $responseCode = (string) (firstValue($flat, ['responseCode', 'respCode', 'statusCode', 'code']) ?? 'UNKNOWN');
    $responseText = (string) (firstValue($flat, ['responseText', 'message', 'statusMessage', 'description']) ?? 'Unknown response');
    $approvedCodes = ['0', '00', '000', 'APPROVED', 'A'];
    $approved = in_array(strtoupper(trim($responseCode)), $approvedCodes, true)
        || str_contains(strtoupper($responseText), 'APPROV');

    return [
        'ok' => true,
        'transaction' => [
            'type' => strtoupper($txType),
            'status' => $approved ? 'approved' : 'declined',
            'responseCode' => $responseCode,
            'responseText' => $responseText,
            'authCode' => firstValue($flat, ['authCode', 'approvalCode', 'authorizationCode']),
            'referenceNo' => firstValue($flat, ['referenceNo', 'transactionId', 'retrievalReference', 'rrn']),
            'maskedCard' => maskCard((string) ($requestPayload['body']['card']['cardNumber'] ?? '')),
            'amount' => $requestPayload['body']['amount'] ?? null,
            'currency' => $requestPayload['body']['currency'] ?? 'USD',
            'invoice' => $requestPayload['body']['orderId'] ?? null,
            'zipCode' => $requestPayload['body']['card']['billingAddress']['zip'] ?? null,
            'originalReference' => $requestPayload['referenceNo'] ?? null,
            'avsResult' => firstValue($flat, ['avsResult', 'avsCode']),
            'cvvResult' => firstValue($flat, ['cvvResult', 'cvvCode']),
            'timestamp' => (new DateTimeImmutable())->format(DATE_ATOM),
            'mode' => $environment === 'production' ? 'PRODUCTION MODE' : 'TEST MODE (sandbox)',
            'host' => 'TSYS Gateway',
        ],
        'gatewayRaw' => $gatewayResponse,
    ];
}

function normalizeTransnoxResponse(array $gatewayResponse, string $txType, array $requestPayload, string $environment): array
{
    $responseNode = $gatewayResponse;
    foreach (['SaleResponse', 'AuthResponse', 'VoidResponse', 'ReturnResponse', 'SearchTransactionResponse'] as $key) {
        if (isset($gatewayResponse[$key]) && is_array($gatewayResponse[$key])) {
            $responseNode = $gatewayResponse[$key];
            break;
        }
    }

    $statusText = strtoupper((string) firstValue($responseNode, ['status', 'Status']));
    $responseCode = (string) (firstValue($responseNode, ['response_code', 'responseCode', 'Code']) ?? 'UNKNOWN');
    $responseMessage = (string) (firstValue($responseNode, ['response_message', 'responseMessage', 'Message']) ?? $statusText);
    $approved = $statusText === 'PASS' || str_starts_with($responseCode, 'A');

    return [
        'ok' => true,
        'transaction' => [
            'type' => strtoupper($txType),
            'status' => $approved ? 'approved' : 'declined',
            'responseCode' => $responseCode,
            'responseText' => $responseMessage !== '' ? $responseMessage : $statusText,
            'authCode' => firstValue($responseNode, ['approval_code', 'authCode']),
            'referenceNo' => firstValue($responseNode, ['transaction_id', 'transactionID', 'referenceNo']),
            'maskedCard' => maskCard((string) firstValue($requestPayload['body']['Sale'] ?? $requestPayload['body']['Auth'] ?? [], ['card_number'])),
            'amount' => firstValue($requestPayload['body']['Sale'] ?? $requestPayload['body']['Auth'] ?? $requestPayload['body']['Return'] ?? [], ['transaction_amount']),
            'currency' => firstValue($requestPayload['body']['Sale'] ?? $requestPayload['body']['Auth'] ?? [], ['currency_code']) ?? 'USD',
            'invoice' => firstValue($requestPayload['body']['Sale'] ?? $requestPayload['body']['Auth'] ?? [], ['order_number']),
            'zipCode' => null,
            'originalReference' => $requestPayload['referenceNo'] ?? null,
            'avsResult' => firstValue($responseNode, ['avs_response', 'avsResult']),
            'cvvResult' => firstValue($responseNode, ['cvv2_response', 'cvvResult']),
            'timestamp' => (new DateTimeImmutable())->format(DATE_ATOM),
            'mode' => $environment === 'production' ? 'PRODUCTION MODE' : 'TEST MODE (sandbox)',
            'host' => 'TSYS TransNox',
        ],
        'gatewayRaw' => $gatewayResponse,
    ];
}

function mockResponse(string $txType, array $requestPayload, string $environment): array
{
    $seed = implode('|', [
        $txType,
        $requestPayload['body']['card']['cardNumber'] ?? '',
        (string) ($requestPayload['body']['amount'] ?? '0.00'),
        $requestPayload['referenceNo'] ?? '',
        (new DateTimeImmutable())->format('YmdHi'),
    ]);
    $score = abs((int) crc32($seed)) % 100;
    $approved = $score < 87;
    $responseCode = $approved ? '000' : '051';
    $responseText = $approved ? 'APPROVED' : 'DECLINED';
    return normalizeGatewayResponse(
        [
            'responseCode' => $responseCode,
            'responseText' => $responseText,
            'authCode' => $approved ? strtoupper(substr(hash('sha256', $seed), 0, 6)) : null,
            'referenceNo' => 'TSYS-' . (new DateTimeImmutable())->format('Ymd-His') . '-' . strtoupper(substr(hash('sha1', $seed), 0, 5)),
            'avsResult' => 'Y',
            'cvvResult' => 'M',
        ],
        $txType,
        $requestPayload,
        $environment
    );
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $payload = getInputPayload();
    $txType = strtolower(trim((string) ($payload['txType'] ?? 'charge')));
    $environment = strtolower(trim((string) ($payload['environment'] ?? 'sandbox')));
    $environment = $environment === 'production' ? 'production' : 'sandbox';
    $errors = validatePayload($payload);
    if ($errors !== []) {
        $statusCode = isset($errors['_global']) ? 400 : 422;
        jsonResponse(['ok' => false, 'message' => 'Doğrulama hatası.', 'errors' => $errors], $statusCode);
    }

    $config = getGatewayConfig();
    $requestPayload = buildTsysRequest($txType, $payload, $config);

    try {
        if (($config['gateway_profile'] ?? '') === 'transnox' && $config['enable_mock'] !== true) {
            if (($config['transaction_key'] ?? '') === '' || ($config['developer_id'] ?? '') === '') {
                jsonResponse([
                    'ok' => false,
                    'message' => 'TSYS TransNox için eksik kimlik bilgisi.',
                    'errors' => [
                        'transaction_key' => 'TSYS_TRANSACTION_KEY zorunlu.',
                        'developer_id' => 'TSYS_DEVELOPER_ID zorunlu.',
                    ],
                ], 422);
            }
        }
        if ($config['enable_mock']) {
            jsonResponse(mockResponse($txType, $requestPayload, $environment));
        }
        $gatewayResponse = callTsysGateway($environment, $requestPayload, $config);
        jsonResponse(normalizeGatewayResponse($gatewayResponse, $txType, $requestPayload, $environment));
    } catch (Throwable $exception) {
        jsonResponse([
            'ok' => false,
            'message' => 'TSYS isteği başarısız oldu.',
            'detail' => $exception->getMessage(),
            'hint' => 'TSYS_API_KEY / TSYS_API_USERNAME / TSYS_API_PASSWORD ve endpoint ayarlarını kontrol edin.',
        ], 502);
    }
}
?>
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>TSYS Virtual Terminal</title>
    <link rel="stylesheet" href="./styles.css" />
  </head>
  <body>
    <header class="topbar">
      <div class="brand-line">
        <h1>TSYS Virtual Terminal</h1>
        <span>- Internet Service Provider</span>
      </div>
      <div class="mode-line">
        <button id="prodSwitch" class="prod-switch" type="button">Switch to Production</button>
        <strong id="modeLabel">TEST MODE (sandbox)</strong>
      </div>
    </header>

    <nav class="main-tabs">
      <button class="main-tab active" type="button">Virtual Terminal</button>
      <button class="main-tab" type="button">Transactions</button>
      <button class="main-tab" type="button">Dashboard</button>
      <button class="main-tab" type="button">Settings</button>
    </nav>

    <main class="content">
      <section class="panel">
        <div class="tx-tabs" role="tablist" aria-label="Transaction Type">
          <button class="tx-tab active" data-tx="charge" type="button">Charge</button>
          <button class="tx-tab" data-tx="auth" type="button">Auth</button>
          <button class="tx-tab" data-tx="void" type="button">Void</button>
          <button class="tx-tab" data-tx="return" type="button">Return</button>
        </div>

        <form id="payment-form" novalidate>
          <input type="hidden" id="txType" name="txType" value="charge" />
          <input type="hidden" id="environment" name="environment" value="sandbox" />
          <h2 id="form-title">Charge (Sale)</h2>

          <div class="field">
            <label for="cardNumber">Card number</label>
            <input id="cardNumber" name="cardNumber" inputmode="numeric" maxlength="19" autocomplete="cc-number" required />
            <small class="error-message" data-error-for="cardNumber"></small>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="expiry">Expiration (MMYY)</label>
              <input id="expiry" name="expiry" maxlength="5" placeholder="1228" autocomplete="cc-exp" required />
              <small class="error-message" data-error-for="expiry"></small>
            </div>
            <div class="field">
              <label for="cvv">CVV</label>
              <input id="cvv" name="cvv" inputmode="numeric" maxlength="4" autocomplete="cc-csc" required />
              <small class="error-message" data-error-for="cvv"></small>
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="amount">Amount (USD)</label>
              <input id="amount" name="amount" inputmode="decimal" placeholder="100.00" required />
              <small class="error-message" data-error-for="amount"></small>
            </div>
            <div class="field">
              <label for="zipCode">Billing ZIP</label>
              <input id="zipCode" name="zipCode" maxlength="10" />
              <small class="error-message" data-error-for="zipCode"></small>
            </div>
          </div>

          <div class="field">
            <label for="invoice">Invoice # (optional)</label>
            <input id="invoice" name="invoice" maxlength="24" placeholder="INV-1001" />
            <small class="error-message" data-error-for="invoice"></small>
          </div>

          <div class="field">
            <label for="referenceNo">Original Ref # (Void / Return için)</label>
            <input id="referenceNo" name="referenceNo" maxlength="32" placeholder="TSYS-..." />
            <small class="error-message" data-error-for="referenceNo"></small>
          </div>

          <button id="runButton" type="submit">Run Charge</button>
        </form>
      </section>

      <section class="panel result-panel">
        <h2>Transaction Result</h2>
        <pre id="output">No transaction yet.

Run a Charge, Auth, Void or Return to see the
full host response and codes here.</pre>
      </section>
    </main>

    <script src="./app.js"></script>
  </body>
</html>
