"""Compare Origination Radar configurations on the same rolling walk-forward backtest.

Questions:
  A) label = any primary round (equity + debt)   vs   equity rounds only (what hires a banker)
  B) train on all snapshots from 2021             vs   only from 2023 (when coverage is dense)
Output: data/processed/radar_experiments.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from lib import radar  # noqa: E402

configs = {
    "equity+debt, from 2021": (("equity", "debt"), None),
    "equity only, from 2021": (("equity",), None),
    "equity+debt, from 2023": (("equity", "debt"), "2023-01-01"),
    "equity only, from 2023": (("equity",), "2023-01-01"),
}
results = {}
for name, (labels, start) in configs.items():
    radar.LABEL_TYPES, radar.TRAIN_START = labels, start
    res = radar.run()
    results[name] = res.backtest.get("summary", {})
    print(f"{name:26s} {results[name]}", flush=True)
(ROOT / "data" / "processed" / "radar_experiments.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
