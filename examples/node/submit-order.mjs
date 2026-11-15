// Node.js 18+. Submits a REAL order: the call center will phone this customer.
// Use only with a real customer who agreed to order. Test or fake orders get the account blocked.
// Requires scope orders:write (and an account with 3+ delivered orders or admin approval).
// Run: BSK_KEY=... CONFIRM_REAL_ORDER=yes node submit-order.mjs <link_id> <+998XXXXXXXXX> [name]
import crypto from 'node:crypto';

const API = 'https://birinchishop.uz/api/v1';
const KEY = process.env.BSK_KEY;
const [linkId, phone, name] = process.argv.slice(2);
if (!KEY || !linkId || !phone) throw new Error('Usage: node submit-order.mjs <link_id> <phone> [name]');
if (process.env.CONFIRM_REAL_ORDER !== 'yes') throw new Error('This creates a REAL order. Set CONFIRM_REAL_ORDER=yes to continue.');

const res = await fetch(`${API}/orders`, {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${KEY}`,
    'Content-Type': 'application/json',
    // Same key on retry => no duplicate order. Derive it from your own lead id if you have one.
    'Idempotency-Key': crypto.randomUUID(),
  },
  body: JSON.stringify({ link_id: Number(linkId), phone, name, sub1: 'my-campaign' }),
});
const body = await res.json();
if (!res.ok) {
  // Branch on error.code, not on the message (e.g. duplicate_order, orders_write_not_allowed)
  throw new Error(`${res.status} ${body.error?.code}: ${body.error?.message}`);
}
console.log('Order created:', body.data.id, body.data.status);
