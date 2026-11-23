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
                    slim["body"] = " ".join(a.get("body") or [])[:1000]
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


def run_codex(batch: Path, out: Path):
    data = batch.read_text(encoding="utf-8")
    prompt = PROMPT + "\n\nARTICLES (JSON lines):\n" + data
    cmd = [
        "codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only",
        "-m", CODEX_MODEL, "-c", 'model_reasoning_effort="low"',
        "--output-schema", str(SCHEMA), "-o", str(out), "-",
    ]
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                       timeout=900, shell=True)
    if not out.exists():
        raise RuntimeError(f"codex failed: {p.stderr[-300:]}")
    parse_json(out.read_text(encoding="utf-8"))  # validate


def run_opencode(batch: Path, out: Path):
    # Newlines can't pass safely through cmd.exe arguments, so the long
    # instructions travel as an attached file and the message stays one line.
    instr = BATCH_DIR / "_instructions.md"
    if not instr.exists():
        instr.write_text(PROMPT, encoding="utf-8")
    msg = ("Follow the instructions in _instructions.md exactly for the articles in the other attached "
           "file (JSON lines). Do not use any tools and do not edit files. Reply with the JSON object only.")
    # message must come BEFORE -f: the -f option is greedy and would swallow it as a file name
    cmd = ["opencode", "run", "-m", OPENCODE_MODEL, f'"{msg}"', "-f", str(instr), "-f", str(batch)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=900,
                       shell=True, cwd=str(BATCH_DIR))
    obj = parse_json(p.stdout)
    out.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


AGENTS = {"codex": run_codex, "opencode": run_opencode}


def job(agent: str, batch: Path, any_agent_ok: bool = True):
    out_dir = OUT_DIR / agent
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (batch.stem + ".json")
    if out.exists() or (any_agent_ok and any((OUT_DIR / a / (batch.stem + ".json")).exists() for a in AGENTS)):
        return agent, batch.stem, "cached"
    for attempt in range(2):
        try:
            AGENTS[agent](batch, out)
            n = len(json.loads(out.read_text(encoding="utf-8"))["records"])
            log(f"[{agent}] {batch.stem}: {n} records")
            return agent, batch.stem, "ok"
        except Exception as e:  # noqa: BLE001
            if out.exists():
                out.unlink()
            log(f"[{agent}] {batch.stem}: attempt {attempt + 1} failed: {str(e)[:200]}")
    return agent, batch.stem, "failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--crosscheck", type=int)
    ap.add_argument("--codex-workers", type=int, default=3)
    ap.add_argument("--opencode-workers", type=int, default=2)
    ap.add_argument("--final", action="store_true", help="also process the last partial batch")
    ap.add_argument("--urls", help="URL csv (default data/raw/entrackr_urls.csv)")
    ap.add_argument("--tag", default="", help="batch name prefix for this URL list, e.g. hist")
    args = ap.parse_args()
    FINAL[0] = args.final
    if args.urls:
        URLS_FILE[0] = ROOT / args.urls
    TAG[0] = f"{args.tag}_" if args.tag else ""

    batches = make_batches()
    log(f"{len(batches)} batches of up to {BATCH_SIZE} articles")
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
