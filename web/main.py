#!/usr/bin/env python3
"""IDeK game — browser UI + local market API + Firebase Auth/Leaderboard (client).

Run:  /usr/bin/python3 main.py
Opens http://127.0.0.1:8765/

Auth & leaderboard use Firebase in the browser.
Market ticks / portfolio still use this Python server + CSV.
"""
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from functions import action_csv
from market import (
    buy_stock,
    calc_market,
    create_markets,
    portfolio_state,
    sell_all_stock,
    sell_stock,
)

HOST = "127.0.0.1"
PORT = 8765
ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[IDeK]", fmt % args)

    def _json(self, code, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _file(self, path: Path, content_type: str):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._file(STATIC / "index.html", "text/html; charset=utf-8")
            return
        # simple static file server under /static/
        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            target = (STATIC / rel).resolve()
            if str(target).startswith(str(STATIC.resolve())) and target.is_file():
                ctype = "application/octet-stream"
                if target.suffix == ".html":
                    ctype = "text/html; charset=utf-8"
                elif target.suffix == ".js":
                    ctype = "application/javascript"
                elif target.suffix == ".css":
                    ctype = "text/css"
                self._file(target, ctype)
                return
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()

        # Password options for Create Account (Firebase stores the chosen password).
        if path == "/api/pass_options":
            username = (body.get("username") or "").strip()
            opts = action_csv(1, username, "pass_list.csv", "pass")
            self._json(200, {"options": opts})
            return

        if path == "/api/tick":
            create_markets()
            calc_market()
            self._json(200, {"ok": True})
            return

        if path == "/api/market":
            username = (body.get("username") or "").strip() or "guest"
            create_markets()
            self._json(200, portfolio_state(username))
            return

        if path == "/api/buy":
            username = (body.get("username") or "").strip()
            self._json(200, buy_stock(username, body.get("risk_id"), body.get("quantity", 1)))
            return

        if path == "/api/sell":
            username = (body.get("username") or "").strip()
            self._json(200, sell_stock(username, body.get("risk_id"), body.get("index")))
            return

        if path == "/api/sell_all":
            username = (body.get("username") or "").strip()
            try:
                risk_id = int(body.get("risk_id"))
            except (TypeError, ValueError):
                self._json(200, {"ok": False, "error": "Invalid risk level."})
                return
            self._json(200, sell_all_stock(username, risk_id))
            return

        self.send_error(404)


def main():
    if not (STATIC / "index.html").is_file():
        raise SystemExit(f"Missing UI file: {STATIC / 'index.html'}")
    create_markets()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"IDeK running at {url}")
    print("Auth/Leaderboard: Firebase project idek-game (client SDK).")
    print("Enable Email/Password in Firebase Console → Authentication → Sign-in method.")
    print("Deploy rules: npx -y firebase-tools@latest deploy --only firestore:rules")
    print("Leave this terminal open while playing.")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
