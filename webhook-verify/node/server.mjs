// Minimal webhook receiver (Node.js 18+, no dependencies).
// Verifies X-Birinchishop-Signature: t=<unix>,v1=<hex HMAC-SHA256(secret, "<t>.<raw body>")>
// and rejects signatures older than 5 minutes. Deduplicate events by `id` in your storage.
// Run: BSK_WEBHOOK_SECRET=... node server.mjs   (put it behind HTTPS)
import http from 'node:http';
import crypto from 'node:crypto';

const SECRET = process.env.BSK_WEBHOOK_SECRET;
if (!SECRET) throw new Error('Set BSK_WEBHOOK_SECRET');

export function verify(rawBody, header, secret, nowSec = Date.now() / 1000) {
  if (!header) return false;
  const parts = Object.fromEntries(header.split(',').map((p) => p.split('=')));
  if (!parts.t || Math.abs(nowSec - Number(parts.t)) > 300) return false;
  const expected = crypto.createHmac('sha256', secret).update(`${parts.t}.${rawBody}`).digest('hex');
  const a = Buffer.from(expected), b = Buffer.from(parts.v1 || '');
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const seen = new Set(); // use a database table in production

http.createServer((req, res) => {
  if (req.method !== 'POST') { res.writeHead(405).end(); return; }
  let raw = '';
  req.on('data', (c) => { raw += c; if (raw.length > 1e6) req.destroy(); });
  req.on('end', () => {
    if (!verify(raw, req.headers['x-birinchishop-signature'], SECRET)) { res.writeHead(401).end(); return; }
    const evt = JSON.parse(raw);
    res.writeHead(200).end('ok'); // answer within 10 s, do slow work after
    if (seen.has(evt.id)) return;
    seen.add(evt.id);
    const o = evt.data.order;
    console.log(evt.type, 'order', evt.data.order_id, evt.data.status, evt.data.conversion_status, o?.tracking?.click_id ?? '');
  });
}).listen(process.env.PORT || 8080);
