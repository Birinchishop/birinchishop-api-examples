# Birinchi Shop Partner API — examples

Code examples for the **[Birinchi Shop](https://birinchishop.uz) Partner API**: a COD (cash on delivery) affiliate network in Uzbekistan.
Partners (affiliates, targetologists, media buyers) promote ready products; the network runs the call center, warehouse and nationwide delivery,
and pays a fixed amount for every **delivered** order.

- Human docs: https://birinchishop.uz/api/v1/docs
- Guide for AI assistants (give it to Claude / ChatGPT / Cursor): https://birinchishop.uz/api/v1/guide.md
- OpenAPI spec: https://birinchishop.uz/api/v1/openapi.json (a copy is in [`openapi.json`](openapi.json))
- Base URL: `https://birinchishop.uz/api/v1`

> **O'zbekcha:** bu repo — Birinchi Shop hamkorlik API'si uchun tayyor kod misollari (lid yuborish, zakaz holatlari, webhook imzosini tekshirish, Keitaro/Binom postback, Postman kolleksiyasi, MCP). Rasmiy kutubxonalar: `npm install birinchishop`, `pip install birinchishop`.
> API kaliti panelda yaratiladi (Dashboard → API). Kalitni hech qachon kodga yoki ochiq repoga yozmang — faqat serveringizdagi `.env` da.
>
> **Русский:** примеры кода для партнёрского API Birinchi Shop — CPA-сети по товарке (COD) в Узбекистане: отправка лидов, статусы заказов, проверка подписи вебхука, постбэк в Keitaro/Binom, MCP для ИИ-агентов.

## Contents

| Folder | What it shows |
|---|---|
| [`examples/curl.sh`](examples/curl.sh) | Read-only requests: account, offers, orders |
| [`examples/node`](examples/node), [`examples/python`](examples/python), [`examples/php`](examples/php) | Listing offers; submitting an order with an `Idempotency-Key` |
| [`webhook-verify`](webhook-verify) | Receiving signed JSON webhooks and verifying `X-Birinchishop-Signature` (Node, Python, PHP) |
| [`integrations/keitaro.md`](integrations/keitaro.md), [`integrations/binom.md`](integrations/binom.md) | S2S postback to Keitaro / Binom with `{click_id}`, status mapping |
| [`postman`](postman) | Postman collection (every endpoint, example responses) and environment |
| [`mcp`](mcp) | Connecting the Birinchi Shop MCP server to Claude, ChatGPT, Cursor |
| [`a2a`](a2a) | Read-only A2A (Agent2Agent) client for the public store agent: Agent Card, `SendMessage`, product search (Node, Python) |

## Official SDKs

| Language | Install | Source |
|---|---|---|
| Node.js 18+ (ESM + CommonJS, TypeScript types, no dependencies) | `npm install birinchishop` | [Birinchishop/birinchishop-node](https://github.com/Birinchishop/birinchishop-node) |
| Python 3.8+ (standard library only, typed) | `pip install birinchishop` | [Birinchishop/birinchishop-python](https://github.com/Birinchishop/birinchishop-python) |

Both cover every REST endpoint, retry `429`/`5xx` safely, page through lists, and verify webhook signatures:

```js
import Birinchishop from 'birinchishop';
const bs = new Birinchishop({ apiKey: process.env.BSK_KEY });
const { data: offers } = await bs.listOffers({ sort: 'best_selling', min_sale_rate: 25 });
```

```python
from birinchishop import Birinchishop
bs = Birinchishop()  # reads BSK_KEY
offers = bs.list_offers(sort="best_selling", min_sale_rate=25)["data"]
```

## Postman

Import [`postman/birinchishop-api-v1.postman_collection.json`](postman/birinchishop-api-v1.postman_collection.json) and
[`postman/birinchishop-api-v1.postman_environment.json`](postman/birinchishop-api-v1.postman_environment.json),
select the **Birinchi Shop API** environment and paste your key into `bsk_key` (a secret variable — never export or share it filled in).
Every request has an example response. `POST /orders` creates a **real** order: `customer_phone` is empty on purpose.
The collection is generated from `openapi.json` by [`postman/build_collection.py`](postman/build_collection.py).

## Authentication

```http
Authorization: Bearer bsk_live_<id>_<secret>
```

Create a key in the partner panel (**Dashboard → API**) with only the scopes you need, an optional IP allowlist and an expiry date.
The key is a **server-side secret**: read it from an environment variable (see [`.env.example`](.env.example)); never put it in browser JavaScript, a mobile app, a URL or a public repository.

## Rules that matter

- `POST /orders` creates a **real order** — a call center phones the customer. Never send test, sample or fake orders: the account gets blocked. The examples refuse to run unless you set `CONFIRM_REAL_ORDER=yes`.
- Submitting orders via API needs the `orders:write` scope and an account with at least 3 delivered orders (or admin approval).
- Always send an `Idempotency-Key` so a retry never creates a duplicate.
- Branch on `error.code`, never on `error.message`.
- Money is integer UZS; customer phone numbers in responses are always masked.
- One phone number cannot order the same offer twice within 24 hours.
- The payout is earned only when an order is **delivered** (`conversion_status = sale`).

## Status model

| `status` | `conversion_status` |
|---|---|
| `new`, `processing`, `callback` | `lead` |
| `confirmed`, `packed`, `shipping` | `approved` |
| `delivered` | `sale` (payout earned) |
| `returned`, `cancelled` | `rejected` |

## Start as a partner

Registration is free: https://birinchishop.uz/register?utm_source=github&utm_campaign=api-examples
Never pay anyone for "registration" or "activation" — see https://birinchishop.uz/xavfsizlik

## License

Examples are MIT-licensed (see [`LICENSE`](LICENSE)). Using the API itself is subject to the partner agreement on birinchishop.uz.
