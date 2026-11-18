# Binom: S2S postback

Send every Birinchi Shop order status to Binom so conversions land on the right click.
See also: [Keitaro](keitaro.md).

## 1. Tracking link (offer URL in Binom)

Create a link for an offer (`POST /links`, scope `links:write`) or take an existing one (`GET /offers/{offer_id}` → `my_links`).
Each link has a `tracking_url_template`:

```
https://birinchishop.uz/l/<your-link>?click_id={click_id}&sub1={sub1}&sub2={sub2}&sub3={sub3}&sub4={sub4}&sub5={sub5}
```

Binom's click ID token is `{clickid}`. Put it into `click_id`, use other Binom tokens for `sub1`…`sub5` if you need them,
and drop the parameters you do not use:

```
https://birinchishop.uz/l/<your-link>?click_id={clickid}&sub1=<binom token>
```

Add this URL as the offer URL in Binom. `click_id` and `sub1`…`sub5` (max 255 characters each) are stored on the order,
returned in `GET /orders` (`tracking`), searchable with `GET /orders?click_id=...`, and substituted into the postback.

> SDK helper: `fillTrackingUrl(link.tracking_url_template, { click_id: '{clickid}' })` (Node) /
> `fill_tracking_url(template, click_id="{clickid}")` (Python).

If you send orders yourself with `POST /orders`, pass `click_id` and `sub1`…`sub5` in the request body instead.

## 2. Postback URL

Take your Binom postback address (your tracker domain plus `/click`, or `/click.php` on older installs — see the postback URL in your Binom)
and register it with `POST /webhooks` (scope `webhooks:manage`):

```bash
curl -s https://birinchishop.uz/api/v1/webhooks \
  -H "Authorization: Bearer $BSK_KEY" -H "Content-Type: application/json" \
  -d '{
    "kind": "postback",
    "description": "Binom",
    "url": "https://binom.example.com/click?cnv_id={click_id}&payout={payout}&cnv_status={conversion_status}&cnv_status2={status}&cnv_currency={currency}"
  }'
```

| Binom parameter | Our macro | Notes |
|---|---|---|
| `cnv_id` | `{click_id}` | Required — the `{clickid}` Binom put into the tracking link |
| `payout` | `{payout}` | Partner payout for the order, UZS |
| `cnv_status` | `{conversion_status}` | `lead` / `approved` / `sale` / `rejected` |
| `cnv_status2` | `{status}` | Detailed status (optional, useful for reports) |
| `cnv_currency` | `{currency}` | Always `UZS` |

Important:

- Binom stores the status text as sent. Build reports or filters on `cnv_status = sale` to see earned money.
- `{payout}` is the order's payout in **every** postback, including `lead` and `rejected`. Binom replaces a click's payout with the
  one from the latest postback, so a lead already shows the payout before delivery. Count revenue only for `sale`
  (for example with Binom's status-based payout settings, or by filtering reports on `cnv_status`).
- Do not turn on Binom's *Upsell* option for this offer: it sums payouts of repeated postbacks for the same click,
  and we send one postback per status change.

## 3. Status mapping

| `status` (`{status}`) | `conversion_status` (`{cnv_status}`) | Meaning |
|---|---|---|
| `new`, `processing`, `callback` | `lead` | Order received, call center has not confirmed yet |
| `confirmed`, `packed`, `shipping` | `approved` | Customer confirmed, not delivered yet (hold) |
| `delivered` | `sale` | Customer received and paid — payout earned |
| `returned`, `cancelled` | `rejected` | No payout |

An order can move back (for example `delivered` → `returned`); the next postback brings the new status.

All macros we can substitute: `{click_id}` `{sub1}`…`{sub5}` `{order_id}` `{external_id}` `{status}` `{conversion_status}`
`{payout}` `{customer_price}` `{currency}` `{offer_id}` `{link_id}` `{event}` `{event_id}` `{timestamp}` —
see the table in [keitaro.md](keitaro.md#3-what-we-send).

## 4. Check it

- `POST /webhooks/{id}/test` sends one sample postback now: `click_id=test_click_id`, `status=delivered`, `conversion_status=sale`,
  `payout=50000`. Binom will not find that click — that is expected; it shows the URL is reachable.
- `GET /webhooks/{id}/deliveries` shows recent attempts with the response code.
- Your tracker must answer 2xx within 10 seconds; failed calls are retried (1m, 5m, 15m, 1h, 3h, 6h, 12h, 24h).
  A webhook that keeps failing is switched off; turn it back on with `PATCH /webhooks/{id}` and `{"is_active": true}`.
- Only public `http(s)` URLs on ports 80/443/8080/8443 are accepted.

A postback to Binom does not reach Meta by itself. If you buy Meta traffic through a tracker, forward `sale` from the tracker to Meta.
