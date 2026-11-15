"""Read-only: list offers worth promoting. Python 3.8+, no dependencies.
Run: BSK_KEY=... python3 list_offers.py
"""
import json
import os
import urllib.request

API = "https://birinchishop.uz/api/v1"
KEY = os.environ.get("BSK_KEY")
if not KEY:
    raise SystemExit("Set BSK_KEY (server-side secret)")

req = urllib.request.Request(
    f"{API}/offers?sort=best_selling&in_stock_only=true&min_sale_rate=25&limit=10",
    headers={"Authorization": f"Bearer {KEY}"},
)
with urllib.request.urlopen(req, timeout=30) as r:
    body = json.load(r)

for o in body["data"]:
    rate = o.get("sale_rate_percent")
    print(f"#{o['id']} {o['name']} - payout {o['payout']} UZS, sale rate {rate if rate is not None else 'n/a'}%")
