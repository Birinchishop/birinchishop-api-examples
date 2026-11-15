<?php
// Submits a REAL order: the call center will phone this customer.
// Use only with a real customer who agreed to order. Test or fake orders get the account blocked.
// Run: BSK_KEY=... CONFIRM_REAL_ORDER=yes php submit_order.php <link_id> <+998XXXXXXXXX> [name]

$key = getenv('BSK_KEY');
if (!$key || $argc < 3) { fwrite(STDERR, "Usage: php submit_order.php <link_id> <phone> [name]\n"); exit(1); }
if (getenv('CONFIRM_REAL_ORDER') !== 'yes') { fwrite(STDERR, "This creates a REAL order. Set CONFIRM_REAL_ORDER=yes.\n"); exit(1); }

$payload = ['link_id' => (int)$argv[1], 'phone' => $argv[2]];
if ($argc > 3) { $payload['name'] = $argv[3]; }

$ch = curl_init('https://birinchishop.uz/api/v1/orders');
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTPHEADER => [
        'Authorization: Bearer ' . $key,
        'Content-Type: application/json',
        'Idempotency-Key: ' . bin2hex(random_bytes(16)), // reuse the same key when retrying
    ],
    CURLOPT_POSTFIELDS => json_encode($payload),
]);
$raw = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

$body = json_decode($raw, true);
if ($code >= 300) {
    fwrite(STDERR, $code . ' ' . ($body['error']['code'] ?? '') . ': ' . ($body['error']['message'] ?? '') . "\n");
    exit(1);
}
echo 'Order created: ' . $body['data']['id'] . ' ' . $body['data']['status'] . "\n";
