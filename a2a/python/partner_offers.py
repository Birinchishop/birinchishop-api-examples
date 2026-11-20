"""Read-only A2A client for the Birinchi Shop PARTNER agent (Python 3.8+, standard library only).

Run: BIRINCHISHOP_API_KEY=bsk_test_... python partner_offers.py "soat"
Flow: fetch the Agent Card -> pick the JSON-RPC interface -> SendMessage (get_account, then search_offers).
The key comes from the partner panel (API section). A test key (bsk_test_...) is the safe way to try this:
it reads real offers but never creates anything. This example never calls create_link or create_order.
"""
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

ORIGIN = "https://birinchishop.uz"
UA = "a2a-example-client/1.0"  # the default Python-urllib User-Agent is blocked by the CDN (403)
KEY = os.environ.get("BIRINCHISHOP_API_KEY")
if not KEY:
    sys.exit("Set BIRINCHISHOP_API_KEY (bsk_test_... or bsk_live_...)")
query = sys.argv[1] if len(sys.argv) > 1 else "soat"


def request(url, payload=None, auth=False):
    headers = {"Accept": "application/json", "User-Agent": UA}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers.update({"Content-Type": "application/json", "A2A-Version": "1.0"})
    if auth:
        headers["Authorization"] = f"Bearer {KEY}"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # A2A errors arrive as JSON-RPC bodies, also on 4xx
        return json.load(e)


# 1. Discover the agent. The card is public; every other call needs the key.
card = request(f"{ORIGIN}/api/a2a/partner/agent-card.json")
iface = next(
    (i for i in card["supportedInterfaces"] if i["protocolBinding"] == "JSONRPC" and i["protocolVersion"] == "1.0"),
    None,
)
if not iface:
    sys.exit("No A2A 1.0 JSON-RPC interface in the Agent Card")
print(f"Agent: {card['name']} v{card['version']}; skills: {', '.join(s['id'] for s in card['skills'])}")


# 2. One skill call = one message with a data part {"skill", "arguments"}. Every skill completes in one step.
def call(skill, arguments=None):
    body = request(
        iface["url"],
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "ROLE_USER",
                    "parts": [{"data": {"skill": skill, "arguments": arguments or {}}}],
                }
            },
        },
        auth=True,
    )
    if "error" in body:
        sys.exit(f"A2A error {body['error']['code']}: {body['error']['message']}")
    task = body["result"]["task"]
    if task["status"]["state"] != "TASK_STATE_COMPLETED":
        parts = (task["status"].get("message") or {}).get("parts", [])
        why = " ".join(p["text"] for p in parts if "text" in p)
        sys.exit(f"{skill}: {task['status']['state']} {why}".strip())
    # The artifact carries a text part (human-readable) and a data part (the same JSON the REST API returns).
    return next(p["data"] for p in task["artifacts"][0]["parts"] if "data" in p)


# 3. Who am I, then which offers match the query.
account = call("get_account")
print("Account:", json.dumps(account, ensure_ascii=False)[:300])

offers = call("search_offers", {"search": query, "limit": 5})
for o in offers.get("data", []):
    rate = "no data yet" if o.get("sale_rate_percent") is None else f"{o['sale_rate_percent']}%"
    print(f"#{o['id']} {o['name']} | price {o['customer_price']} UZS | payout {o['payout']} UZS | sale rate {rate}")
