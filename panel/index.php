<?php

declare(strict_types=1);

session_start();
error_reporting(E_ALL);
ini_set('display_errors', '1');

$gatewayClassFileCandidates = [
    __DIR__ . '/../src/Gateways/TsysVirtualTerminalGateway.php', // repo structure
    __DIR__ . '/src/Gateways/TsysVirtualTerminalGateway.php',    // htdocs root structure
];

$gatewayClassFile = null;
foreach ($gatewayClassFileCandidates as $candidate) {
    if (is_file($candidate)) {
        $gatewayClassFile = $candidate;
        break;
    }
}

if ($gatewayClassFile === null) {
    http_response_code(500);
    echo 'TsysVirtualTerminalGateway.php bulunamadi. ';
    echo 'Beklenen konumlardan birine dosyayi yerlestirin: ';
    echo implode(' | ', $gatewayClassFileCandidates);
    exit;
}

require_once $gatewayClassFile;

try {
    $gateway = new TsysVirtualTerminalGateway();
    $gatewayInfo = $gateway->getGatewayInfo();
    $virtualTerminal = $gateway->createVirtualTerminal();
} catch (Throwable $e) {
    http_response_code(500);
    echo 'Gateway baslatilamadi: ' . $e->getMessage();
    exit;
}

if (!isset($_SESSION['transactions'])) {
    $_SESSION['transactions'] = [];
}

if (!isset($_SESSION['flash'])) {
    $_SESSION['flash'] = null;
}

/**
 * Creates a flash message for the panel UI.
 */
function setFlash(string $type, string $message): void
{
    $_SESSION['flash'] = [
        'type' => $type,
        'message' => $message,
    ];
}

/**
 * Returns and clears current flash message.
 */
function consumeFlash(): ?array
{
    $flash = $_SESSION['flash'];
    $_SESSION['flash'] = null;

    return $flash;
}

/**
 * Sanitizes user input.
 */
function cleanString(string $value): string
{
    return trim($value);
}

/**
 * Converts decimal amount to cents.
 */
function toCents(string $amount): int
{
    return (int) round(((float) $amount) * 100);
}

/**
 * Converts cents to decimal amount string.
 */
function fromCents(int $amount): string
{
    return number_format($amount / 100, 2, '.', '');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action === 'payment') {
        $cardHolder = cleanString($_POST['card_holder_name'] ?? '');
        $cardNumber = preg_replace('/\D+/', '', $_POST['card_number'] ?? '');
        $expiryMonth = cleanString($_POST['expiry_month'] ?? '');
        $expiryYear = cleanString($_POST['expiry_year'] ?? '');
        $cvv = preg_replace('/\D+/', '', $_POST['cvv'] ?? '');
        $amountInput = cleanString($_POST['amount'] ?? '');
        $currency = strtoupper(cleanString($_POST['currency'] ?? 'USD'));

        if (
            $cardHolder === '' ||
            strlen($cardNumber) < 12 ||
            strlen($expiryMonth) !== 2 ||
            strlen($expiryYear) !== 4 ||
            strlen($cvv) < 3 ||
            !is_numeric($amountInput) ||
            (float) $amountInput <= 0
        ) {
            setFlash('error', 'Odeme alinamadi: Lutfen gecerli kart ve tutar bilgisi girin.');
        } else {
            $transactionId = 'txn_' . strtoupper(bin2hex(random_bytes(6)));
            $amountCents = toCents($amountInput);

            $_SESSION['transactions'][$transactionId] = [
                'transaction_id' => $transactionId,
                'type' => 'payment',
                'status' => 'approved',
                'amount_cents' => $amountCents,
                'refunded_cents' => 0,
                'currency' => $currency,
                'card_holder_name' => $cardHolder,
                'masked_card' => '**** **** **** ' . substr($cardNumber, -4),
                'created_at' => date('Y-m-d H:i:s'),
            ];

            setFlash('success', sprintf('Odeme alindi. Islem no: %s', $transactionId));
        }
    }

    if ($action === 'refund') {
        $transactionId = cleanString($_POST['transaction_id'] ?? '');
        $refundAmountInput = cleanString($_POST['refund_amount'] ?? '');

        if (
            $transactionId === '' ||
            !isset($_SESSION['transactions'][$transactionId]) ||
            !is_numeric($refundAmountInput) ||
            (float) $refundAmountInput <= 0
        ) {
            setFlash('error', 'Iade yapilamadi: Islem no veya tutar gecersiz.');
        } else {
            $transaction = $_SESSION['transactions'][$transactionId];
            $refundCents = toCents($refundAmountInput);
            $availableCents = $transaction['amount_cents'] - $transaction['refunded_cents'];

            if ($refundCents > $availableCents) {
                setFlash('error', 'Iade tutari, kalan odeme tutarindan buyuk olamaz.');
            } else {
                $_SESSION['transactions'][$transactionId]['refunded_cents'] += $refundCents;
                $isFullyRefunded = $_SESSION['transactions'][$transactionId]['refunded_cents'] >= $_SESSION['transactions'][$transactionId]['amount_cents'];
                $_SESSION['transactions'][$transactionId]['status'] = $isFullyRefunded ? 'refunded' : 'partially_refunded';

                setFlash(
                    'success',
                    sprintf(
                        'Iade basarili. Islem no: %s, iade tutari: %s %s',
                        $transactionId,
                        fromCents($refundCents),
                        $transaction['currency']
                    )
                );
            }
        }
    }

    header('Location: ' . $_SERVER['PHP_SELF']);
    exit;
}

$flash = consumeFlash();
$transactions = array_values($_SESSION['transactions']);
usort(
    $transactions,
    static function (array $a, array $b): int {
        return strcmp($b['created_at'], $a['created_at']);
    }
);
?>
<!doctype html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TSYS Virtual Terminal Panel</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
        }
        .container {
            max-width: 1100px;
            margin: 24px auto;
            padding: 0 16px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 16px;
        }
        .card {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            padding: 16px;
        }
        h1, h2 {
            margin-top: 0;
        }
        .meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 8px;
            font-size: 14px;
        }
        .meta div {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 8px;
        }
        form {
            display: grid;
            gap: 8px;
        }
        label {
            font-size: 13px;
            font-weight: 600;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #d1d5db;
            box-sizing: border-box;
        }
        button {
            background: #0f766e;
            color: #fff;
            border: none;
            cursor: pointer;
            font-weight: 700;
        }
        button:hover {
            background: #0d665f;
        }
        .flash {
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 8px;
            font-weight: 600;
        }
        .flash.success {
            background: #dcfce7;
            color: #166534;
        }
        .flash.error {
            background: #fee2e2;
            color: #991b1b;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            border-bottom: 1px solid #e5e7eb;
            padding: 10px 8px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background: #f8fafc;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>TSYS Virtual Terminal Panel</h1>
    <?php if ($flash !== null): ?>
        <div class="flash <?= htmlspecialchars($flash['type'], ENT_QUOTES, 'UTF-8') ?>">
            <?= htmlspecialchars($flash['message'], ENT_QUOTES, 'UTF-8') ?>
        </div>
    <?php endif; ?>

    <div class="card" style="margin-bottom:16px;">
        <h2>Terminal Bilgileri</h2>
        <div class="meta">
            <div><strong>DBA</strong><br><?= htmlspecialchars($gatewayInfo['business']['dba'], ENT_QUOTES, 'UTF-8') ?></div>
            <div><strong>Merchant No</strong><br><?= htmlspecialchars($gatewayInfo['merchant_profile']['merchant_number'], ENT_QUOTES, 'UTF-8') ?></div>
            <div><strong>Store No</strong><br><?= htmlspecialchars($gatewayInfo['merchant_profile']['store_number'], ENT_QUOTES, 'UTF-8') ?></div>
            <div><strong>Terminal No</strong><br><?= htmlspecialchars($gatewayInfo['merchant_profile']['terminal_number'], ENT_QUOTES, 'UTF-8') ?></div>
            <div><strong>Virtual Terminal</strong><br><?= htmlspecialchars($virtualTerminal['virtual_terminal']['status'], ENT_QUOTES, 'UTF-8') ?></div>
            <div><strong>Iade Durumu</strong><br><?= htmlspecialchars($virtualTerminal['return']['status'], ENT_QUOTES, 'UTF-8') ?></div>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Kart ile Odeme Al</h2>
            <form method="post">
                <input type="hidden" name="action" value="payment">
                <div>
                    <label for="card_holder_name">Kart Uzerindeki Isim</label>
                    <input id="card_holder_name" name="card_holder_name" required>
                </div>
                <div>
                    <label for="card_number">Kart Numarasi</label>
                    <input id="card_number" name="card_number" inputmode="numeric" placeholder="4111111111111111" required>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
                    <div>
                        <label for="expiry_month">Ay (MM)</label>
                        <input id="expiry_month" name="expiry_month" placeholder="12" required>
                    </div>
                    <div>
                        <label for="expiry_year">Yil (YYYY)</label>
                        <input id="expiry_year" name="expiry_year" placeholder="2030" required>
                    </div>
                    <div>
                        <label for="cvv">CVV</label>
                        <input id="cvv" name="cvv" inputmode="numeric" placeholder="123" required>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                    <div>
                        <label for="amount">Tutar</label>
                        <input id="amount" name="amount" type="number" min="0.01" step="0.01" required>
                    </div>
                    <div>
                        <label for="currency">Para Birimi</label>
                        <select id="currency" name="currency">
                            <?php foreach ($gatewayInfo['supported_currencies'] as $currency): ?>
                                <option value="<?= htmlspecialchars($currency, ENT_QUOTES, 'UTF-8') ?>" <?= $currency === 'USD' ? 'selected' : '' ?>>
                                    <?= htmlspecialchars($currency, ENT_QUOTES, 'UTF-8') ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                </div>
                <button type="submit">Odeme Al</button>
            </form>
        </div>

        <div class="card">
            <h2>Iade Yap</h2>
            <form method="post">
                <input type="hidden" name="action" value="refund">
                <div>
                    <label for="transaction_id">Islem No</label>
                    <input id="transaction_id" name="transaction_id" placeholder="txn_ABC123..." required>
                </div>
                <div>
                    <label for="refund_amount">Iade Tutari</label>
                    <input id="refund_amount" name="refund_amount" type="number" min="0.01" step="0.01" required>
                </div>
                <button type="submit">Iade Gerceklestir</button>
            </form>
        </div>
    </div>

    <div class="card">
        <h2>Islem Gecmisi</h2>
        <table>
            <thead>
            <tr>
                <th>Tarih</th>
                <th>Islem No</th>
                <th>Kart</th>
                <th>Tutar</th>
                <th>Iade Edilen</th>
                <th>Durum</th>
            </tr>
            </thead>
            <tbody>
            <?php if ($transactions === []): ?>
                <tr>
                    <td colspan="6">Henuz islem yok.</td>
                </tr>
            <?php else: ?>
                <?php foreach ($transactions as $txn): ?>
                    <tr>
                        <td><?= htmlspecialchars($txn['created_at'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($txn['transaction_id'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($txn['masked_card'], ENT_QUOTES, 'UTF-8') ?><br><small><?= htmlspecialchars($txn['card_holder_name'], ENT_QUOTES, 'UTF-8') ?></small></td>
                        <td><?= htmlspecialchars(fromCents($txn['amount_cents']) . ' ' . $txn['currency'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars(fromCents($txn['refunded_cents']) . ' ' . $txn['currency'], ENT_QUOTES, 'UTF-8') ?></td>
                        <td><?= htmlspecialchars($txn['status'], ENT_QUOTES, 'UTF-8') ?></td>
                    </tr>
                <?php endforeach; ?>
            <?php endif; ?>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
