"""Check that the Gemini and Groq keys work (prints model names and a test reply; never prints keys)."""
import json
import os
import urllib.request
import winreg


def key(name):
    v = os.environ.get(name)
    if v:
        return v
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except OSError:
        return None


def call(url, headers, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={**headers, "Content-Type": "application/json",
                                          "User-Agent": "arventum-deal-intelligence"})
    return json.load(urllib.request.urlopen(req, timeout=60))


g = key("GEMINI_API_KEY")
print("GEMINI key found:", bool(g))
if g:
    try:
        H = {"x-goog-api-key": g}
        ms = [m["name"] for m in call("https://generativelanguage.googleapis.com/v1beta/models?pageSize=100", H)["models"]
              if "generateContent" in m.get("supportedGenerationMethods", []) and "flash" in m["name"]]
        print("  flash models:", ms[:6])
        for m in ms[:3]:
            try:
                r = call(f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent", H,
                         {"contents": [{"parts": [{"text": "Reply with exactly: OK"}]}]})
                print("  ", m, "->", r["candidates"][0]["content"]["parts"][0]["text"].strip())
                break
            except Exception as e:  # noqa: BLE001
                print("  ", m, "-> ERROR", str(e)[:80])
    except Exception as e:  # noqa: BLE001
        print("  ERROR", str(e)[:120])

q = key("GROQ_API_KEY")
print("GROQ key found:", bool(q))
if q:
    try:
        H = {"Authorization": f"Bearer {q}"}
        ms = [m["id"] for m in call("https://api.groq.com/openai/v1/models", H)["data"]]
        print("  models:", [m for m in ms if "llama" in m or "qwen" in m or "gpt-oss" in m][:8])
        pick = next((m for m in ms if "70b" in m or "gpt-oss-120b" in m), ms[0])
        r = call("https://api.groq.com/openai/v1/chat/completions", H,
                 {"model": pick, "messages": [{"role": "user", "content": "Reply with exactly: OK"}]})
        print("  ", pick, "->", r["choices"][0]["message"]["content"].strip())
    except Exception as e:  # noqa: BLE001
        print("  ERROR", str(e)[:120])
