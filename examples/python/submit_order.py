"""Submits a REAL order: the call center will phone this customer.
Use only with a real customer who agreed to order. Test or fake orders get the account blocked.
Run: BSK_KEY=... CONFIRM_REAL_ORDER=yes python3 submit_order.py <link_id> <+998XXXXXXXXX> [name]
"""
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

API = "https://birinchishop.uz/api/v1"
KEY = os.environ.get("BSK_KEY")
if not KEY or len(sys.argv) < 3:
    raise SystemExit("Usage: submit_order.py <link_id> <phone> [name]")
if os.environ.get("CONFIRM_REAL_ORDER") != "yes":
    raise SystemExit("This creates a REAL order. Set CONFIRM_REAL_ORDER=yes to continue.")

payload = {"link_id": int(sys.argv[1]), "phone": sys.argv[2]}
if len(sys.argv) > 3:
    payload["name"] = sys.argv[3]

req = urllib.request.Request(
    f"{API}/orders",
    data=json.dumps(payload).encode(),
    method="POST",
    headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "Idempotency-Key": str(uuid.uuid4()),  # reuse the same key when retrying
    },
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    print("Order created:", body["data"]["id"], body["data"]["status"])
except urllib.error.HTTPError as e:
    err = json.load(e).get("error", {})
    raise SystemExit(f"{e.code} {err.get('code')}: {err.get('message')}")
