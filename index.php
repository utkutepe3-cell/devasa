<?php
declare(strict_types=1);

function jsonResponse(array $payload, int $statusCode = 200): void
{
    http_response_code($statusCode);
    header('Content-Type: application/json; charset=UTF-8');
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    exit;
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

    $lastDayOfMonth = $expDate->modify('last day of this month')->setTime(23, 59, 59);
    if ($lastDayOfMonth < new DateTimeImmutable('now')) {
        return null;
    }

    return ['month' => str_pad((string) $month, 2, '0', STR_PAD_LEFT), 'year' => (string) $fullYear];
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $rawInput = file_get_contents('php://input') ?: '';
    $contentType = $_SERVER['CONTENT_TYPE'] ?? '';
    $payload = [];

    if (str_contains(strtolower($contentType), 'application/json')) {
        $decoded = json_decode($rawInput, true);
        if (is_array($decoded)) {
            $payload = $decoded;
        }
    } else {
        $payload = $_POST;
        if (!$payload && $rawInput !== '') {
            parse_str($rawInput, $payload);
        }
    }

    $txType = strtolower(trim((string) ($payload['txType'] ?? 'charge')));
    $allowedTxTypes = ['charge', 'auth', 'void', 'return'];
    if (!in_array($txType, $allowedTxTypes, true)) {
        jsonResponse(['ok' => false, 'message' => 'Geçersiz işlem tipi.'], 422);
    }

    $cardNumber = trim((string) ($payload['cardNumber'] ?? ''));
    $expiry = trim((string) ($payload['expiry'] ?? ''));
    $cvv = trim((string) ($payload['cvv'] ?? ''));
    $amountRaw = trim((string) ($payload['amount'] ?? ''));
    $zipCode = trim((string) ($payload['zipCode'] ?? ''));
    $invoice = trim((string) ($payload['invoice'] ?? ''));
    $referenceNo = trim((string) ($payload['referenceNo'] ?? ''));
    $errors = [];

    if (in_array($txType, ['charge', 'auth'], true)) {
        if (!isValidLuhn($cardNumber)) {
            $errors['cardNumber'] = 'Kart numarası geçerli görünmüyor.';
        }
        if (parseExpiry($expiry) === null) {
            $errors['expiry'] = 'Son kullanma tarihi MMYY formatında ve geçerli olmalı.';
        }
        $cvvDigits = normalizeDigits($cvv);
        if (!preg_match('/^\d{3,4}$/', $cvvDigits)) {
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

    if ($errors !== []) {
        jsonResponse([
            'ok' => false,
            'message' => 'Doğrulama hatası.',
            'errors' => $errors,
        ], 422);
    }

    $amount = $amountRaw !== '' ? number_format((float) $amountRaw, 2, '.', '') : null;
    $seed = implode('|', [
        $txType,
        normalizeDigits($cardNumber),
        $amount ?? '0.00',
        $referenceNo,
        $invoice,
        (new DateTimeImmutable())->format('YmdHi'),
    ]);
    $score = abs((int) crc32($seed)) % 100;
    $approveThreshold = $txType === 'void' ? 94 : 85;
    $approved = $score < $approveThreshold;

    $declineMap = [
        '051' => 'Yetersiz bakiye',
        '054' => 'Kartın son kullanma tarihi geçmiş',
        '091' => 'Issuer/host erişilemiyor',
        '116' => 'Yetersiz fon',
    ];
    $declineCodes = array_keys($declineMap);
    $declineCode = $declineCodes[$score % count($declineCodes)];
    $responseCode = $approved ? '000' : $declineCode;
    $responseText = $approved ? 'APPROVED' : 'DECLINED - ' . $declineMap[$declineCode];
    $avsOptions = ['Y', 'N', 'A', 'U'];
    $cvvOptions = ['M', 'N', 'P', 'S'];

    jsonResponse([
        'ok' => true,
        'transaction' => [
            'type' => strtoupper($txType),
            'status' => $approved ? 'approved' : 'declined',
            'responseCode' => $responseCode,
            'responseText' => $responseText,
            'authCode' => $approved ? strtoupper(substr(hash('sha256', $seed), 0, 6)) : null,
            'referenceNo' => 'TSYS-' . (new DateTimeImmutable())->format('Ymd-His') . '-' . strtoupper(substr(hash('sha1', $seed), 0, 5)),
            'maskedCard' => $cardNumber !== '' ? maskCard($cardNumber) : null,
            'amount' => $amount,
            'currency' => 'USD',
            'invoice' => $invoice ?: null,
            'zipCode' => $zipCode ?: null,
            'originalReference' => $referenceNo ?: null,
            'avsResult' => $avsOptions[$score % count($avsOptions)],
            'cvvResult' => $cvvOptions[$score % count($cvvOptions)],
            'timestamp' => (new DateTimeImmutable())->format(DATE_ATOM),
            'mode' => 'TEST MODE (sandbox)',
            'host' => 'TSYS Virtual Host',
        ],
    ]);
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
        <button class="prod-switch" type="button">Switch to Production</button>
        <strong>TEST MODE (sandbox)</strong>
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
