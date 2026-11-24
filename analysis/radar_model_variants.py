"""Compare model families for the Origination Radar on the same rolling backtest."""
import json
import sys
from pathlib import Path

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from lib import radar  # noqa: E402

variants = {
    "GBM (current)": radar._model,
    "GBM regularised": lambda: HistGradientBoostingClassifier(max_iter=200, learning_rate=0.03, max_leaf_nodes=7,
                                                              min_samples_leaf=150, l2_regularization=5.0,
                                                              random_state=7),
    "Logistic regression": lambda: make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                                 LogisticRegression(C=0.3, max_iter=2000)),
}
out = {}
for name, factory in variants.items():
    radar._model = factory
    s = radar.run().backtest.get("summary", {})
    out[name] = s
    print(f"{name:22s} {s}", flush=True)
(ROOT / "data" / "processed" / "radar_model_variants.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
