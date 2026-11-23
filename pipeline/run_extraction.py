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
lock = threading.Lock()


def log(msg):
    with lock:
        print(msg, flush=True)


def make_batches():
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    arts = [json.loads(l) for l in ARTICLES.open(encoding="utf-8")]
    arts = [a for a in arts if not a.get("error") and a.get("title")]
    batches = []
    for i in range(0, len(arts), BATCH_SIZE):
        path = BATCH_DIR / f"batch_{i // BATCH_SIZE:04d}.jsonl"
        if not path.exists():
            with path.open("w", encoding="utf-8") as f:
                for a in arts[i : i + BATCH_SIZE]:
                    slim = {k: a.get(k) for k in ("url", "date", "title", "description", "company_kw")}
                    slim["body"] = " ".join(a.get("body") or [])[:1500]
                    f.write(json.dumps(slim, ensure_ascii=False) + "\n")
        batches.append(path)
    return batches


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
        "-c", 'model_reasoning_effort="low"',
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


def job(agent: str, batch: Path):
    out_dir = OUT_DIR / agent
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (batch.stem + ".json")
    if out.exists():
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
    args = ap.parse_args()

    batches = make_batches()
    log(f"{len(batches)} batches of up to {BATCH_SIZE} articles")
    if args.crosscheck:
        jobs = [(a, b) for b in batches[: args.crosscheck] for a in AGENTS]
    else:
        if args.limit:
            batches = batches[: args.limit]
        # weighted round-robin so faster agent gets proportionally more work
        pattern = ["codex"] * args.codex_workers + ["opencode"] * args.opencode_workers
        jobs = [(pattern[i % len(pattern)], b) for i, b in enumerate(batches)]

    workers = args.codex_workers + args.opencode_workers
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda j: job(*j), jobs))
    failed = [r for r in results if r[2] == "failed"]
    log(f"done: {len(results) - len(failed)} ok, {len(failed)} failed")
    for f in failed:
        log(f"  failed: {f}")


if __name__ == "__main__":
    main()
