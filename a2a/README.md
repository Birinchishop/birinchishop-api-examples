# A2A (Agent2Agent) examples

Birinchi Shop runs two agents that speak the [A2A protocol](https://a2a-protocol.org/latest/specification/) (v1.0; 0.3 clients also work): a public **store agent** for shoppers and a **partner agent** for affiliates.

## Store agent (public, no key)

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

## Partner agent (affiliates, API key)

The same Partner API as REST and MCP, exposed as A2A skills: same scopes, limits and test-mode sandbox.

- Agent Card: https://birinchishop.uz/api/a2a/partner/agent-card.json (public)
- JSON-RPC endpoint: `POST https://birinchishop.uz/api/a2a/partner` with `Authorization: Bearer <key>` and `A2A-Version: 1.0`
- Auth: an API key from the partner panel (API section), or an OAuth access token
- Skills: `get_account`, `search_offers`, `get_offer`, `list_links`, `list_orders`, `get_order`, `get_stats`, `list_events` (read) and `create_link`, `create_order` (write scopes)

| File | What it does |
|---|---|
| [`node/partner-offers.mjs`](node/partner-offers.mjs) | Node 18+: fetch the card, call `get_account`, then `search_offers`, print price / payout / sale rate |
| [`python/partner_offers.py`](python/partner_offers.py) | Same in Python 3.8+ (standard library only) |

```bash
export BIRINCHISHOP_API_KEY=bsk_test_...   # a test key reads real offers but never creates anything
node a2a/node/partner-offers.mjs "soat"
python a2a/python/partner_offers.py "soat"
```

Both examples are **read-only**: they never call `create_link` or `create_order`. `create_order` with a live key submits a real order that a call center phones; never send invented or test orders with a live key. Every partner skill completes in one step (there is no multi-turn task).

## Notes

- Both agents are deterministic (no LLM). Send a data part `{"skill": "<id>", "arguments": {...}}`; plain text is treated as a product search.
- Send a `User-Agent` header (the default `Python-urllib` one is blocked by the CDN).
- Tasks live in memory for about an hour; streaming and push notifications are not supported.
