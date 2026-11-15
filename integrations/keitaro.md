# S2S postback: Keitaro, Binom, Voluum

1. Create a tracking link for an offer (`POST /links`) and take its `tracking_url_template`, e.g.
   `https://birinchishop.uz/l/<link_id>?click_id={clickid}&sub1={campaign}` — use your tracker's own macro names on the right side.
2. Register a postback (`POST /webhooks`, scope `webhooks:manage`):

```bash
curl -s https://birinchishop.uz/api/v1/webhooks \
  -H "Authorization: Bearer $BSK_KEY" -H "Content-Type: application/json" \
  -d '{"kind":"postback","url":"https://tracker.example.com/postback?subid={click_id}&status={conversion_status}&payout={payout}&currency={currency}"}'
```

We call your URL with **GET** on every order event and replace these macros (URL-encoded):

`{click_id}` `{sub1}`…`{sub5}` `{order_id}` `{external_id}` `{status}` `{conversion_status}` `{payout}` `{customer_price}` `{currency}` `{offer_id}` `{link_id}` `{event}` `{event_id}` `{timestamp}`

Map `conversion_status` in the tracker: `lead` → lead, `approved` → approved/hold, `sale` → sale (payout earned), `rejected` → rejected.

Only public `http(s)` URLs on ports 80/443/8080/8443 are accepted. Test it with `POST /webhooks/{id}/test` and check `GET /webhooks/{id}/deliveries`.
