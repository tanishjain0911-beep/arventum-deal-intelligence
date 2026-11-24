"""Full-page screenshots of every app page via headless Edge + the DevTools protocol (visual QA).

Waits until Streamlit has finished rendering (no "running" status widget, no skeletons), then captures
the full page height. Usage: python analysis/screenshot_pages.py OUT_DIR [page ...]
"""
import base64
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PAGES = {"home": "", "pulse": "Market_Pulse", "radar": "Origination_Radar", "match": "Investor_Matchmaker",
         "buyers": "Buyer_Mapping", "price": "Price_Finder", "lookup": "Company_Lookup",
         "quality": "Data_and_Quality",
         "built": "How_It_Was_Built"}
PORT = 9333


class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60)
        self.i = 0

    def call(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.i:
                return msg.get("result", {})

    def eval(self, expr):
        return self.call("Runtime.evaluate", expression=expr, returnByValue=True).get("result", {}).get("value")


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    names = sys.argv[2:] or list(PAGES)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as prof:
        proc = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
                                 f"--remote-debugging-port={PORT}", "--remote-allow-origins=*",
                                 f"--user-data-dir={prof}", "about:blank"])
        try:
            for _ in range(50):
                try:
                    tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                    page = next(t for t in tabs if t["type"] == "page")
                    break
                except Exception:  # noqa: BLE001
                    time.sleep(0.3)
            c = CDP(page["webSocketDebuggerUrl"])
            c.call("Page.enable")
            c.call("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1, mobile=False)
            for name in names:
                c.call("Page.navigate", url=f"http://localhost:8501/{PAGES[name]}")
                time.sleep(4)
                for _ in range(60):  # wait for Streamlit to finish running the script
                    busy = c.eval("!!document.querySelector('[data-testid=\"stStatusWidget\"]') || "
                                  "!!document.querySelector('[data-testid=\"stSkeleton\"]') || "
                                  "document.querySelectorAll('[data-testid=\"stMain\"] *').length < 30")
                    if not busy:
                        break
                    time.sleep(1)
                time.sleep(3)  # let charts finish drawing
                h = c.eval("Math.max(document.querySelector('[data-testid=\"stMain\"]')?.scrollHeight || 0, "
                           "document.body.scrollHeight)") or 2000
                h = int(min(h, 7000))
                c.call("Emulation.setDeviceMetricsOverride", width=1400, height=h, deviceScaleFactor=1, mobile=False)
                time.sleep(2)
                shot = c.call("Page.captureScreenshot", format="png", captureBeyondViewport=True)
                (out / f"{name}.png").write_bytes(base64.b64decode(shot["data"]))
                c.call("Emulation.setDeviceMetricsOverride", width=1400, height=1000, deviceScaleFactor=1,
                       mobile=False)
                errs = c.eval("Array.from(document.querySelectorAll('[data-testid=\"stException\"]'))"
                              ".map(e => e.innerText.slice(0, 200))")
                print(name, "height", h, "exceptions", errs or 0, flush=True)
        finally:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
            time.sleep(1)


if __name__ == "__main__":
    main()
