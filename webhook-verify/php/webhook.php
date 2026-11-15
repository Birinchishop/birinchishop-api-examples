<?php
// Minimal webhook receiver (PHP 7.4+). Verifies X-Birinchishop-Signature,
// rejects signatures older than 5 minutes. Deduplicate events by `id` in your database.

function bsk_verify(string $raw, string $header, string $secret, ?int $now = null): bool {
    $parts = [];
    foreach (explode(',', $header) as $p) {
        $kv = explode('=', $p, 2);
        if (count($kv) === 2) { $parts[$kv[0]] = $kv[1]; }
    }
    $now = $now ?? time();
    if (!isset($parts['t']) || abs($now - (int)$parts['t']) > 300) { return false; }
    $expected = hash_hmac('sha256', $parts['t'] . '.' . $raw, $secret);
    return hash_equals($expected, $parts['v1'] ?? '');
}

if (PHP_SAPI !== 'cli') {
    $raw = file_get_contents('php://input');
    $header = $_SERVER['HTTP_X_BIRINCHISHOP_SIGNATURE'] ?? '';
    if (!bsk_verify($raw, $header, getenv('BSK_WEBHOOK_SECRET') ?: '')) { http_response_code(401); exit; }
    http_response_code(200);
    $evt = json_decode($raw, true);
    error_log($evt['type'] . ' order ' . $evt['data']['order_id'] . ' ' . $evt['data']['status']);
}
