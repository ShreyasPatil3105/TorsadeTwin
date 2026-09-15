#!/usr/bin/env python3
"""Zero-dependency local frontend server + API reverse proxy.

Run the existing TorsadeTwin FastAPI backend separately:
    uvicorn backend.app.main:app --host 127.0.0.1 --port 8001

Then:
    python frontend/dev_server.py

The browser talks to this server on :5173. Requests to /api/* are
proxied to the existing backend. No backend source files are modified.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
BACKEND = os.environ.get("TORSADETWIN_BACKEND", "http://127.0.0.1:8001").rstrip("/")

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy("GET")
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self.proxy("POST")
        self.send_error(405, "Method Not Allowed")

    def proxy(self, method):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else None
        target = f"{BACKEND}{self.path}"
        req = Request(target, data=body, method=method,
                      headers={"Content-Type": self.headers.get("Content-Type", "application/json"),
                               "Accept": "application/json"})
        try:
            with urlopen(req, timeout=240) as resp:
                payload = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except HTTPError as e:
            payload = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except URLError as e:
            payload = ('{"detail":"Frontend proxy could not reach FastAPI: %s"}' % str(e.reason)).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def log_message(self, fmt, *args):
        # Keep useful request logs while making them visually compact.
        print("%s %s" % (self.address_string(), fmt % args))

if __name__ == "__main__":
    host = os.environ.get("TORSADETWIN_FRONTEND_HOST", "127.0.0.1")
    port = int(os.environ.get("TORSADETWIN_FRONTEND_PORT", "5173"))
    print(f"TorsadeTwin frontend: http://{host}:{port}")
    print(f"Proxying /api/* -> {BACKEND}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
