"""Listed comparable companies for valuation benchmarking (Yahoo Finance, free).

Each ticker is mapped to a sector from sectors.py. We store size, growth,
margins and the trading multiples bankers use (EV/Revenue, EV/EBITDA).
Output: data/processed/comparables.csv
"""
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "comparables.csv"

UNIVERSE = {
    # ---- India listed tech / new-age
    "INFY.NS": "IT Services", "TCS.NS": "IT Services", "WIPRO.NS": "IT Services", "HCLTECH.NS": "IT Services",
    "TECHM.NS": "IT Services", "LTIM.NS": "IT Services", "PERSISTENT.NS": "Digital Engineering",
    "COFORGE.NS": "IT Services", "KPITTECH.NS": "Digital Engineering", "TATAELXSI.NS": "Digital Engineering",
    "LTTS.NS": "Digital Engineering", "CYIENT.NS": "Digital Engineering", "HAPPSTMNDS.NS": "IT Services",
    "LATENTVIEW.NS": "Data Infrastructure", "TANLA.NS": "SaaS", "ROUTE.NS": "SaaS", "AFFLE.NS": "Consumer Internet",
    "NAUKRI.NS": "Consumer Internet", "ETERNAL.NS": "Consumer Internet", "SWIGGY.NS": "Consumer Internet",
    "NYKAA.NS": "E-commerce & D2C", "PAYTM.NS": "FinTech & Payments", "POLICYBZR.NS": "FinTech & Payments",
    "ZAGGLE.NS": "FinTech & Payments", "DELHIVERY.NS": "Logistics & Mobility", "MAPMYINDIA.NS": "Data Infrastructure",
    "NAZARA.NS": "Media & Gaming", "DATAPATTNS.NS": "DefenceTech", "ZENTEC.NS": "DefenceTech",
    "BEL.NS": "DefenceTech", "IDEAFORGE.NS": "DefenceTech", "OLAELEC.NS": "EV & Auto",
    "NEWGEN.NS": "Enterprise Software", "INTELLECT.NS": "Enterprise Software", "NUCLEUS.NS": "Digital Banking",
    "QUICKHEAL.NS": "Cybersecurity", "KAYNES.NS": "Semiconductors", "DIXON.NS": "Industrial Tech",
    "SUZLON.NS": "Energy Transition", "WAAREEENER.NS": "Energy Transition", "PREMIERENE.NS": "Energy Transition",
    "INOXWIND.NS": "ClimateTech", "IXIGO.NS": "Travel & Hospitality", "EASEMYTRIP.NS": "Travel & Hospitality",
    "CARTRADE.NS": "Consumer Internet", "JUSTDIAL.NS": "Consumer Internet", "RATEGAIN.NS": "SaaS",
    "MEDPLUS.NS": "HealthTech", "FIRSTCRY.NS": "E-commerce & D2C",
    # ---- Global benchmarks
    "FRSH": "SaaS", "CRM": "SaaS", "NOW": "Enterprise Software", "HUBS": "SaaS", "TEAM": "Developer Tools",
    "GTLB": "Developer Tools", "DDOG": "Cloud Infrastructure", "SNOW": "Data Infrastructure", "MDB": "Data Infrastructure",
    "NET": "Cloud Infrastructure", "CRWD": "Cybersecurity", "PANW": "Cybersecurity", "ZS": "Cybersecurity",
    "S": "Cybersecurity", "OKTA": "Cybersecurity", "PLTR": "Artificial Intelligence", "AI": "Artificial Intelligence",
    "PATH": "Automation & Robotics", "SYM": "Automation & Robotics", "NVDA": "Semiconductors", "AMD": "Semiconductors",
    "ARM": "Semiconductors", "PYPL": "FinTech & Payments", "XYZ": "FinTech & Payments", "AFRM": "FinTech & Payments",
    "SOFI": "Digital Banking", "NU": "Digital Banking", "SHOP": "E-commerce & D2C", "RKLB": "SpaceTech",
    "ASTS": "SpaceTech", "KTOS": "DefenceTech", "AVAV": "DefenceTech", "ENPH": "Energy Transition",
    "FSLR": "Energy Transition", "TSLA": "EV & Auto", "IONQ": "DeepTech", "ROK": "Industrial Tech",
    "EPAM": "IT Services", "GLOB": "Digital Engineering", "DOCS": "HealthTech", "DUOL": "EdTech",
    "UBER": "Logistics & Mobility", "ABNB": "Travel & Hospitality",
}


def main():
    rows = []
    for t, sector in UNIVERSE.items():
        try:
            info = yf.Ticker(t).info
            ev, rev = info.get("enterpriseValue"), info.get("totalRevenue")
            ebitda = info.get("ebitda")
            rows.append({
                "ticker": t, "name": info.get("shortName") or info.get("longName") or t, "sector": sector,
                "market": "India" if t.endswith(".NS") else "Global", "currency": info.get("currency"),
                "market_cap": info.get("marketCap"), "enterprise_value": ev, "revenue": rev,
                "revenue_growth": info.get("revenueGrowth"), "gross_margin": info.get("grossMargins"),
                "ebitda_margin": (ebitda / rev) if ebitda and rev else None,
                "ev_revenue": (ev / rev) if ev and rev and rev > 0 else None,
                "ev_ebitda": (ev / ebitda) if ev and ebitda and ebitda > 0 else None,
            })
            print(f"ok   {t:15s} EV/Rev={rows[-1]['ev_revenue']}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"fail {t}: {str(e)[:80]}", flush=True)
        time.sleep(0.6)
    df = pd.DataFrame(rows)
    df["as_of"] = pd.Timestamp.today().date()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"saved {len(df)} comparables, {df.ev_revenue.notna().sum()} with EV/Revenue")


if __name__ == "__main__":
    main()
