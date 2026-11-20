// Node.js 18+ (built-in fetch). Read-only A2A client for the Birinchi Shop PARTNER agent.
// Run: BIRINCHISHOP_API_KEY=bsk_test_... node partner-offers.mjs "soat"
// Flow: fetch the Agent Card -> pick the JSON-RPC interface -> SendMessage (get_account, then search_offers).
// The key comes from the partner panel (API section). A test key (bsk_test_...) is the safe way to try this:
// it reads real offers but never creates anything. This example never calls create_link or create_order.
const ORIGIN = 'https://birinchishop.uz';
const KEY = process.env.BIRINCHISHOP_API_KEY;
if (!KEY) throw new Error('Set BIRINCHISHOP_API_KEY (bsk_test_... or bsk_live_...)');
const query = process.argv[2] || 'soat';

// 1. Discover the agent. The card is public; every other call needs the key.
const card = await (await fetch(`${ORIGIN}/api/a2a/partner/agent-card.json`)).json();
const iface = card.supportedInterfaces.find((i) => i.protocolBinding === 'JSONRPC' && i.protocolVersion === '1.0');
if (!iface) throw new Error('No A2A 1.0 JSON-RPC interface in the Agent Card');
console.log(`Agent: ${card.name} v${card.version}; skills: ${card.skills.map((s) => s.id).join(', ')}`);

// 2. One skill call = one message with a data part {"skill", "arguments"}. Every skill completes in one step.
let rpcId = 0;
async function call(skill, args = {}) {
  const res = await fetch(iface.url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'A2A-Version': '1.0', Authorization: `Bearer ${KEY}` },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: ++rpcId,
      method: 'SendMessage',
      params: {
        message: { messageId: crypto.randomUUID(), role: 'ROLE_USER', parts: [{ data: { skill, arguments: args } }] },
      },
    }),
  });
  const body = await res.json();
  if (body.error) throw new Error(`A2A error ${body.error.code}: ${body.error.message}`);
  const task = body.result.task;
  if (task.status.state !== 'TASK_STATE_COMPLETED') {
    const why = task.status.message?.parts?.map((p) => p.text).filter(Boolean).join(' ');
    throw new Error(`${skill}: ${task.status.state}${why ? ` (${why})` : ''}`);
  }
  // The artifact carries a text part (human-readable) and a data part (the same JSON the REST API returns).
  return task.artifacts[0].parts.find((p) => p.data).data;
}

// 3. Who am I, then which offers match the query.
const account = await call('get_account');
console.log('Account:', JSON.stringify(account).slice(0, 300));

const offers = await call('search_offers', { search: query, limit: 5 });
for (const o of offers.data ?? []) {
  const rate = o.sale_rate_percent == null ? 'no data yet' : `${o.sale_rate_percent}%`;
  console.log(`#${o.id} ${o.name} | price ${o.customer_price} UZS | payout ${o.payout} UZS | sale rate ${rate}`);
}
