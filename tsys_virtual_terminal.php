<?php
declare(strict_types=1);

/**
 * TSYS benzeri tek dosyalik sanal terminal ornegi.
 *
 * Not:
 * - Bu dosya, TSYS API detaylari ortama gore degistigi icin endpoint ve yetkilendirme
 *   basliklarini environment degiskenleri ile bekler.
 * - Verilen merchant bilgileri entegre edilmistir.
 */

$merchantConfig = [
    'dba' => 'Get Your Life Back LLC',
    'streetAddress' => '28 Tindall Rd',
    'city' => 'Middletown',
    'state' => 'New Jersey',
    'zip' => '07748',
    'customerServicePhone' => '+1 800-993-0929',
    'merchantNumber' => '401151759710',
    'vNumber' => 'V6298237',
    'mcc' => '5499',
    'bin' => '494306',
    'chain' => '031776',
    'agentBank' => '031776',
    'storeNumber' => '0001',
    'terminalNumber' => '7000',
    'locationNumber' => '00001',
    'cardTypesAccepted' => [
        'Visa',
        'Mastercard PIN Debit Gift Card',
        'American Express EBT',
        'Discover/JCB ACH',
    ],
    'approvedMonthlyVolume' => '$30,000.00',
];

$defaultGatewayUrl = 'https://stagegw.transnox.com/servlets/transnox_api_server';
$gatewayUrl = trim((string) ($_POST['gateway_url'] ?? getenv('TSYS_API_URL') ?: $defaultGatewayUrl));

$apiConfig = [
    // Canli/sandbox endpointi: form alani > environment > fallback.
    'baseUrl' => rtrim($gatewayUrl, '/'),
    'apiKey' => (string) getenv('TSYS_API_KEY'),
    'apiSecret' => (string) getenv('TSYS_API_SECRET'),
    'timeout' => 45,
];

$result = [
    'ok' => false,
    'message' => 'No transaction yet.',
    'details' => [],
];

$activeTab = 'charge';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $activeTab = strtolower(trim((string) ($_POST['transaction_type'] ?? 'charge')));
    $supportedTypes = ['charge', 'auth', 'void', 'return'];
    if (!in_array($activeTab, $supportedTypes, true)) {
        $activeTab = 'charge';
    }

    $input = [
        'card_number' => preg_replace('/\D+/', '', (string) ($_POST['card_number'] ?? '')),
        'expiration' => strtoupper(trim((string) ($_POST['expiration'] ?? ''))),
        'cvv' => trim((string) ($_POST['cvv'] ?? '')),
        'amount' => trim((string) ($_POST['amount'] ?? '')),
        'billing_zip' => trim((string) ($_POST['billing_zip'] ?? '')),
        'invoice' => trim((string) ($_POST['invoice'] ?? '')),
        'original_transaction_id' => trim((string) ($_POST['original_transaction_id'] ?? '')),
    ];

    try {
        $payload = buildPayload($activeTab, $input, $merchantConfig);
        $apiResult = sendToTsys($payload, $apiConfig);
        $result = [
            'ok' => $apiResult['ok'],
            'message' => $apiResult['message'],
            'details' => $apiResult['details'],
        ];
    } catch (Throwable $exception) {
        $result = [
            'ok' => false,
            'message' => 'Request could not be completed.',
            'details' => [
                'error' => $exception->getMessage(),
            ],
        ];
    }
}

function buildPayload(string $transactionType, array $input, array $merchantConfig): array
{
    $transactionMap = [
        'charge' => 'sale',
        'auth' => 'auth',
        'void' => 'void',
        'return' => 'refund',
    ];

    if (!isset($transactionMap[$transactionType])) {
        throw new InvalidArgumentException('Unsupported transaction type.');
    }

    $request = [
        'merchant' => [
            'dba' => $merchantConfig['dba'],
            'merchantNumber' => $merchantConfig['merchantNumber'],
            'vNumber' => $merchantConfig['vNumber'],
            'mcc' => $merchantConfig['mcc'],
            'bin' => $merchantConfig['bin'],
            'chain' => $merchantConfig['chain'],
            'agentBank' => $merchantConfig['agentBank'],
            'storeNumber' => $merchantConfig['storeNumber'],
            'terminalNumber' => $merchantConfig['terminalNumber'],
            'locationNumber' => $merchantConfig['locationNumber'],
            'address' => [
                'street' => $merchantConfig['streetAddress'],
                'city' => $merchantConfig['city'],
                'state' => $merchantConfig['state'],
                'zip' => $merchantConfig['zip'],
                'phone' => $merchantConfig['customerServicePhone'],
            ],
        ],
        'transactionType' => $transactionMap[$transactionType],
        'invoiceNumber' => $input['invoice'] !== '' ? $input['invoice'] : null,
    ];

    if (in_array($transactionType, ['charge', 'auth'], true)) {
        if ($input['card_number'] === '' || $input['expiration'] === '' || $input['cvv'] === '' || $input['amount'] === '') {
            throw new InvalidArgumentException('Card number, expiration, CVV and amount are required.');
        }

        [$expMonth, $expYear] = parseExpiry($input['expiration']);
        $amount = normalizeAmount($input['amount']);

        $request['amount'] = $amount;
        $request['currency'] = 'USD';
        $request['paymentMethod'] = [
            'type' => 'card',
            'cardNumber' => $input['card_number'],
            'expirationMonth' => $expMonth,
            'expirationYear' => $expYear,
            'cvv' => $input['cvv'],
            'billingZip' => $input['billing_zip'] !== '' ? $input['billing_zip'] : null,
        ];
    }

    if (in_array($transactionType, ['void', 'return'], true)) {
        if ($input['original_transaction_id'] === '') {
            throw new InvalidArgumentException('Original transaction id is required for void/return.');
        }

        $request['originalTransactionId'] = $input['original_transaction_id'];

        // Iade islemlerinde amount opsiyonel olabilir, doluysa gonderilir.
        if ($input['amount'] !== '') {
            $request['amount'] = normalizeAmount($input['amount']);
            $request['currency'] = 'USD';
        }
    }

    // API'ye null alanlar gitmesin.
    return array_filter_recursive($request);
}

function sendToTsys(array $payload, array $apiConfig): array
{
    if ($apiConfig['baseUrl'] === '') {
        throw new RuntimeException('Gateway URL bos birakilamaz.');
    }

    $endpoint = resolveTsysEndpoint($apiConfig['baseUrl']);

    $headers = [
        'Content-Type: application/json',
        'Accept: application/json',
    ];

    // Cogu TSYS entegrasyonunda API key/secret veya benzeri auth gerekir.
    if ($apiConfig['apiKey'] !== '' && $apiConfig['apiSecret'] !== '') {
        $headers[] = 'Authorization: Basic ' . base64_encode($apiConfig['apiKey'] . ':' . $apiConfig['apiSecret']);
    } elseif ($apiConfig['apiKey'] !== '') {
        $headers[] = 'Authorization: Bearer ' . $apiConfig['apiKey'];
    }

    $ch = curl_init($endpoint);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => (int) $apiConfig['timeout'],
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_POSTFIELDS => json_encode($payload, JSON_UNESCAPED_SLASHES),
    ]);

    $body = curl_exec($ch);
    if ($body === false) {
        $error = curl_error($ch);
        curl_close($ch);
        throw new RuntimeException('cURL error: ' . $error);
    }

    $httpStatus = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $decoded = json_decode($body, true);
    if (!is_array($decoded)) {
        $decoded = ['raw_response' => $body];
    }

    $ok = $httpStatus >= 200 && $httpStatus < 300;
    $message = $ok ? 'Transaction sent successfully.' : 'TSYS request failed.';

    return [
        'ok' => $ok,
        'message' => $message,
        'details' => [
            'gateway_url' => $endpoint,
            'http_status' => $httpStatus,
            'request_payload' => maskRequestPayload($payload),
            'response' => $decoded,
        ],
    ];
}

function resolveTsysEndpoint(string $baseUrl): string
{
    // Eger URL dogrudan endpoint ise oldugu gibi kullan.
    if (preg_match('/(\/transactions|transnox_api_server)$/', $baseUrl) === 1) {
        return $baseUrl;
    }

    // Varsayilan REST endpoint sonu.
    return $baseUrl . '/transactions';
}

function parseExpiry(string $expiration): array
{
    if (!preg_match('/^(0[1-9]|1[0-2])\s*\/\s*(\d{2}|\d{4})$/', $expiration, $match)) {
        throw new InvalidArgumentException('Expiration must be MM/YY or MM/YYYY.');
    }

    $month = $match[1];
    $year = $match[2];
    if (strlen($year) === 2) {
        $year = '20' . $year;
    }

    return [$month, $year];
}

function normalizeAmount(string $amount): string
{
    $clean = str_replace(',', '.', trim($amount));
    if (!is_numeric($clean)) {
        throw new InvalidArgumentException('Amount must be numeric.');
    }

    $float = (float) $clean;
    if ($float <= 0) {
        throw new InvalidArgumentException('Amount must be greater than zero.');
    }

    return number_format($float, 2, '.', '');
}

function maskCard(string $cardNumber): string
{
    if ($cardNumber === '') {
        return '';
    }
    $len = strlen($cardNumber);
    if ($len <= 4) {
        return str_repeat('*', $len);
    }
    return str_repeat('*', $len - 4) . substr($cardNumber, -4);
}

function maskRequestPayload(array $payload): array
{
    if (isset($payload['paymentMethod']['cardNumber'])) {
        $payload['paymentMethod']['cardNumber'] = maskCard((string) $payload['paymentMethod']['cardNumber']);
    }
    if (isset($payload['paymentMethod']['cvv'])) {
        $payload['paymentMethod']['cvv'] = '***';
    }
    return $payload;
}

function array_filter_recursive(array $data): array
{
    foreach ($data as $key => $value) {
        if (is_array($value)) {
            $data[$key] = array_filter_recursive($value);
            if ($data[$key] === []) {
                unset($data[$key]);
            }
        } elseif ($value === null || $value === '') {
            unset($data[$key]);
        }
    }
    return $data;
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSYS Virtual Terminal</title>
    <style>
        :root {
            --navy: #0f1f44;
            --panel: #f1f3f7;
            --border: #cfd6e3;
            --primary: #1c9ed8;
            --text: #1f2b3d;
            --muted: #6e7f95;
            --success: #2b8a3e;
            --error: #c92a2a;
        }
        * { box-sizing: border-box; font-family: Arial, sans-serif; }
        body { margin: 0; background: #d9e2ef; color: var(--text); }
        .topbar {
            background: var(--navy);
            color: #fff;
            padding: 14px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 700;
        }
        .topbar small { opacity: 0.85; margin-left: 10px; font-weight: 400; }
        .environment {
            background: #2ea44f20;
            color: #8fffaa;
            border: 1px solid #7de599;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
        }
        .shell {
            max-width: 1200px;
            margin: 18px auto;
            background: #fff;
            border: 1px solid var(--border);
            padding: 12px;
        }
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--border);
            margin-bottom: 12px;
            gap: 4px;
        }
        .tab-btn {
            border: 1px solid var(--border);
            border-bottom: none;
            background: #eef2f8;
            color: #536479;
            padding: 10px 16px;
            cursor: pointer;
            font-weight: 700;
        }
        .tab-btn.active {
            background: #fff;
            color: #1b2a41;
        }
        .layout {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 14px;
        }
        .panel {
            border: 1px solid var(--border);
            background: var(--panel);
            padding: 14px;
            min-height: 560px;
        }
        .panel h2 {
            margin: 0 0 10px;
            font-size: 24px;
            color: #1f2b3d;
        }
        .panel h3 {
            margin: 8px 0 16px;
            font-size: 21px;
            color: #1f2b3d;
        }
        .field { margin-bottom: 14px; }
        .field label {
            display: block;
            font-size: 13px;
            color: #5c6f86;
            margin-bottom: 4px;
            font-weight: 700;
        }
        .field input {
            width: 100%;
            border: 2px solid #9faec2;
            padding: 10px;
            font-size: 15px;
            background: #fff;
        }
        .row-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .cta {
            width: 100%;
            border: none;
            padding: 14px;
            font-size: 24px;
            font-weight: 700;
            color: #fff;
            background: var(--primary);
            cursor: pointer;
            margin-top: 12px;
        }
        .status {
            background: #f8fafc;
            border: 1px dashed #c2cfdf;
            padding: 12px;
            margin-bottom: 12px;
            min-height: 110px;
        }
        .status.ok { border-color: #b8e7c4; background: #edf9f0; color: var(--success); }
        .status.error { border-color: #f2c2c2; background: #fff1f1; color: var(--error); }
        pre {
            background: #f5f7fb;
            border: 1px solid #d8e0ec;
            padding: 12px;
            overflow: auto;
            max-height: 380px;
            margin: 0;
            font-size: 13px;
        }
        .merchant-box {
            margin-top: 14px;
            font-size: 12px;
            color: var(--muted);
            line-height: 1.45;
            border-top: 1px solid #d5deea;
            padding-top: 10px;
        }
        .hidden { display: none; }
        @media (max-width: 980px) {
            .layout { grid-template-columns: 1fr; }
            .panel { min-height: auto; }
            .cta { font-size: 19px; }
        }
    </style>
</head>
<body>
<div class="topbar">
    <div>
        TSYS Virtual Terminal
        <small>- Internet Service Provider</small>
    </div>
    <div class="environment">TEST MODE (sandbox)</div>
</div>

<div class="shell">
    <div class="tabs">
        <button class="tab-btn <?= $activeTab === 'charge' ? 'active' : '' ?>" type="button" data-tab="charge">Charge</button>
        <button class="tab-btn <?= $activeTab === 'auth' ? 'active' : '' ?>" type="button" data-tab="auth">Auth</button>
        <button class="tab-btn <?= $activeTab === 'void' ? 'active' : '' ?>" type="button" data-tab="void">Void</button>
        <button class="tab-btn <?= $activeTab === 'return' ? 'active' : '' ?>" type="button" data-tab="return">Return</button>
    </div>

    <div class="layout">
        <div class="panel">
            <h2 id="operation-title">Charge</h2>
            <h3 id="operation-subtitle">Charge (Sale)</h3>

            <form method="post" id="payment-form" autocomplete="off">
                <input type="hidden" name="transaction_type" id="transaction_type" value="<?= htmlspecialchars($activeTab) ?>">

                <div id="card-fields">
                    <div class="field">
                        <label for="card_number">Card number</label>
                        <input id="card_number" name="card_number" type="text" inputmode="numeric" maxlength="19" placeholder="4111111111111111">
                    </div>
                    <div class="row-2">
                        <div class="field">
                            <label for="expiration">Expiration (MM/YY / MM/YYYY)</label>
                            <input id="expiration" name="expiration" type="text" maxlength="7" placeholder="12/28">
                        </div>
                        <div class="field">
                            <label for="cvv">CVV</label>
                            <input id="cvv" name="cvv" type="password" inputmode="numeric" maxlength="4" placeholder="123">
                        </div>
                    </div>
                    <div class="row-2">
                        <div class="field">
                            <label for="amount">Amount (USD)</label>
                            <input id="amount" name="amount" type="text" inputmode="decimal" placeholder="10.00">
                        </div>
                        <div class="field">
                            <label for="billing_zip">Billing ZIP</label>
                            <input id="billing_zip" name="billing_zip" type="text" placeholder="07748">
                        </div>
                    </div>
                    <div class="field">
                        <label for="invoice">Invoice # (optional)</label>
                        <input id="invoice" name="invoice" type="text" maxlength="30">
                    </div>
                </div>

                <div id="reversal-fields" class="hidden">
                    <div class="field">
                        <label for="original_transaction_id">Original transaction id</label>
                        <input id="original_transaction_id" name="original_transaction_id" type="text" placeholder="TSYS transaction reference">
                    </div>
                    <div class="field">
                        <label for="amount_refund">Amount (USD, optional for full return)</label>
                        <input id="amount_refund" type="text" inputmode="decimal" placeholder="10.00">
                    </div>
                </div>

                <div class="field">
                    <label for="gateway_url">TSYS Gateway URL</label>
                    <input
                        id="gateway_url"
                        name="gateway_url"
                        type="text"
                        value="<?= htmlspecialchars($apiConfig['baseUrl']) ?>"
                        placeholder="https://stagegw.transnox.com/servlets/transnox_api_server"
                    >
                </div>

                <button class="cta" id="action-button" type="submit">Run Charge</button>
            </form>

            <div class="merchant-box">
                <strong>Merchant:</strong> <?= htmlspecialchars($merchantConfig['dba']) ?><br>
                Merchant #<?= htmlspecialchars($merchantConfig['merchantNumber']) ?> |
                Terminal #<?= htmlspecialchars($merchantConfig['terminalNumber']) ?> |
                Store #<?= htmlspecialchars($merchantConfig['storeNumber']) ?><br>
                <?= htmlspecialchars($merchantConfig['streetAddress']) ?>, <?= htmlspecialchars($merchantConfig['city']) ?>, <?= htmlspecialchars($merchantConfig['state']) ?> <?= htmlspecialchars($merchantConfig['zip']) ?><br>
                Customer Service: <?= htmlspecialchars($merchantConfig['customerServicePhone']) ?>
            </div>
        </div>

        <div class="panel">
            <h2>Transaction Result</h2>
            <div class="status <?= $result['ok'] ? 'ok' : 'error' ?>">
                <strong><?= htmlspecialchars($result['message']) ?></strong>
            </div>
            <pre><?= htmlspecialchars(json_encode($result['details'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)) ?></pre>
        </div>
    </div>
</div>

<script>
    const tabConfig = {
        charge: { title: 'Charge', subtitle: 'Charge (Sale)', button: 'Run Charge', reversal: false },
        auth: { title: 'Auth', subtitle: 'Authorization', button: 'Run Auth', reversal: false },
        void: { title: 'Void', subtitle: 'Void Transaction', button: 'Run Void', reversal: true },
        return: { title: 'Return', subtitle: 'Return (Refund)', button: 'Run Return', reversal: true }
    };

    const tabs = Array.from(document.querySelectorAll('.tab-btn'));
    const transactionInput = document.getElementById('transaction_type');
    const operationTitle = document.getElementById('operation-title');
    const operationSubtitle = document.getElementById('operation-subtitle');
    const actionButton = document.getElementById('action-button');
    const cardFields = document.getElementById('card-fields');
    const reversalFields = document.getElementById('reversal-fields');
    const amountField = document.getElementById('amount');
    const refundAmountField = document.getElementById('amount_refund');

    function applyTab(tabName) {
        const cfg = tabConfig[tabName] || tabConfig.charge;
        tabs.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabName));
        transactionInput.value = tabName;
        operationTitle.textContent = cfg.title;
        operationSubtitle.textContent = cfg.subtitle;
        actionButton.textContent = cfg.button;

        if (cfg.reversal) {
            cardFields.classList.add('hidden');
            reversalFields.classList.remove('hidden');
            amountField.removeAttribute('name');
            refundAmountField.setAttribute('name', 'amount');
        } else {
            cardFields.classList.remove('hidden');
            reversalFields.classList.add('hidden');
            refundAmountField.removeAttribute('name');
            amountField.setAttribute('name', 'amount');
        }
    }

    tabs.forEach(btn => {
        btn.addEventListener('click', () => applyTab(btn.dataset.tab));
    });

    applyTab('<?= htmlspecialchars($activeTab) ?>');
</script>
</body>
</html>
