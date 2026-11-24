"""Which free OpenCode models are responsive right now? (60 s timeout each, run in parallel)"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import run_extraction as r  # noqa: E402


def probe(item):
    name, model = item
    t = time.time()
    try:
        p = r.run_killable(["opencode", "run", "-m", model, '"Reply with exactly: OK"'], timeout=60)
        return name, "OK" in (p.stdout or ""), round(time.time() - t)
    except Exception as e:  # noqa: BLE001
        return name, False, str(e)[:50]


with ThreadPoolExecutor(8) as ex:
    for res in ex.map(probe, r.FREE_MODELS.items()):
        print(res, flush=True)
