// Node.js 18+ (built-in fetch). Read-only A2A client for the Birinchi Shop store agent.
// Run: node shop-search.mjs "soat"        (no API key needed; the store agent is public)
// Flow: fetch the Agent Card -> pick the JSON-RPC interface -> SendMessage -> read the Task artifact.
// This example only searches the catalog. It never calls the place_order skill (a real order is phoned by a call center).
const ORIGIN = 'https://birinchishop.uz';
const query = process.argv[2] || 'soat';

// 1. Discover the agent.
const card = await (await fetch(`${ORIGIN}/.well-known/agent-card.json`)).json();
const iface = card.supportedInterfaces.find((i) => i.protocolBinding === 'JSONRPC' && i.protocolVersion === '1.0');
if (!iface) throw new Error('No A2A 1.0 JSON-RPC interface in the Agent Card');
console.log(`Agent: ${card.name} v${card.version}; skills: ${card.skills.map((s) => s.id).join(', ')}`);

// 2. Send a message. A data part names the skill explicitly (plain text would also be read as a search query).
const res = await fetch(iface.url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'A2A-Version': '1.0' },
  body: JSON.stringify({
    jsonrpc: '2.0',
    id: 1,
    method: 'SendMessage',
    params: {
      message: {
        messageId: crypto.randomUUID(),
        role: 'ROLE_USER',
        parts: [{ data: { skill: 'search_products', arguments: { query, limit: 5 } } }],
      },
    },
  }),
});
const body = await res.json();
if (body.error) throw new Error(`A2A error ${body.error.code}: ${body.error.message}`);

// 3. Read the result: the search is synchronous, so the Task is already completed.
const task = body.result.task;
console.log(`Task ${task.id}: ${task.status.state}`);
for (const artifact of task.artifacts ?? []) {
  for (const part of artifact.parts) {
    if (part.text) console.log(part.text);
  }
  const data = artifact.parts.find((p) => p.data)?.data;
  if (data?.items) console.log(`(${data.items.length} structured items, total ${data.total})`);
}
