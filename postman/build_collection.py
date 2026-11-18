#!/usr/bin/env python3
"""Builds the Postman collection from ../openapi.json.

Run after updating openapi.json:  python3 postman/build_collection.py
Example responses below are illustrative (fictional ids, names and amounts).
"""

import json
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT.parent / "openapi.json").read_text(encoding="utf-8"))
NS = uuid.UUID("6f0a3c52-1b7e-4d2e-9a51-0b1c2d3e4f50")  # stable ids => clean diffs

TS = "2026-11-18T09:30:00.000Z"
LINK = {
    "id": 2001, "name": "Instagram reels - November", "offer_id": 432, "offer_name": "Smart watch X8",
    "offer_active": True, "url": "https://birinchishop.uz/l/AbC123",
    "tracking_url_template": "https://birinchishop.uz/l/AbC123?click_id={click_id}&sub1={sub1}&sub2={sub2}&sub3={sub3}&sub4={sub4}&sub5={sub5}",
    "clicks": 1520, "orders": 64, "delivered": 21, "created_at": "2026-11-01T06:12:00.000Z",
}
OFFER = {
    "id": 432, "name": "Smart watch X8", "customer_price": 199000, "customer_price_is_minimum": False,
    "payout": 50000, "payout_is_minimum": False, "lead_bonus": 0, "currency": "UZS", "in_stock": True, "stock": 340,
    "sale_rate_percent": 31, "sale_rate_tier": "good", "payment_type": "after_delivery",
    "image_url": "https://birinchishop.uz/uploads/example.jpg", "video_url": None, "has_variants": True,
    "created_at": "2026-10-02T08:00:00.000Z",
}
OFFER_DETAIL = {
    **OFFER,
    "description": "Product description shown on the landing page.",
    "images": ["https://birinchishop.uz/uploads/example.jpg"],
    "variants": [{"id": 5101, "name": "Black", "customer_price": 199000, "payout": 50000, "in_stock": True,
                  "image_url": None, "types": [{"id": 9001, "name": "42 mm", "in_stock": True}]}],
    "my_links": [LINK],
}
ORDER = {
    "id": 880123, "status": "shipping", "conversion_status": "approved", "created_at": TS, "updated_at": TS,
    "offer": {"id": 432, "name": "Smart watch X8"}, "link": {"id": 2001, "name": "Instagram reels - November"},
    "variant": {"id": 5101, "name": "Black", "type_id": 9001, "type_name": "42 mm"},
    "customer": {"name": "Ali", "phone_masked": "+998 ** *** 45 67", "region": "Toshkent shahri"},
    "customer_price": 199000, "payout": 50000, "payout_status": "pending", "currency": "UZS",
    "delivery_date": "2026-11-20", "operator_note": None, "courier_note": None, "source": "api",
    "sale_chance_percent": 64,
    "tracking": {"click_id": "abc123clk", "sub1": "reels", "sub2": None, "sub3": None, "sub4": None, "sub5": None,
                 "external_id": "crm-1001"},
}
NEW_ORDER = {**ORDER, "status": "new", "conversion_status": "lead", "delivery_date": None, "sale_chance_percent": None}
WEBHOOK = {
    "id": 31, "kind": "postback",
    "url": "https://tracker.example.com/postback?subid={click_id}&status={conversion_status}&payout={payout}",
    "events": ["order.created", "order.status_changed"], "description": "Tracker", "is_active": True,
    "disabled_reason": None, "consecutive_failures": 0, "last_success_at": TS, "last_failure_at": None, "created_at": TS,
}
ACTION = {
    "id": 77, "kind": "change_budget", "status": "pending_confirmation", "campaign_id": 15,
    "title": "Change daily budget", "details": [{"label": "Daily budget", "value": "150 000 UZS"}],
    "result": None, "expires_at": "2026-11-18T10:00:00.000Z", "created_at": TS, "decided_at": None,
}
CAMPAIGN = {
    "id": 15, "name": "Smart watch - leads", "status": "active", "offer_name": "Smart watch X8", "daily_budget": 10,
    "delivery_status": "active", "problem": None, "paused_reason": None,
    "stats": {"spend_uzs": 1250000, "spend_today_uzs": 120000, "orders": 48, "approved": 30, "delivered": 18,
              "cost_per_order_uzs": 26042, "cost_per_delivered_uzs": 69444, "net_profit_uzs": -350000,
              "likely_revenue_uzs": 1400000},
}
PAGE = {"page": 1, "limit": 20, "total": 1, "total_pages": 1}

EXAMPLES = {
    "getAccount": (200, {"id": 7, "name": "Partner name", "status": "active", "balance": 450000, "balance_frozen": 0,
                         "min_withdrawal": 50000, "currency": "UZS", "created_at": "2026-06-01T10:00:00.000Z",
                         "api_key": {"name": "server", "scopes": ["account:read", "offers:read", "orders:read"],
                                     "expires_at": None}}, None),
    "listOffers": (200, [OFFER], {**PAGE, "sort": "recommended"}),
    "getOffer": (200, OFFER_DETAIL, None),
    "listLinks": (200, [LINK], PAGE),
    "createLink": (201, LINK, None),
    "getLink": (200, LINK, None),
    "listOrders": (200, [ORDER], PAGE),
    "createOrder": (201, NEW_ORDER, None),
    "getOrder": (200, ORDER, None),
    "getStats": (200, [{"offer_id": 432, "offer_name": "Smart watch X8", "orders": 64, "approved": 40, "delivered": 21,
                        "rejected": 12, "pending": 31, "approval_rate_percent": 63, "delivery_rate_percent": 33,
                        "earned": 1050000, "potential_earnings": 950000, "clicks": 1520, "unique_clicks": 1210}],
                 {"group_by": "offer", "date_from": "2026-11-01", "date_to": "2026-11-18", "timezone": "Asia/Tashkent",
                  "currency": "UZS", "totals": {"orders": 64, "delivered": 21, "earned": 1050000, "clicks": 1520,
                                                "unique_clicks": 1210}, "clicks_since": "2026-11-05"}),
    "listEvents": (200, [{"id": 55012, "type": "order.status_changed", "created_at": TS, "order_id": 880123,
                          "status": "shipping", "previous_status": "packed", "conversion_status": "approved"}],
                   {"next_cursor": 55012, "has_more": False}),
    "getOrderSaleChance": (200, {"order_id": 880123, "percent": 64, "level": "mid", "final": False,
                                 "factors": [{"factor": "offer"}, {"factor": "stage"}], "computed_at": TS}, None),
    "getInsights": (200, {"day": "2026-11-18", "yesterday": {}, "week": {}, "pending": {}, "balance": {},
                          "my_offers": [], "suggested_offers": [], "campaigns": [],
                          "recommendations": [{"type": "try_offers", "priority": 3, "hint": "Try best-selling offers"}],
                          "morning_brief": None}, None),
    "getAdsStatus": (200, {"connected": False, "hint": "Connect a Meta ad account in the partner panel (/dashboard/meta-ads)."}, None),
    "listCampaigns": (200, [CAMPAIGN], None),
    "pauseCampaign": (200, {"id": 15, "status": "paused", "changed": True}, None),
    "resumeCampaign": (202, {**ACTION, "kind": "resume_campaign", "title": "Resume campaign", "details": []}, None),
    "changeCampaignBudget": (202, ACTION, None),
    "getAction": (200, {**ACTION, "status": "done", "decided_at": TS, "result": "ok"}, None),
    "listWebhooks": (200, [WEBHOOK], None),
    "createWebhook": (201, {**WEBHOOK, "kind": "json", "url": "https://example.com/hooks/birinchishop",
                            "description": None, "last_success_at": None, "secret": "whsec_shown_once_store_it"}, None),
    "updateWebhook": (200, WEBHOOK, None),
    "deleteWebhook": (200, {"id": 31, "deleted": True}, None),
    "testWebhook": (200, {"ok": True, "response_code": 200, "response_snippet": "ok", "error": None, "duration_ms": 184}, None),
    "listWebhookDeliveries": (200, [{"id": 9001, "event_id": 55012, "status": "delivered", "attempts": 1,
                                     "response_code": 200, "response_snippet": "ok", "error": None, "duration_ms": 120,
                                     "next_attempt_at": None, "created_at": TS, "delivered_at": TS}], None),
    "getReference": (200, {"api_version": SPEC["info"]["version"], "base_url": "https://birinchishop.uz/api/v1",
                           "currency": "UZS (Uzbek som), integer amounts"}, None),
}
ERROR_EXAMPLES = {
    "createOrder": [(409, "duplicate_order", "This phone number already has an order for this offer in the last 24 hours"),
                    (403, "orders_write_not_allowed", "Sending orders via API requires at least 3 delivered orders on the account, or admin approval.")],
    "getAccount": [(401, "unauthorized", "Invalid API key.")],
    "listOffers": [(403, "insufficient_scope", 'This API key lacks the "offers:read" scope.')],
    "listOrders": [(429, "rate_limited", "Rate limit exceeded (120 requests per minute per key).")],
}

# Sample request bodies. Every {{var}} comes from the environment file.
BODIES = {
    "createLink": {"offer_id": "{{offer_id}}", "name": "Instagram reels - November"},
    "createOrder": {"link_id": "{{link_id}}", "phone": "{{customer_phone}}", "name": "{{customer_name}}",
                    "region": "Toshkent shahri", "external_id": "crm-1001", "click_id": "abc123clk", "sub1": "reels"},
    "changeCampaignBudget": {"daily_budget": 150000, "unit": "UZS"},
    "createWebhook": {"kind": "postback",
                      "url": "https://tracker.example.com/postback?subid={click_id}&status={conversion_status}&payout={payout}&currency={currency}",
                      "events": ["order.created", "order.status_changed"], "description": "Tracker"},
    "updateWebhook": {"is_active": True},
}
INT_BODY_FIELDS = {"offer_id", "link_id"}  # numeric fields filled from variables: unquote in raw JSON

PATH_VARS = {"offer_id": "offer_id", "link_id": "link_id", "order_id": "order_id", "campaign_id": "campaign_id",
             "action_id": "action_id", "webhook_id": "webhook_id"}

CREATE_ORDER_WARNING = (
    "**⚠ Creates a REAL order.** A call center phones the customer and a courier delivers the product. "
    "Only for a real customer who asked to order, with their correct phone number. "
    "Never send test, sample or fake orders — the account gets blocked.\n\n"
    "`customer_phone` is empty in the environment on purpose, so an accidental Send fails with `invalid_request`. "
    "`Idempotency-Key` uses `{{$guid}}`; when you retry the same order, send the same key so no duplicate is created.\n\n"
)


def ref(obj):
    if isinstance(obj, dict) and "$ref" in obj:
        parts = obj["$ref"].lstrip("#/").split("/")
        node = SPEC
        for p in parts:
            node = node[p]
        return node
    return obj


def raw_json(body):
    s = json.dumps(body, indent=2, ensure_ascii=False)
    for f in INT_BODY_FIELDS:
        s = re.sub(rf'("{f}": )"(\{{\{{{f}\}}\}})"', r"\1\2", s)
    return s


def envelope(op_id, status):
    code, data, meta = EXAMPLES[op_id]
    body = {"data": data}
    if meta is not None:
        body["meta"] = meta
    body["request_id"] = "req_Ab12Cd34Ef56"
    return body


def make_url(path, query_params):
    segs = []
    variables = []
    for s in path.strip("/").split("/"):
        m = re.fullmatch(r"\{(\w+)\}", s)
        if m:
            segs.append(":" + m.group(1))
            variables.append({"key": m.group(1), "value": "{{" + PATH_VARS.get(m.group(1), m.group(1)) + "}}"})
        else:
            segs.append(s)
    raw = "{{baseUrl}}/" + "/".join(segs)
    enabled = [q for q in query_params if not q.get("disabled")]
    if enabled:
        raw += "?" + "&".join(f"{q['key']}={q['value']}" for q in enabled)
    url = {"raw": raw, "host": ["{{baseUrl}}"], "path": segs}
    if query_params:
        url["query"] = query_params
    if variables:
        url["variable"] = variables
    return url


def sample_query_value(name, schema):
    defaults = {"search": "soat", "sort": "best_selling", "lang": "uz", "status": "delivered",
                "conversion_status": "sale", "date_from": "2026-11-01", "date_to": "2026-11-18",
                "updated_since": "2026-11-18T00:00:00Z", "group_by": "offer", "type": "order.status_changed",
                "period": "7d", "click_id": "abc123clk", "external_id": "crm-1001", "ids": "432,433",
                "after": "0", "min_sale_rate": "25", "min_payout": "30000"}
    if name in PATH_VARS:
        return "{{" + PATH_VARS[name] + "}}"
    if name in defaults:
        return defaults[name]
    if "default" in schema:
        d = schema["default"]
        return str(d).lower() if isinstance(d, bool) else str(d)
    return ""


def build_item(path, method, op):
    op_id = op["operationId"]
    params = [ref(p) for p in op.get("parameters", [])]
    query = []
    headers = [{"key": "Accept", "value": "application/json"}]
    for p in params:
        if p["in"] == "query":
            enabled_keys = {"listOffers": {"sort", "limit"}, "listOrders": {"limit"}, "getStats": {"group_by", "date_from", "date_to"},
                            "listEvents": {"after", "limit"}, "listCampaigns": {"period"}, "listLinks": {"limit"}}
            q = {"key": p["name"], "value": sample_query_value(p["name"], p.get("schema", {})),
                 "description": (p.get("description") or "") + (f" Allowed: {', '.join(map(str, p['schema']['enum']))}." if "enum" in p.get("schema", {}) else "")}
            if p["name"] not in enabled_keys.get(op_id, set()):
                q["disabled"] = True
            query.append(q)
        elif p["in"] == "header" and p["name"] == "Idempotency-Key":
            headers.append({"key": "Idempotency-Key", "value": "{{$guid}}",
                            "description": "Same key on retry => the existing order is returned (200, Idempotent-Replayed: true)."})
    body = None
    if "requestBody" in op:
        headers.append({"key": "Content-Type", "value": "application/json"})
        body = {"mode": "raw", "raw": raw_json(BODIES.get(op_id, {})), "options": {"raw": {"language": "json"}}}

    scopes = op.get("security", [{}])[0].get("ApiKey") if op.get("security") else None
    desc = op.get("description") or ""
    if op_id == "createOrder":
        desc = CREATE_ORDER_WARNING + desc
    if scopes:
        desc = f"Scope: `{', '.join(scopes)}`\n\n" + desc
    request = {"method": method.upper(), "header": headers, "url": make_url(path, query), "description": desc.strip()}
    if body:
        request["body"] = body
    if op.get("security") == []:
        request["auth"] = {"type": "noauth"}

    responses = []
    if op_id in EXAMPLES:
        code = EXAMPLES[op_id][0]
        resp_headers = [{"key": "Content-Type", "value": "application/json; charset=utf-8"}]
        responses.append({"name": f"{code} {SPEC['paths'][path][method]['responses'].get(str(code), {}).get('description', 'OK')}",
                          "originalRequest": request, "status": "OK" if code < 300 else "Error", "code": code,
                          "_postman_previewlanguage": "json", "header": resp_headers,
                          "body": json.dumps(envelope(op_id, code), indent=2, ensure_ascii=False)})
    for code, ecode, msg in ERROR_EXAMPLES.get(op_id, []):
        responses.append({"name": f"{code} {ecode}", "originalRequest": request, "status": "Error", "code": code,
                          "_postman_previewlanguage": "json",
                          "header": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}],
                          "body": json.dumps({"error": {"code": ecode, "message": msg}, "request_id": "req_Ab12Cd34Ef56"}, indent=2)})
    return {"id": str(uuid.uuid5(NS, op_id)), "name": op.get("summary") or op_id, "request": request, "response": responses}


FOLDERS = [
    ("Account", ["getAccount", "getReference"]),
    ("Offers", ["listOffers", "getOffer"]),
    ("Links", ["listLinks", "createLink", "getLink"]),
    ("Orders", ["listOrders", "getOrder", "getOrderSaleChance", "createOrder"]),
    ("Stats & events", ["getStats", "listEvents"]),
    ("AI manager", ["getInsights"]),
    ("Meta ads", ["getAdsStatus", "listCampaigns", "pauseCampaign", "resumeCampaign", "changeCampaignBudget", "getAction"]),
    ("Webhooks & postbacks", ["listWebhooks", "createWebhook", "updateWebhook", "deleteWebhook", "testWebhook",
                              "listWebhookDeliveries"]),
]


def main():
    ops = {}
    for path, item in SPEC["paths"].items():
        for method, op in item.items():
            if isinstance(op, dict) and op.get("operationId") and op["operationId"] != "mcp":
                ops[op["operationId"]] = (path, method, op)
    listed = {o for _, ids in FOLDERS for o in ids}
    missing = set(ops) - listed
    if missing:
        raise SystemExit(f"operations not placed in a folder: {sorted(missing)}")

    info_desc = (
        "Birinchi Shop Partner API v1 — COD CPA affiliate network in Uzbekistan.\n\n"
        "1. Import `birinchishop-api-v1.postman_environment.json`, select it and paste your key into `bsk_key` "
        "(Dashboard → API in the partner panel). Keep the key secret: do not share a collection export with the value filled in.\n"
        "2. Set the id variables (`offer_id`, `link_id`, …) to your own objects.\n\n"
        "**`POST /orders` creates a REAL order** (a call center phones the customer). Never send test or fake orders.\n\n"
        "Docs: https://birinchishop.uz/api/v1/docs · OpenAPI: https://birinchishop.uz/api/v1/openapi.json · "
        "Examples: https://github.com/Birinchishop/birinchishop-api-examples\n\n"
        f"Generated from openapi.json (api_version {SPEC['info']['version']}). Example responses use fictional data."
    )
    collection = {
        "info": {
            "_postman_id": str(uuid.uuid5(NS, "collection")),
            "name": "Birinchi Shop Partner API v1",
            "description": info_desc,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{bsk_key}}", "type": "string"}]},
        "item": [{"name": name, "item": [build_item(*ops[o]) for o in ids]} for name, ids in FOLDERS],
        "variable": [{"key": "baseUrl", "value": "https://birinchishop.uz/api/v1", "type": "string"}],
    }
    env = {
        "id": str(uuid.uuid5(NS, "environment")),
        "name": "Birinchi Shop API",
        "values": [
            {"key": "baseUrl", "value": "https://birinchishop.uz/api/v1", "type": "default", "enabled": True},
            {"key": "bsk_key", "value": "", "type": "secret", "enabled": True},
            {"key": "offer_id", "value": "", "type": "default", "enabled": True},
            {"key": "link_id", "value": "", "type": "default", "enabled": True},
            {"key": "order_id", "value": "", "type": "default", "enabled": True},
            {"key": "campaign_id", "value": "", "type": "default", "enabled": True},
            {"key": "action_id", "value": "", "type": "default", "enabled": True},
            {"key": "webhook_id", "value": "", "type": "default", "enabled": True},
            {"key": "customer_phone", "value": "", "type": "default", "enabled": True},
            {"key": "customer_name", "value": "", "type": "default", "enabled": True},
        ],
        "_postman_variable_scope": "environment",
    }
    (ROOT / "birinchishop-api-v1.postman_collection.json").write_text(
        json.dumps(collection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "birinchishop-api-v1.postman_environment.json").write_text(
        json.dumps(env, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{sum(len(i) for _, i in FOLDERS)} requests in {len(FOLDERS)} folders")


if __name__ == "__main__":
    main()
