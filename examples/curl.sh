#!/usr/bin/env bash
# Read-only requests. Set BSK_KEY in your environment first (never hard-code it).
set -euo pipefail
API=https://birinchishop.uz/api/v1
H="Authorization: Bearer ${BSK_KEY:?set BSK_KEY}"

# Your account and balance (scope account:read)
curl -s "$API/me" -H "$H"

# Best-selling offers in stock with a sale rate of at least 25% (scope offers:read)
curl -s "$API/offers?sort=best_selling&min_sale_rate=25&limit=10" -H "$H"

# Your latest orders and their statuses (scope orders:read)
curl -s "$API/orders?limit=20" -H "$H"
