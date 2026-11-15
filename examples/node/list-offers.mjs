// Node.js 18+ (built-in fetch). Read-only: lists offers worth promoting.
// Run: BSK_KEY=... node list-offers.mjs
const API = 'https://birinchishop.uz/api/v1';
const KEY = process.env.BSK_KEY;
if (!KEY) throw new Error('Set BSK_KEY (server-side secret, never in browser code)');

const res = await fetch(`${API}/offers?sort=best_selling&in_stock_only=true&min_sale_rate=25&limit=10`, {
  headers: { Authorization: `Bearer ${KEY}` },
});
const body = await res.json();
if (!res.ok) throw new Error(`${res.status} ${body.error?.code}: ${body.error?.message}`);

for (const o of body.data) {
  console.log(`#${o.id} ${o.name} — payout ${o.payout} UZS, sale rate ${o.sale_rate_percent ?? 'n/a'}%`);
}
