<?php
declare(strict_types=1);

/**
 * TSYS direct-post sample (single file).
 *
 * IMPORTANT:
 * - Keep real secrets only in .env (never in git).
 * - For production, prefer tokenization/hosted fields to avoid touching raw PAN/CVV.
 */

function loadEnv(string $path): void
{
    if (!is_file($path)) {
        return;
    }

    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    if ($lines === false) {
        return;
    }

    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '' || str_starts_with($line, '#') || !str_contains($line, '=')) {
            continue;
        }

        [$key, $value] = explode('=', $line, 2);
        $key = trim($key);
        $value = trim($value);
        $value = trim($value, "\"'");

        if ($key !== '' && getenv($key) === false) {
            putenv($key . '=' . $value);
            $_ENV[$key] = $value;
        }
    }
}

function envValue(string $key, ?string $default = null): ?string
{
    $value = getenv($key);
    if ($value === false || $value === '') {
        return $default;
    }

    return $value;
}

function esc(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

function normalizeMerchantNumber(string $merchantNumber): string
{
    $digits = preg_replace('/\D+/', '', trim($merchantNumber)) ?? '';
    if ($digits === '') {
        return '';
    }

    return str_pad($digits, 12, '0', STR_PAD_LEFT);
}

function normalizeVitalNumber(string $vNumber): string
{
    $raw = strtoupper(trim($vNumber));
    if ($raw === '') {
        return '';
    }

    // Many TSYS/Vital setups require replacing leading V with 7.
    if (preg_match('/^V(\d{7})$/', $raw, $m)) {
        return '7' . $m[1];
    }

    $digits = preg_replace('/\D+/', '', $raw) ?? '';
    if (strlen($digits) === 8) {
        return $digits;
    }

    return $raw;
}

function normalizeAmount(string $amount): string
{
    $amount = str_replace(',', '.', trim($amount));
    if (!preg_match('/^\d+(\.\d{1,2})?$/', $amount)) {
        throw new InvalidArgumentException('Amount format is invalid.');
    }

    return number_format((float)$amount, 2, '.', '');
}

function parseExpiry(string $expiry): array
{
    $expiry = trim($expiry);
    if (!preg_match('/^(0[1-9]|1[0-2])\/?(\d{2}|\d{4})$/', $expiry, $m)) {
        throw new InvalidArgumentException('Expiry must be MM/YY or MM/YYYY.');
    }

    $month = $m[1];
    $year = $m[2];
    if (strlen($year) === 2) {
        $year = '20' . $year;
    }

    return [$month, $year];
}

function maskCard(string $cardNumber): string
{
    $digits = preg_replace('/\D+/', '', $cardNumber);
    if ($digits === null || strlen($digits) < 8) {
        return '********';
    }

    return substr($digits, 0, 6) . str_repeat('*', max(strlen($digits) - 10, 0)) . substr($digits, -4);
}

function requestToGateway(string $url, array $payload, string $apiKey): array
{
    $ch = curl_init($url);
    if ($ch === false) {
        throw new RuntimeException('cURL initialization failed.');
    }

    $json = json_encode($payload, JSON_THROW_ON_ERROR);

    $headers = [
        'Content-Type: application/json',
        'Accept: application/json',
    ];
    if (trim($apiKey) !== '') {
        $headers[] = 'Authorization: Bearer ' . $apiKey;
    }

    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 45,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_POSTFIELDS => $json,
    ]);

    $body = curl_exec($ch);
    $curlError = curl_error($ch);
    $httpCode = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($body === false) {
        throw new RuntimeException('Gateway request failed: ' . $curlError);
    }

    $decoded = json_decode($body, true);
    if (!is_array($decoded)) {
        $decoded = ['raw_response' => $body];
    }

    return [
        'http_code' => $httpCode,
        'response' => $decoded,
        'raw_response' => $body,
    ];
}

function mockGatewayResponse(array $payload): array
{
    $approved = random_int(1, 100) > 8; // ~92% success for demo behavior.
    $txType = (string)($payload['transaction']['type'] ?? 'sale');

    return [
        'http_code' => $approved ? 200 : 402,
        'response' => [
            'mode' => 'mock',
            'approved' => $approved,
            'transaction_type' => $txType,
            'transaction_id' => 'MOCK-' . strtoupper(bin2hex(random_bytes(4))),
            'auth_code' => $approved ? strtoupper(substr(bin2hex(random_bytes(3)), 0, 6)) : null,
            'message' => $approved
                ? ($txType === 'return' ? 'Mock return approved' : 'Mock sale approved')
                : 'Mock decline: insufficient funds',
            'amount' => (string)($payload['transaction']['amount'] ?? '0.00'),
            'currency' => (string)($payload['transaction']['currency'] ?? 'USD'),
            'user_trace' => (string)($payload['transaction']['user_trace'] ?? ''),
            'created_at' => gmdate('c'),
        ],
        'raw_response' => '',
    ];
}

loadEnv(__DIR__ . '/.env');
if (!is_file(__DIR__ . '/.env')) {
    loadEnv(__DIR__ . '/.env.example');
}

$config = [
    // Merchant defaults are pre-filled from your provided profile.
    'api_url' => envValue('TSYS_API_URL', 'https://ssl2.vitalps.net/scripts/gateway.dll?transact'),
    'api_key' => envValue('TSYS_API_KEY', ''),
    'merchant_number' => envValue('TSYS_MERCHANT_NUMBER', '401151759710'),
    'v_number' => envValue('TSYS_V_NUMBER', 'V6298237'),
    'store_number' => envValue('TSYS_STORE_NUMBER', '0001'),
    'terminal_number' => envValue('TSYS_TERMINAL_NUMBER', '7000'),
    'location_number' => envValue('TSYS_LOCATION_NUMBER', '00001'),
    'currency' => envValue('TSYS_CURRENCY', 'USD'),
];

$merchantProfile = [
    'dba' => envValue('TSYS_DBA', 'Get Your Life Back LLC'),
    'street' => envValue('TSYS_STREET', '28 Tindall Rd'),
    'city' => envValue('TSYS_CITY', 'Middletown'),
    'state' => envValue('TSYS_STATE', 'New Jersey'),
    'zip' => envValue('TSYS_ZIP', '07748'),
    'customer_service_phone' => envValue('TSYS_CUSTOMER_SERVICE_PHONE', '+1 800-993-0929'),
    'mcc' => envValue('TSYS_MCC', '5499'),
    'bin' => envValue('TSYS_BIN', '494306'),
    'chain' => envValue('TSYS_CHAIN', '031776'),
    'agent_bank' => envValue('TSYS_AGENT_BANK', '031776'),
];

// Final safety fallback: keep merchant identity populated even if env is missing.
if ($config['merchant_number'] === '' || $config['merchant_number'] === null) {
    $config['merchant_number'] = '401151759710';
}
if ($config['v_number'] === '' || $config['v_number'] === null) {
    $config['v_number'] = 'V6298237';
}
if ($merchantProfile['dba'] === '' || $merchantProfile['dba'] === null) {
    $merchantProfile['dba'] = 'Get Your Life Back LLC';
}
$config['merchant_number'] = normalizeMerchantNumber((string)$config['merchant_number']);
$config['v_number'] = normalizeVitalNumber((string)$config['v_number']);

$errors = [];
$result = null;

$defaults = [
    'gateway_mode' => strtolower((string)envValue('TSYS_GATEWAY_MODE', 'mock')) === 'live' ? 'live' : 'mock',
    'transaction_type' => 'sale',
    'amount' => '10.00',
    'api_url' => (string)$config['api_url'],
    'api_key' => (string)$config['api_key'],
    'card_number' => '',
    'expiry' => '',
    'cvv' => '',
    'zip' => '',
    'original_transaction_id' => '',
    'user_trace' => bin2hex(random_bytes(4)),
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = [
        'gateway_mode' => strtolower(trim((string)($_POST['gateway_mode'] ?? (string)$defaults['gateway_mode']))),
        'transaction_type' => strtolower(trim((string)($_POST['transaction_type'] ?? 'sale'))),
        'amount' => trim((string)($_POST['amount'] ?? '')),
        'api_url' => trim((string)($_POST['api_url'] ?? (string)$config['api_url'])),
        'api_key' => trim((string)($_POST['api_key'] ?? (string)$config['api_key'])),
        'card_number' => trim((string)($_POST['card_number'] ?? '')),
        'expiry' => trim((string)($_POST['expiry'] ?? '')),
        'cvv' => trim((string)($_POST['cvv'] ?? '')),
        'zip' => trim((string)($_POST['zip'] ?? '')),
        'original_transaction_id' => trim((string)($_POST['original_transaction_id'] ?? '')),
        'user_trace' => trim((string)($_POST['user_trace'] ?? '')),
    ];
    $defaults = array_merge($defaults, $input);

    if (!in_array($input['transaction_type'], ['sale', 'return'], true)) {
        $errors[] = 'Transaction type must be sale or return.';
    }

    try {
        $amount = normalizeAmount($input['amount']);
    } catch (InvalidArgumentException $e) {
        $errors[] = $e->getMessage();
        $amount = '0.00';
    }

    $cardNumberDigits = preg_replace('/\D+/', '', $input['card_number']) ?? '';
    if (strlen($cardNumberDigits) < 12 || strlen($cardNumberDigits) > 19) {
        $errors[] = 'Card number looks invalid.';
    }

    try {
        [$expMonth, $expYear] = parseExpiry($input['expiry']);
    } catch (InvalidArgumentException $e) {
        $errors[] = $e->getMessage();
        $expMonth = '';
        $expYear = '';
    }

    if (!preg_match('/^\d{3,4}$/', $input['cvv'])) {
        $errors[] = 'CVV must be 3 or 4 digits.';
    }

    if (!preg_match('/^\d{5}(-\d{4})?$/', $input['zip'])) {
        $errors[] = 'ZIP must be 5 digits (or ZIP+4).';
    }

    $effectiveConfig = $config;
    $effectiveConfig['api_url'] = $input['api_url'];
    $effectiveConfig['api_key'] = $input['api_key'];
    $effectiveConfig['gateway_mode'] = in_array($input['gateway_mode'], ['live', 'mock'], true) ? $input['gateway_mode'] : 'mock';

    if ($effectiveConfig['gateway_mode'] === 'live') {
        foreach (['api_url'] as $required) {
            if (($effectiveConfig[$required] ?? '') === '') {
                $errors[] = sprintf('Missing config: %s', $required);
            }
        }
        if (($effectiveConfig['merchant_number'] ?? '') === '' || strlen((string)$effectiveConfig['merchant_number']) !== 12) {
            $errors[] = 'Merchant number must be 12 digits.';
        }
        if (($effectiveConfig['v_number'] ?? '') === '' || strlen((string)$effectiveConfig['v_number']) !== 8) {
            $errors[] = 'V number must resolve to 8 digits (ex: V1234567 -> 71234567).';
        }
    }
    if ($input['transaction_type'] === 'return' && $input['original_transaction_id'] === '') {
        $errors[] = 'Original transaction ID is required for return.';
    }

    if ($errors === []) {
        $payload = [
            'merchant' => [
                'merchant_number' => $config['merchant_number'],
                'v_number' => $config['v_number'],
                'store_number' => $config['store_number'],
                'terminal_number' => $config['terminal_number'],
                'location_number' => $config['location_number'],
                'dba' => $merchantProfile['dba'],
                'mcc' => $merchantProfile['mcc'],
                'bin' => $merchantProfile['bin'],
                'chain' => $merchantProfile['chain'],
                'agent_bank' => $merchantProfile['agent_bank'],
            ],
            'transaction' => [
                'type' => $input['transaction_type'],
                'amount' => $amount,
                'currency' => $config['currency'],
                'user_trace' => $input['user_trace'] !== '' ? $input['user_trace'] : ('trace-' . time()),
            ],
            'payment_method' => [
                'card' => [
                    'number' => $cardNumberDigits,
                    'exp_month' => $expMonth,
                    'exp_year' => $expYear,
                    'cvv' => $input['cvv'],
                    'zip' => $input['zip'],
                ],
            ],
            'billing' => [
                'street' => $merchantProfile['street'],
                'city' => $merchantProfile['city'],
                'state' => $merchantProfile['state'],
                'zip' => $merchantProfile['zip'],
                'phone' => $merchantProfile['customer_service_phone'],
            ],
            'meta' => [
                'client_ip' => $_SERVER['REMOTE_ADDR'] ?? '',
                'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
            ],
        ];
        if ($input['transaction_type'] === 'return') {
            $payload['transaction']['original_transaction_id'] = $input['original_transaction_id'];
            $payload['transaction']['reason'] = 'customer_requested_refund';
        }

        try {
            $gatewayResult = $effectiveConfig['gateway_mode'] === 'mock'
                ? mockGatewayResponse($payload)
                : requestToGateway($effectiveConfig['api_url'], $payload, $effectiveConfig['api_key']);
            $result = [
                'success' => $gatewayResult['http_code'] >= 200 && $gatewayResult['http_code'] < 300,
                'http_code' => $gatewayResult['http_code'],
                'response' => $gatewayResult['response'],
                'masked_card' => maskCard($cardNumberDigits),
                'gateway_mode' => $effectiveConfig['gateway_mode'],
            ];
        } catch (Throwable $e) {
            $errors[] = $e->getMessage();
        }
    }
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>TSYS Virtual Terminal (PHP)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background: #f6f6f6; color: #222; }
        .card { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 16px; max-width: 900px; }
        .row { display: flex; gap: 12px; margin-bottom: 12px; }
        .col { flex: 1; }
        label { display: block; font-size: 13px; margin-bottom: 5px; }
        input, select, button { width: 100%; box-sizing: border-box; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #111; color: #fff; border: none; cursor: pointer; }
        .error { background: #ffe7e7; border: 1px solid #f0b3b3; color: #8f1f1f; padding: 10px; margin-bottom: 12px; border-radius: 4px; }
        .ok { background: #e8f8ea; border: 1px solid #b8dfbe; color: #205b2a; padding: 10px; margin-bottom: 12px; border-radius: 4px; }
        pre { white-space: pre-wrap; word-break: break-word; background: #f3f3f3; padding: 10px; border-radius: 4px; }
        .hint { font-size: 12px; color: #666; margin-top: 8px; }
    </style>
</head>
<body>
    <h2>Virtual Terminal</h2>
    <div class="card">
        <p><strong>Merchant:</strong> <?= esc((string)$merchantProfile['dba']) ?> (<?= esc((string)$config['merchant_number']) ?>)</p>

        <?php if ($errors !== []): ?>
            <div class="error">
                <strong>Please check all required fields:</strong>
                <ul>
                    <?php foreach ($errors as $error): ?>
                        <li><?= esc($error) ?></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        <?php endif; ?>

        <?php if (is_array($result)): ?>
            <div class="<?= $result['success'] ? 'ok' : 'error' ?>">
                <strong><?= $result['success'] ? 'Transaction sent successfully.' : 'Gateway returned an error.' ?></strong><br>
                Mode: <?= esc((string)$result['gateway_mode']) ?><br>
                HTTP Code: <?= esc((string)$result['http_code']) ?><br>
                Card: <?= esc((string)$result['masked_card']) ?>
            </div>
            <pre><?= esc((string)json_encode($result['response'], JSON_PRETTY_PRINT)) ?></pre>
        <?php endif; ?>

        <form method="post" autocomplete="off">
            <div class="row">
                <div class="col">
                    <label for="gateway_mode">Gateway Mode</label>
                    <select id="gateway_mode" name="gateway_mode">
                        <option value="mock" <?= $defaults['gateway_mode'] === 'mock' ? 'selected' : '' ?>>Mock (immediate test)</option>
                        <option value="live" <?= $defaults['gateway_mode'] === 'live' ? 'selected' : '' ?>>Live TSYS</option>
                    </select>
                </div>
            </div>

            <div class="row">
                <div class="col">
                    <label for="api_url">Gateway API URL</label>
                    <input id="api_url" name="api_url" value="<?= esc((string)$defaults['api_url']) ?>" placeholder="https://.../transactions" required>
                </div>
                <div class="col">
                    <label for="api_key">Gateway API Key (opsiyonel)</label>
                    <input id="api_key" name="api_key" value="<?= esc((string)$defaults['api_key']) ?>" placeholder="API key (if required)">
                </div>
            </div>

            <div class="row">
                <div class="col">
                    <label for="transaction_type">Transaction Type</label>
                    <select id="transaction_type" name="transaction_type">
                        <option value="sale" <?= $defaults['transaction_type'] === 'sale' ? 'selected' : '' ?>>Sale</option>
                        <option value="return" <?= $defaults['transaction_type'] === 'return' ? 'selected' : '' ?>>Return</option>
                    </select>
                </div>
                <div class="col">
                    <label for="amount">Amount</label>
                    <input id="amount" name="amount" value="<?= esc((string)$defaults['amount']) ?>" placeholder="10.00" required>
                </div>
            </div>

            <div class="row">
                <div class="col">
                    <label for="card_number">Card Number</label>
                    <input id="card_number" name="card_number" value="<?= esc((string)$defaults['card_number']) ?>" placeholder="4111111111111111" required>
                </div>
                <div class="col">
                    <label for="expiry">Expiration (MM/YY)</label>
                    <input id="expiry" name="expiry" value="<?= esc((string)$defaults['expiry']) ?>" placeholder="04/28" required>
                </div>
            </div>

            <div class="row">
                <div class="col">
                    <label for="cvv">CVV</label>
                    <input id="cvv" name="cvv" value="<?= esc((string)$defaults['cvv']) ?>" placeholder="123" required>
                </div>
                <div class="col">
                    <label for="zip">ZIP</label>
                    <input id="zip" name="zip" value="<?= esc((string)$defaults['zip']) ?>" placeholder="07748" required>
                </div>
                <div class="col">
                    <label for="user_trace">User Trace</label>
                    <input id="user_trace" name="user_trace" value="<?= esc((string)$defaults['user_trace']) ?>" placeholder="trace-id">
                </div>
            </div>
            <div class="row">
                <div class="col">
                    <label for="original_transaction_id">Original Transaction ID (Return icin)</label>
                    <input
                        id="original_transaction_id"
                        name="original_transaction_id"
                        value="<?= esc((string)$defaults['original_transaction_id']) ?>"
                        placeholder="sale transaction id"
                    >
                </div>
            </div>

            <button type="submit">Process Transaction</button>
            <p class="hint">
                This direct-post example is for controlled server-side integration. For production internet payments,
                use TSYS tokenization/hosted fields + 3DS where available. In Mock mode, no external gateway call is made.
            </p>
        </form>
    </div>
</body>
</html>
