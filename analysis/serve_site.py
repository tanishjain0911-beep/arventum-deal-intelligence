"""Serve site/ locally with caching disabled (so edits show on reload). Usage: python analysis/serve_site.py [port]"""
import functools
import http.server
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8600
    http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(NoCache, directory=str(SITE))).serve_forever()
