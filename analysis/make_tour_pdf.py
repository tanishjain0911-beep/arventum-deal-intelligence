"""Build docs/Arventum_Deal_Intelligence_Product_Tour.pdf from page screenshots (a backup for live demos)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "docs" / "screenshots"
OUT = ROOT / "docs" / "Arventum_Deal_Intelligence_Product_Tour.pdf"
PAGES = [
    ("home", "Home: five engines mapped to Arventum's deal process, plus data quality at a glance"),
    ("pulse", "Market Pulse: capital and rounds per month, sector momentum, round-size benchmarks, latest deals"),
    ("radar", "Origination Radar: backtested 'who raises next' list with reasons and a weekly brief"),
    ("match", "Investor Matchmaker: ranked investors for a client profile, with the evidence"),
    ("buyers", "Buyer Mapping: serial acquirers of Indian tech companies by sector"),
    ("price", "Price Finder: football-field valuation from listed peers, regression and private rounds"),
    ("lookup", "Company Lookup: one company's deals, backers, financials and Radar score"),
    ("quality", "Data & Quality: agent agreement, rule checks, coverage, audit trail"),
    ("built", "How it was built: the AI team and the engineering log"),
]
W = 1400
try:
    font = ImageFont.truetype("segoeui.ttf", 26)
    big = ImageFont.truetype("segoeuib.ttf", 40)
except OSError:
    font = big = ImageFont.load_default()

pages = []
cover = Image.new("RGB", (W, 900), "#0d1b2a")
d = ImageDraw.Draw(cover)
d.text((80, 320), "Arventum Deal Intelligence", font=big, fill="white")
d.text((80, 390), "Product tour: AI-native deal intelligence for Indian technology deals", font=font, fill="#c3c2b7")
d.text((80, 440), "Built from public data by a team of AI agents", font=font, fill="#c3c2b7")
pages.append(cover)
for name, caption in PAGES:
    f = SHOTS / f"{name}.png"
    if not f.exists():
        continue
    img = Image.open(f).convert("RGB")
    img = img.crop((240, 0, img.width, img.height))  # drop the sidebar for readability
    header = 90
    page = Image.new("RGB", (img.width, img.height + header), "white")
    ImageDraw.Draw(page).text((40, 28), caption, font=font, fill="#0d1b2a")
    page.paste(img, (0, header))
    pages.append(page)
pages[0].save(OUT, save_all=True, append_images=pages[1:], resolution=110)
print(f"wrote {OUT} ({len(pages)} pages, {OUT.stat().st_size / 1e6:.1f} MB)")
