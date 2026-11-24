"""Wait until an AI extractor is available again, then resume extraction automatically.

Every 10 minutes: one tiny Codex call (ChatGPT quota) and one free-model call. When either answers,
rebuild the "remaining" queue (articles not yet covered by any AI agent) and run extraction on it with
whatever is available. Repeats until nothing remains. Safe to stop at any time.
"""
import datetime as dt
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import run_extraction as rx  # noqa: E402

PY = sys.executable


def available():
    ok = []
    try:
        p = rx.run_killable(["codex", "exec", "--skip-git-repo-check", "--ephemeral", "-m", rx.CODEX_MODEL,
                             "-c", 'model_reasoning_effort="low"', "-"], input_text="Reply with exactly: OK",
                            timeout=90)
        if "OK" in (p.stdout or "") and "usage limit" not in ((p.stdout or "") + (p.stderr or "")).lower():
            ok.append("codex")
    except Exception:  # noqa: BLE001
        pass
    try:
        p = rx.run_killable(["opencode", "run", "-m", rx.FREE_MODELS["deepseek"], '"Reply with exactly: OK"'],
                            timeout=90)
        if "OK" in (p.stdout or ""):
            ok.append("deepseek")
    except Exception:  # noqa: BLE001
        pass
    return ok


def main():
    while True:
        ok = available()
        stamp = dt.datetime.now().strftime("%H:%M")
        print(stamp, "available:", ok or "none", flush=True)
        if ok:
            rx.QUOTA_FLAG.unlink(missing_ok=True) if "codex" in ok else None
            subprocess.run([PY, "pipeline/make_remaining.py"], cwd=ROOT)
            n = sum(1 for _ in open(ROOT / "data" / "raw" / "remaining_urls.csv", encoding="utf-8")) - 1
            if n <= 0:
                print("nothing left to extract", flush=True)
                return
            agents = "codex:3,opencode:2" if "codex" in ok else "deepseek:2,pickle:1"
            tag = "ai" + dt.datetime.now().strftime("%m%d%H%M")
            print(f"{stamp} extracting {n} remaining articles with {agents} (tag {tag})", flush=True)
            subprocess.run([PY, "pipeline/run_extraction.py", "--urls", "data/raw/remaining_urls.csv", "--tag", tag,
                            "--agents", agents, "--final"], cwd=ROOT)
            subprocess.run([PY, "pipeline/run_all.py"], cwd=ROOT)
            if "codex" in ok:  # investor type/HQ enrichment (cached; only new investors are sent)
                subprocess.run([PY, "pipeline/enrich_investors.py", "800"], cwd=ROOT)
                subprocess.run([PY, "pipeline/run_all.py"], cwd=ROOT)
            continue
        time.sleep(600)


if __name__ == "__main__":
    main()
