# A2A (Agent2Agent) examples

Birinchi Shop runs a public, key-less **store agent** that speaks the [A2A protocol](https://a2a-protocol.org/latest/specification/) (v1.0; 0.3 clients also work).

- Agent Card: https://birinchishop.uz/.well-known/agent-card.json
- JSON-RPC endpoint: `POST https://birinchishop.uz/api/a2a/shop` (send the header `A2A-Version: 1.0`)
- Skills: `search_products`, `get_product`, `get_order_status`, `store_info`, `place_order`

| File | What it does |
|---|---|
| [`node/shop-search.mjs`](node/shop-search.mjs) | Node 18+: fetch the card, `SendMessage` with a `search_products` skill call, print the Task result |
| [`python/shop_search.py`](python/shop_search.py) | Same in Python 3.8+ (standard library only) |

```bash
node a2a/node/shop-search.mjs "soat"
python a2a/python/shop_search.py "soat"
```

Both examples are **read-only**: they never call `place_order`. Placing an order creates a real order that a call center phones, so only do it with a real shopper's explicit confirmation (the agent also answers `TASK_STATE_INPUT_REQUIRED` until the shopper confirms).

Notes:
- The agent is deterministic (no LLM). Send a data part `{"skill": "<id>", "arguments": {...}}`; plain text is treated as a product search.
- Send a `User-Agent` header (the default `Python-urllib` one is blocked by the CDN).
- Tasks live in memory for about an hour; streaming and push notifications are not supported.
