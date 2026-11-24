// Landing page: every figure comes from data/summary.json at load time.
const el = id => document.getElementById(id);
const num = n => (n == null || isNaN(n)) ? "—" : Math.round(n).toLocaleString("en-IN");
const pct = x => (x == null || isNaN(x)) ? "—" : `${Math.round(x * 100)}%`;
const mon = iso => iso ? new Date(iso + "T00:00:00").toLocaleDateString("en-GB", { month: "long", year: "numeric" }) : "—";

function put(id, text) { const n = el(id); if (n) n.textContent = text; }

async function fill() {
  let s;
  try {
    const res = await fetch("data/summary.json", { cache: "no-store" });
    if (!res.ok) throw new Error(res.status);
    s = await res.json();
  } catch (e) {
    document.querySelectorAll("[data-figure], #h-deals, #h-range").forEach(n => { n.textContent = "—"; });
    return;
  }
  const r = s.radar?.summary || {};

  put("h-deals", num(s.tables?.deals));
  put("h-range", `${mon(s.first)} – ${mon(s.last)}`);

  put("f-deals", num(s.tables?.deals));
  put("f-deals-sub", `${num(s.tables?.sources)} articles read, ${num(s.companies)} companies and ${num(s.investors)} investors named.`);

  put("f-companies", num(s.companies));
  put("f-companies-sub", `${num(s.tables?.financials)} annual financial records from public filings coverage.`);

  put("f-radar", pct(r.mean_precision_top100));
  put("f-radar-sub", `of its top 100 picks raised within 12 months, against ${pct(r.mean_precision_top100_heuristic)} for a simple timing rule and ${pct(r.mean_base_rate)} for random picking.`);

  put("f-asof", mon(s.last));

  put("f-investors", num(s.investors));
  put("f-investors-sub", `funds, angels and corporate backers named across ${num(s.tables?.deal_investors)} deal participations.`);

  document.title = `Deal Intelligence: ${num(s.tables?.deals)} Indian technology deals, traced and tested`;
}

function reveal() {
  const items = document.querySelectorAll(".figures, .tools, .closing");
  if (!("IntersectionObserver" in window) || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    items.forEach(n => n.classList.add("in"));
    return;
  }
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  items.forEach(n => io.observe(n));
}

fill();
reveal();
