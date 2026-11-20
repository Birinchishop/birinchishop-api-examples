"""Read-only A2A client for the Birinchi Shop store agent (Python 3.8+, standard library only).

Run: python shop_search.py "soat"      (no API key needed; the store agent is public)
Flow: fetch the Agent Card -> pick the JSON-RPC interface -> SendMessage -> read the Task artifact.
Only searches the catalog. Never calls place_order (a real order is phoned by a call center).
"""
import json
import sys
import urllib.request
import uuid

ORIGIN = "https://birinchishop.uz"
UA = "a2a-example-client/1.0"  # the default Python-urllib User-Agent is blocked by the CDN (403)
query = sys.argv[1] if len(sys.argv) > 1 else "soat"


def get_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


# 1. Discover the agent.
card = get_json(f"{ORIGIN}/.well-known/agent-card.json")
iface = next(
    (i for i in card["supportedInterfaces"] if i["protocolBinding"] == "JSONRPC" and i["protocolVersion"] == "1.0"),
    None,
)
if not iface:
    sys.exit("No A2A 1.0 JSON-RPC interface in the Agent Card")
print(f"Agent: {card['name']} v{card['version']}; skills: {', '.join(s['id'] for s in card['skills'])}")

# 2. Send a message with an explicit skill call (plain text would also be read as a search query).
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "SendMessage",
    "params": {
        "message": {
            "messageId": str(uuid.uuid4()),
            "role": "ROLE_USER",
            "parts": [{"data": {"skill": "search_products", "arguments": {"query": query, "limit": 5}}}],
        }
    },
}
req = urllib.request.Request(
    iface["url"],
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json", "A2A-Version": "1.0", "User-Agent": UA},
)
with urllib.request.urlopen(req, timeout=30) as r:
    body = json.load(r)
if "error" in body:
    sys.exit(f"A2A error {body['error']['code']}: {body['error']['message']}")

# 3. Read the result: the search is synchronous, so the Task is already completed.
task = body["result"]["task"]
print(f"Task {task['id']}: {task['status']['state']}")
for artifact in task.get("artifacts", []):
    for part in artifact["parts"]:
        if "text" in part:
            print(part["text"])
        elif "data" in part and "items" in part["data"]:
            print(f"({len(part['data']['items'])} structured items, total {part['data'].get('total')})")
