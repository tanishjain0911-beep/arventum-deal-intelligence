"""Step 3: multi-agent extraction.

Splits articles into batches and farms them out in parallel to
  - Codex CLI   (ChatGPT Plus, strict JSON schema enforced)
  - OpenCode    (ChatGPT Plus via OpenCode, JSON parsed from reply)
Each batch result is cached in data/extracted/<agent>/batch_NNNN.json, so the
run can be resumed. A --crosscheck mode sends the same batches to both
agents to measure agreement.

Usage:
  python pipeline/run_extraction.py                 # all batches
  python pipeline/run_extraction.py --limit 2       # first 2 batches (smoke test)
  python pipeline/run_extraction.py --crosscheck 5  # 5 batches to BOTH agents
"""
import argparse
import json
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sectors import ALL_SECTORS, STAGES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "data" / "raw" / "articles.jsonl"
BATCH_DIR = ROOT / "data" / "batches"
OUT_DIR = ROOT / "data" / "extracted"
SCHEMA = ROOT / "pipeline" / "extract_schema.json"
PROMPT = (
    (ROOT / "pipeline" / "extract_prompt.md").read_text(encoding="utf-8")
    .replace("{SECTORS}", ", ".join(ALL_SECTORS))
    .replace("{STAGES}", ", ".join(STAGES))
)
BATCH_SIZE = 30
OPENCODE_MODEL = "openai/gpt-5.6-terra"
CODEX_MODEL = "gpt-5.6-terra"   # lighter model: plenty for extraction, saves ChatGPT Plus quota
lock = threading.Lock()


def log(msg):
    with lock:
        print(msg, flush=True)


def _articles_in_order():
    """Successfully downloaded articles, in URL-list order, up to the first one not yet downloaded.
    Lets extraction run while the downloader is still working."""
    import csv
    import hashlib
    urls = URLS_FILE[0]
    cache = ROOT / "data" / "raw" / "articles"
    kinds = {"deal", "acquisition", "financials", "report"}
    out = []
    for row in csv.DictReader(urls.open(encoding="utf-8")):
        if row["kind"] not in kinds:
            continue
        p = cache / (hashlib.md5(row["url"].encode()).hexdigest() + ".json")
        if not p.exists():
            break
        a = json.loads(p.read_text(encoding="utf-8"))
        if a.get("error"):
            if PERMANENT.match(a["error"]):
                continue  # page gone / forbidden: skip, never block the queue
            break
        if a.get("title") and a.get("kind") != "report":
            out.append(a)
    return out


def make_batches():
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    arts = _articles_in_order()
    batches = []
    for i in range(0, len(arts), BATCH_SIZE):
        chunk = arts[i : i + BATCH_SIZE]
        if len(chunk) < BATCH_SIZE and not FINAL[0]:
            break  # wait until the batch is full (download still running)
        path = BATCH_DIR / f"{TAG[0]}batch_{i // BATCH_SIZE:04d}.jsonl"
        if not path.exists():
            with path.open("w", encoding="utf-8") as f:
                for a in chunk:
                    if is_roundup(a["url"]):
                        continue  # weekly/monthly round-ups are parsed by rules, not sent to the AI
                    slim = {k: a.get(k) for k in ("url", "date", "title", "description", "company_kw")}
                    # financial stories mention the loss/profit later in the text -> send more of it
                    limit = 2000 if a.get("kind") == "financials" or re.search(r"revenue|loss|profit|fy\d\d",
                                                                                 (a.get("title") or "").lower()) else 700
                    slim["body"] = " ".join(a.get("body") or [])[:limit]
                    f.write(json.dumps(slim, ensure_ascii=False) + "\n")
        batches.append(path)
    return batches


FINAL = [False]


def is_roundup(url: str) -> bool:
    return bool(re.search(r"this-week|weekly-funding|monthly-funding|funding-galore", url))


PERMANENT = re.compile(r"http (40[0-4]|410|451)")
URLS_FILE = [ROOT / "data" / "raw" / "entrackr_urls.csv"]
TAG = [""]   # batch-name prefix for additional URL lists, e.g. "hist_"


def parse_json(text: str):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start : end + 1])


CALL_TIMEOUT = 360  # seconds per batch; a healthy call takes 1-4 minutes


class _Result:
    def __init__(self, stdout, stderr, returncode):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode


def run_killable(cmd, input_text=None, cwd=None, timeout=CALL_TIMEOUT):
    """Run a CLI agent; on timeout kill the WHOLE process tree.
    (subprocess.run(shell=True, timeout=...) only kills the shell, leaving a hung agent running forever -
    which is how the free models stalled the pipeline overnight.)"""
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                         errors="replace", shell=True, cwd=cwd)
    try:
        out, err = p.communicate(input=input_text, timeout=timeout)
        return _Result(out, err, p.returncode)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        p.communicate()
        raise RuntimeError(f"agent call timed out after {timeout}s (process tree killed)")


def run_codex(batch: Path, out: Path):
    data = batch.read_text(encoding="utf-8")
    prompt = PROMPT + "\n\nARTICLES (JSON lines):\n" + data
    cmd = [
        "codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only",
        "-m", CODEX_MODEL, "-c", 'model_reasoning_effort="low"',
        "--output-schema", str(SCHEMA), "-o", str(out), "-",
    ]
    p = run_killable(cmd, input_text=prompt)
    if not out.exists() or out.stat().st_size == 0:
        raise RuntimeError(f"codex failed: {(p.stderr or '')[-300:]} {(p.stdout or '')[-200:]}")
    parse_json(out.read_text(encoding="utf-8"))  # validate


def run_opencode(batch: Path, out: Path, model: str = None):
    # Newlines can't pass safely through cmd.exe arguments, so the long
    # instructions travel as an attached file and the message stays one line.
    instr = BATCH_DIR / "_instructions.md"
    if not instr.exists():
        instr.write_text(PROMPT, encoding="utf-8")
    msg = ("Follow the instructions in _instructions.md exactly for the articles in the other attached "
           "file (JSON lines). Do not use any tools and do not edit files. Reply with the JSON object only.")
    # message must come BEFORE -f: the -f option is greedy and would swallow it as a file name
    cmd = ["opencode", "run", "-m", model or OPENCODE_MODEL, f'"{msg}"', "-f", str(instr), "-f", str(batch)]
    p = run_killable(cmd, cwd=str(BATCH_DIR))
    if re.search(r"usage limit", (p.stdout or "") + (p.stderr or ""), re.I):
        raise RuntimeError("usage limit has been reached")
    obj = parse_json(p.stdout)
    out.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


from functools import partial  # noqa: E402

# free OpenCode-hosted models (used when the ChatGPT Plus quota is exhausted)
FREE_MODELS = {
    "pickle": "opencode/big-pickle",
    "deepseek": "opencode/deepseek-v4.1-flash-free",
    "nemotron": "opencode/nemotron-3.5-super-vl-free",
    "mimo": "opencode/mimo-v2.6-flash-free",
    "beam": "opencode/beam-free",
    "hy4": "opencode/hy4-flash-free",
    "flint": "opencode/flint-40b-free",
    "lightning": "opencode/nemotron-3.5-lightning-free",
}
AGENTS = {"codex": run_codex, "opencode": run_opencode,
          **{k: partial(run_opencode, model=v) for k, v in FREE_MODELS.items()}}


QUOTA_FLAG = ROOT / "data" / "processed" / "_gpt_quota_exhausted"
QUOTA_COOLDOWN = 45 * 60          # after this long, try the GPT agents again
GPT_AGENTS = {"codex", "opencode"}
FALLBACK = ["deepseek", "pickle"]   # best free models by measured agreement (analysis/model_eval.py)


def quota_exhausted() -> bool:
    import time
    return QUOTA_FLAG.exists() and time.time() - QUOTA_FLAG.stat().st_mtime < QUOTA_COOLDOWN


def job(agent: str, batch: Path, any_agent_ok: bool = True):
    if any_agent_ok and any((OUT_DIR / a / (batch.stem + ".json")).exists() for a in AGENTS):
        return agent, batch.stem, "cached"
    for attempt in range(3):
        use = agent
        if agent in GPT_AGENTS and any_agent_ok and quota_exhausted():
            use = FALLBACK[(hash(batch.stem) + attempt) % len(FALLBACK)]  # automatic free-model fallback
        out_dir = OUT_DIR / use
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / (batch.stem + ".json")
        if out.exists():
            return use, batch.stem, "cached"
        try:
            AGENTS[use](batch, out)
            n = len(json.loads(out.read_text(encoding="utf-8"))["records"])
            log(f"[{use}] {batch.stem}: {n} records")
            return use, batch.stem, "ok"
        except Exception as e:  # noqa: BLE001
            if out.exists():
                out.unlink()
            msg = str(e)
            if use in GPT_AGENTS and re.search(r"usage limit", msg, re.I):
                QUOTA_FLAG.write_text("exhausted", encoding="utf-8")
                log(f"[{use}] ChatGPT quota exhausted -> switching to free models for {QUOTA_COOLDOWN // 60} min")
            log(f"[{use}] {batch.stem}: attempt {attempt + 1} failed: {msg[:200]}")
    return agent, batch.stem, "failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--crosscheck", type=int)
    ap.add_argument("--codex-workers", type=int, default=3)
    ap.add_argument("--opencode-workers", type=int, default=2)
    ap.add_argument("--final", action="store_true", help="also process the last partial batch")
    ap.add_argument("--agents", help="override worker pool, e.g. 'pickle:2,deepseek:2'")
    ap.add_argument("--only", help="comma list of batch stems to (re)run with --agents (quality tests)")
    ap.add_argument("--urls", help="URL csv (default data/raw/entrackr_urls.csv)")
    ap.add_argument("--tag", default="", help="batch name prefix for this URL list, e.g. hist")
    args = ap.parse_args()
    FINAL[0] = args.final
    if args.urls:
        URLS_FILE[0] = ROOT / args.urls
    TAG[0] = f"{args.tag}_" if args.tag else ""

    batches = make_batches()
    log(f"{len(batches)} batches of up to {BATCH_SIZE} articles")
    if args.only:
        wanted = set(args.only.split(","))
        names = [a.split(":")[0] for a in args.agents.split(",")]
        jobs = [(a, b, False) for b in batches if b.stem in wanted for a in names]
        workers = max(1, len(jobs))
        with ThreadPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(lambda j: job(*j), jobs))
        log(f"done: {results}")
        return
    if args.agents:
        pattern = []
        for spec in args.agents.split(","):
            name, n = (spec.split(":") + ["1"])[:2]
            pattern += [name] * int(n)
        jobs = [(pattern[i % len(pattern)], b, True) for i, b in enumerate(batches[: args.limit] if args.limit
                                                                           else batches)]
        with ThreadPoolExecutor(max_workers=len(pattern)) as ex:
            results = list(ex.map(lambda j: job(*j), jobs))
        failed = [r for r in results if r[2] == "failed"]
        log(f"done: {len(results) - len(failed)} ok, {len(failed)} failed")
        for f in failed:
            log(f"  failed: {f}")
        return
    if args.crosscheck:
        # spread the cross-check sample across the whole time range
        step = max(1, len(batches) // args.crosscheck)
        jobs = [(a, b, False) for b in batches[::step][: args.crosscheck] for a in AGENTS]
    else:
        if args.limit:
            batches = batches[: args.limit]
        # weighted round-robin so faster agent gets proportionally more work
        pattern = ["codex"] * args.codex_workers + ["opencode"] * args.opencode_workers
        jobs = [(pattern[i % len(pattern)], b, True) for i, b in enumerate(batches)]

    workers = args.codex_workers + args.opencode_workers
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda j: job(*j), jobs))
    failed = [r for r in results if r[2] == "failed"]
    log(f"done: {len(results) - len(failed)} ok, {len(failed)} failed")
    for f in failed:
        log(f"  failed: {f}")


if __name__ == "__main__":
    main()
