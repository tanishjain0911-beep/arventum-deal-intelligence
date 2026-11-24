"""List Gemini models available to the free API key and test a tiny generation (key read from the user env)."""
import json
import os
import time
import urllib.request

KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        KEY = winreg.QueryValueEx(k, "GEMINI_API_KEY")[0]
H = {"x-goog-api-key": KEY, "Content-Type": "application/json"}
BASE = "https://generativelanguage.googleapis.com/v1beta"

req = urllib.request.Request(f"{BASE}/models?pageSize=100", headers=H)
models = [m["name"] for m in json.load(urllib.request.urlopen(req, timeout=30))["models"]
          if "generateContent" in m.get("supportedGenerationMethods", [])]
flash = [m for m in models if "flash" in m]
print("flash models:", flash[:15])
for m in flash[:6]:
    body = json.dumps({"contents": [{"parts": [{"text": "Reply with exactly: OK"}]}]}).encode()
    t = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(f"{BASE}/{m}:generateContent", data=body, headers=H),
                                   timeout=60)
        txt = json.load(r)["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"{m}: {txt!r} ({time.time() - t:.1f}s)")
    except Exception as e:  # noqa: BLE001
        print(f"{m}: ERROR {str(e)[:90]}")
