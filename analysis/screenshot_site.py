"""Screenshots of the static site (site/) at desktop and phone widths via headless Edge + DevTools.

Serve the site first (python analysis/serve_site.py). Usage:
    python analysis/screenshot_site.py OUT_DIR [view ...]      views: summary market radar ... method
Writes <view>.png (1440 wide, full height) and <view>-mobile.png (390 wide); prints any console errors.
"""
import base64
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from screenshot_pages import CDP, EDGE, PORT  # noqa: E402
import json, subprocess, tempfile, urllib.request  # noqa: E401,E402

VIEWS = ["summary", "market", "radar", "investors", "buyers", "valuation", "company", "method"]
SIZES = {"": (1440, False), "-mobile": (390, True)}


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    views = sys.argv[2:] or VIEWS
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as prof:
        proc = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", "--no-first-run", "--hide-scrollbars",
                                 f"--remote-debugging-port={PORT}", "--remote-allow-origins=*",
                                 f"--user-data-dir={prof}", "about:blank"])
        try:
            for _ in range(50):
                try:
                    page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                                if t["type"] == "page"); break
                except Exception:  # noqa: BLE001
                    time.sleep(0.3)
            c = CDP(page["webSocketDebuggerUrl"])
            c.call("Page.enable")
            for v in views:
                for suffix, (w, mobile) in SIZES.items():
                    c.call("Emulation.setDeviceMetricsOverride", width=w, height=900, deviceScaleFactor=1, mobile=mobile)
                    c.call("Page.navigate", url=f"http://localhost:8600/app.html?r={time.time()}#/{v}")
                    for _ in range(40):
                        if c.eval("!!document.querySelector('main .view')"):
                            break
                        time.sleep(0.25)
                    time.sleep(1.2)  # entrance animation
                    h = int(min(c.eval("document.documentElement.scrollHeight") or 2000, 9000))
                    overflow = c.eval("document.documentElement.scrollWidth > innerWidth")
                    c.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobile)
                    time.sleep(0.5)
                    shot = c.call("Page.captureScreenshot", format="png", captureBeyondViewport=True)
                    (out / f"{v}{suffix}.png").write_bytes(base64.b64decode(shot["data"]))
                    err = c.eval("document.querySelector('main .empty')?.innerText || ''")
                    print(f"{v}{suffix}: {w}x{h} overflow={overflow} {err}", flush=True)
        finally:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)


if __name__ == "__main__":
    main()
