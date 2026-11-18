# Keitaro: S2S postback

Send every Birinchi Shop order status to Keitaro so conversions land on the right click.
See also: [Binom](binom.md). Other trackers (Voluum, RedTrack…) work the same way: pass `click_id` in, get it back in the postback.

## 1. Tracking link (offer URL in Keitaro)

Create a link for an offer (`POST /links`, scope `links:write`) or take an existing one (`GET /offers/{offer_id}` → `my_links`).
Each link has a `tracking_url_template`:

```
https://birinchishop.uz/l/<your-link>?click_id={click_id}&sub1={sub1}&sub2={sub2}&sub3={sub3}&sub4={sub4}&sub5={sub5}
```

Replace the right-hand side with **Keitaro** macros and drop the parameters you do not use. Keitaro's click ID macro is `{subid}`:

```
https://birinchishop.uz/l/<your-link>?click_id={subid}&sub1={campaign_id}
```

Add this URL as the offer URL in Keitaro. `click_id` and `sub1`…`sub5` (max 255 characters each) are stored on the order,
returned in `GET /orders` (`tracking`), searchable with `GET /orders?click_id=...`, and substituted into the postback.

> SDK helper: `fillTrackingUrl(link.tracking_url_template, { click_id: '{subid}', sub1: '{campaign_id}' })` (Node) /
> `fill_tracking_url(template, click_id="{subid}", sub1="{campaign_id}")` (Python).

If you send orders yourself with `POST /orders`, pass `click_id` and `sub1`…`sub5` in the request body instead.

## 2. Postback URL

Copy your postback URL from Keitaro (**Settings → Postback URL**; it looks like `https://<keitaro-domain>/<postback-key>/postback`)
and register it with `POST /webhooks` (scope `webhooks:manage`):

```bash
curl -s https://birinchishop.uz/api/v1/webhooks \
  -H "Authorization: Bearer $BSK_KEY" -H "Content-Type: application/json" \
  -d '{
    "kind": "postback",
    "description": "Keitaro",
    "url": "https://tracker.example.com/POSTBACK_KEY/postback?subid={click_id}&status={conversion_status}&payout={payout}&currency={currency}&lead_status=lead,approved&sale_status=sale&rejected_status=rejected"
  }'
```

- `{conversion_status}` is one of `lead`, `approved`, `sale`, `rejected`. Keitaro has no "approved" conversion type, so the
  status training `lead_status=lead,approved` records it as a lead; `sale_status=sale` and `rejected_status=rejected` map the rest.
  Without status training Keitaro ignores statuses it does not know.
- Postbacks for the same click update the conversion as the order moves on (lead → sale or rejected).
  If one click can produce several orders, Keitaro's `tid` parameter (for example `&tid={order_id}`) records them as separate
  conversions — check in your Keitaro how repeated postbacks with the same `tid` are handled before relying on it.
- `{payout}` is the order's payout in UZS in **every** postback, including `lead` and `rejected`. The money is earned only on `sale`.
- `{currency}` is always `UZS`.

## 3. What we send

We call the URL with **GET** on every order event (`order.created`, `order.status_changed`), with these macros URL-encoded:

| Macro | Value |
|---|---|
| `{click_id}`, `{sub1}`…`{sub5}` | Values from the tracking link or `POST /orders` (empty if none) |
| `{order_id}` | Birinchi Shop order id |
| `{external_id}` | Your own id from `POST /orders` (empty otherwise) |
| `{status}` | Detailed status: `new`, `processing`, `callback`, `confirmed`, `packed`, `shipping`, `delivered`, `returned`, `cancelled` |
| `{conversion_status}` | `lead` / `approved` / `sale` / `rejected` |
| `{payout}` | Partner payout for the order, UZS |
| `{customer_price}` | Price paid by the customer, UZS (without delivery) |
| `{currency}` | `UZS` |
| `{offer_id}`, `{link_id}` | Ids of the offer and the link |
| `{event}` | `order.created` or `order.status_changed` |
| `{event_id}` | Event id (increasing) |
| `{timestamp}` | Event time, Unix seconds |

| `status` | `conversion_status` | Keitaro (with the status training above) |
|---|---|---|
| `new`, `processing`, `callback` | `lead` | Lead |
| `confirmed`, `packed`, `shipping` | `approved` | Lead |
| `delivered` | `sale` | Sale — payout earned |
| `returned`, `cancelled` | `rejected` | Rejected |

An order can move back (for example `delivered` → `returned`); the next postback brings the new status.

## 4. Check it

- `POST /webhooks/{id}/test` sends one sample postback now: `click_id=test_click_id`, `status=delivered`, `conversion_status=sale`,
  `payout=50000`, `event_id=0`. Keitaro will log that the click is not found — that is expected; it shows the URL is reachable.
- `GET /webhooks/{id}/deliveries` shows recent attempts with the response code.
- Your tracker must answer 2xx within 10 seconds; failed calls are retried (1m, 5m, 15m, 1h, 3h, 6h, 12h, 24h).
  A webhook that keeps failing is switched off; turn it back on with `PATCH /webhooks/{id}` and `{"is_active": true}`.
- Only public `http(s)` URLs on ports 80/443/8080/8443 are accepted.

A postback to Keitaro does not reach Meta by itself. If you buy Meta traffic through a tracker, forward `sale` from the tracker to Meta.
