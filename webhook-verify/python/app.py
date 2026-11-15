"""Minimal webhook receiver (Python 3.8+, standard library only).
Verifies X-Birinchishop-Signature and rejects signatures older than 5 minutes.
Run: BSK_WEBHOOK_SECRET=... python3 app.py   (put it behind HTTPS)
"""
import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = os.environ.get("BSK_WEBHOOK_SECRET", "")


def verify(raw_body: bytes, header: str, secret: str, now: float = None) -> bool:
    if not header:
        return False
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    now = time.time() if now is None else now
    if "t" not in parts or abs(now - int(parts["t"])) > 300:
        return False
    expected = hmac.new(secret.encode(), parts["t"].encode() + b"." + raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))


SEEN = set()  # use a database table in production


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if not verify(raw, self.headers.get("X-Birinchishop-Signature", ""), SECRET):
            self.send_response(401)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        evt = json.loads(raw)
        if evt["id"] in SEEN:
            return
        SEEN.add(evt["id"])
        d = evt["data"]
        print(evt["type"], "order", d["order_id"], d["status"], d["conversion_status"])


if __name__ == "__main__":
    if not SECRET:
        raise SystemExit("Set BSK_WEBHOOK_SECRET")
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), Handler).serve_forever()
