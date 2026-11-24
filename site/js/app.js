import { load, deals, esc, h, usd, inr, pct, int, date, month, stageLabel, quantile, median, exhibit, table, bindTips,
  barChart, hbarChart, rangeChart, lineChart } from "./kit.js";

const SECTIONS = [
  ["summary", "Summary", "The deal book at a glance"],
  ["market", "Market", "Capital, sectors, round sizes"],
  ["radar", "Origination", "Who is likely to raise next"],
  ["investors", "Investors", "Who would back a client"],
  ["buyers", "Buyers", "Who acquires companies like it"],
  ["valuation", "Valuation", "What a company is worth"],
  ["company", "Company", "One company, all its deals"],
  ["method", "Method", "Sources, checks, accuracy"],
];
const $main = document.getElementById("main");
const state = { market: { sector: "focus", months: 12 }, radar: { sector: "focus", stage: "any", min: 1, sel: null },
  inv: { sector: "FinTech & Payments", stage: "series-a", amount: 10, lead: true, foreign: false, sel: null },
  buy: { sector: "FinTech & Payments" }, val: { sector: "SaaS", rev: 150, growth: 50, margin: 10, gross: null, scope: "Both" },
  company: null };

// ---------- shell ----------
function renderTabs(active) {
  document.getElementById("tabs").innerHTML = SECTIONS.map(([id, name, sub], i) =>
    `<a class="tab ${id === active ? "on" : ""}" href="#/${id}" ${id === active ? 'aria-current="page"' : ""}><b>${i + 1}</b><span>${name}</span><small>${sub}</small></a>`).join("");
}
async function renderFoot() {
  const s = await load("summary");
  document.getElementById("spinefoot").innerHTML = `${int(s.tables.deals)} deals · ${month(s.first)} to ${month(s.last)}<br>Public sources only. Decision support, not investment advice.`;
}
const sourceLine = (txt, link = "#/method") => `<b>Source:</b> ${txt} <a href="${link}">Method</a>`;
const sectorOptions = (all, cur, extra = []) => [...extra, ...all.map(s => [s, s])].map(([v, l]) => `<option value="${esc(v)}" ${v === cur ? "selected" : ""}>${esc(l)}</option>`).join("");
const STAGES = ["pre-seed", "seed", "pre-series-a", "series-a", "series-b", "series-c", "series-d", "series-e+", "growth", "pre-ipo"];
const STAGE_RANK = Object.fromEntries(STAGES.map((s, i) => [s, i]));

// ---------- 1 summary ----------
async function viewSummary() {
  const [s, ds] = await Promise.all([load("summary"), deals()]);
  const prim = ds.filter(d => d.type === "equity" || d.type === "debt");
  const q = {};
  prim.forEach(d => { const [y, m] = d.date.split("-"); const k = `${y} Q${Math.floor((+m - 1) / 3) + 1}`; q[k] = (q[k] || 0) + (d.usd_m || 0); });
  const keys = Object.keys(q).sort();
  const items = keys.map(k => ({ x: k.replace(" Q1", "").includes("Q") ? "" : k.slice(0, 4), v: q[k], tip: `${k}: ${usd(q[k])} raised` }));
  keys.forEach((k, i) => items[i].x = k.endsWith("Q1") ? k.slice(0, 4) : "");
  const r = s.radar.summary || {}, m = s.matching || {}, cov = s.coverage || {}, cc = s.crosscheck || {};
  return h`<div class="sechead"><div><h1><b>1</b>Summary</h1><p>A sourced, quality-checked record of Indian technology funding rounds and acquisitions, with tools that map to each step of a sell-side or fundraising mandate.</p></div>
    <div class="controls"><a class="btn" href="#/radar">Open the Origination Radar</a><a class="btn ghost" href="#/company">Look up a company</a></div></div>
  <div class="grid">
    ${exhibit({ n: "1.1", title: "Capital raised by Indian tech companies, per quarter", cls: "c8",
      body: `<p class="lede">${int(s.tables.deals)} deals since ${new Date(s.first).getFullYear()}, <em>each traced to the article it came from.</em></p>${barChart(items, { fmt: v => usd(v, 0), height: 300 })}`,
      source: sourceLine(`${int(s.tables.sources)} public articles (Entrackr, Inc42), extracted by AI agents and checked by rules; equity and venture debt rounds. Latest quarter may be incomplete.`) })}
    ${exhibit({ n: "1.2", title: "Measured, not claimed", sub: "Every model is tested on outcomes it never saw.", cls: "c4",
      body: `<ul class="results-list">
        <li><span class="what">Origination Radar: its top 100 picks that raised within 12 months</span><span class="fig">${pct(r.mean_precision_top100)}</span><span class="vs">vs ${pct(r.mean_precision_top100_heuristic)} for the "raised 18–24 months ago" rule; ${r.mean_lift_top100}× random</span></li>
        <li><span class="what">Investor Matchmaker: a real investor in its top 10</span><span class="fig">${pct(m.model_hit_rate?.["10"])}</span><span class="vs">vs ${pct(m.baseline_hit_rate?.["10"])} for a "most active investors" list; ${m.test_deals} rounds</span></li>
        <li><span class="what">Two AI agents agree on the company</span><span class="fig">${cc.company}%</span><span class="vs">${s.crosscheck_n} articles read independently by both</span></li>
        <li><span class="what">Reported startup capital captured</span><span class="fig">${cov.usd_recall_pct}%</span><span class="vs">${cov.deal_recall_pct}% of deals by count; small undisclosed rounds are the gap</span></li></ul>`,
      source: sourceLine("walk-forward backtests and quality checks in this repository.") })}
    ${exhibit({ n: "1.3", title: "What is in this book", cls: "c12",
      body: `<table><thead><tr><th>Section</th><th>Question it answers</th><th>Built on</th></tr></thead><tbody>
        ${[["2 Market", "What is happening in each sector right now?", "capital, deal counts and round sizes by sector and stage"],
           ["3 Origination", "Which private companies will raise in the next 12 months?", "a logistic model on funding history, backtested over four quarters"],
           ["4 Investors", "Which funds are most likely to back this client?", "each investor's sector, stage and cheque history, recency-weighted"],
           ["5 Buyers", "Who acquires companies like this one?", `${int(s.acquisitions)} acquisitions with named buyers`],
           ["6 Valuation", "What is a reasonable value range?", "listed peers, a cross-validated regression and Indian private rounds"],
           ["7 Company", "What has this company raised, from whom?", `${int(s.companies)} companies, ${int(s.tables.financials)} annual financial records`]]
          .map(([a, b, c]) => `<tr><td><a href="#/${SECTIONS[+a[0] - 1][0]}">${a}</a></td><td>${b}</td><td class="muted">${c}</td></tr>`).join("")}</tbody></table>` })}
  </div>`;
}

// ---------- 2 market ----------
async function viewMarket() {
  const [s, ds] = await Promise.all([load("summary"), deals()]);
  const st = state.market, focus = new Set(s.focus_sectors);
  const pick = d => st.sector === "all" ? true : st.sector === "focus" ? focus.has(d.sector) : d.sector === st.sector;
  const prim = ds.filter(d => (d.type === "equity" || d.type === "debt"));
  const sel = prim.filter(pick), end = new Date(s.last);
  const cut = new Date(end); cut.setMonth(cut.getMonth() - st.months);
  const recent = sel.filter(d => new Date(d.date) > cut);
  const byQ = {}; sel.forEach(d => { const [y, m] = d.date.split("-"); const k = `${y} Q${Math.floor((+m - 1) / 3) + 1}`; (byQ[k] ||= { v: 0, n: 0 }); byQ[k].v += d.usd_m || 0; byQ[k].n++; });
  const qk = Object.keys(byQ).sort();
  const capItems = qk.map(k => ({ x: k.endsWith("Q1") ? k.slice(0, 4) : "", v: byQ[k].v, tip: `${k}: ${usd(byQ[k].v)} across ${byQ[k].n} rounds` }));
  const cntItems = qk.map(k => ({ x: k.endsWith("Q1") ? k.slice(0, 4) : "", v: byQ[k].n, tip: `${k}: ${byQ[k].n} rounds` }));
  // sector momentum (always market-wide, last 6m vs prior 6m)
  const six = new Date(end); six.setMonth(six.getMonth() - 6); const twelve = new Date(end); twelve.setMonth(twelve.getMonth() - 12);
  const agg = {}; prim.forEach(d => { if (d.sector === "Unclassified" || !d.sector) return; const t = new Date(d.date);
    const a = (agg[d.sector] ||= { now: 0, prev: 0, n: 0 }); if (t > six) { a.now += d.usd_m || 0; a.n++; } else if (t > twelve) a.prev += d.usd_m || 0; });
  const heat = Object.entries(agg).filter(([, a]) => a.n >= 2).sort((a, b) => b[1].now - a[1].now).slice(0, 18)
    .map(([k, a]) => ({ label: k, v: a.now, alt: !focus.has(k), tip: `${k}: ${usd(a.now)} in 6 months (${a.prev ? ((a.now / a.prev - 1) * 100).toFixed(0) + "% vs prior 6m" : "new"}), ${a.n} rounds` }));
  // stage benchmarks (2 years)
  const two = new Date(end); two.setFullYear(two.getFullYear() - 2);
  const bench = STAGES.map(stg => { const v = sel.filter(d => d.stage === stg && d.usd_m && new Date(d.date) > two).map(d => d.usd_m);
    return v.length >= 3 ? { label: stageLabel(stg), lo: quantile(v, .25), mid: median(v), hi: quantile(v, .75), n: v.length,
      tip: `${stageLabel(stg)}: middle half ${usd(quantile(v, .25))}–${usd(quantile(v, .75))}, median ${usd(median(v))} (${v.length} rounds)` } : null; }).filter(Boolean);
  const label = st.sector === "focus" ? "Arventum's 20 focus sectors" : st.sector === "all" ? "all sectors" : st.sector;
  const html = h`<div class="sechead"><div><h1><b>2</b>Market</h1><p>Where capital is going in Indian technology, by sector and stage. Use it to open a pitch with current numbers.</p></div>
    <div class="controls"><label class="f">Sector<select id="m-sector">${sectorOptions(s.all_sectors, st.sector, [["focus", "Arventum's 20 focus sectors"], ["all", "All sectors"]])}</select></label>
    <label class="f">Tables cover<select id="m-months">${[3, 6, 12, 24].map(m => `<option value="${m}" ${m === st.months ? "selected" : ""}>Last ${m} months</option>`).join("")}</select></label></div></div>
    <dl class="facts"><div><dt>Rounds, last ${st.months} months</dt><dd>${int(recent.length)}</dd></div><div><dt>Capital raised</dt><dd>${usd(recent.reduce((a, d) => a + (d.usd_m || 0), 0))}</dd></div>
      <div><dt>Median disclosed round</dt><dd>${usd(median(recent.map(d => d.usd_m)))}</dd></div><div><dt>Companies funded</dt><dd>${int(new Set(recent.map(d => d.cid)).size)}</dd></div></dl>
    <div class="grid">
      ${exhibit({ n: "2.1", title: `Capital raised per quarter, ${label}`, cls: "c6", body: barChart(capItems, { w: 500, fmt: v => usd(v, 0), height: 230 }), source: sourceLine("equity and venture-debt rounds with disclosed amounts.") })}
      ${exhibit({ n: "2.2", title: `Rounds per quarter, ${label}`, cls: "c6", body: barChart(cntItems, { w: 500, fmt: v => int(v), height: 230 }), source: sourceLine("all primary rounds, disclosed or not.") })}
      ${exhibit({ n: "2.3", title: "Where the money went in the last six months", sub: `<span class="legend"><span><i style="background:var(--teal)"></i>Arventum focus sector</span><span><i style="background:#A8B3C4"></i>Other sector</span></span>`, cls: "c7",
        body: hbarChart(heat, { w: 600, labelW: 160, row: 24, fmt: v => usd(v, 0) }), source: sourceLine("capital in disclosed rounds; hover a bar for the change versus the prior six months.") })}
      ${exhibit({ n: "2.4", title: "What a round looks like now, by stage", sub: "Middle half of disclosed rounds in the last two years; the dark tick is the median.", cls: "c5",
        body: bench.length ? rangeChart(bench, { log: true, fmt: v => usd(v, 0), ticksAt: [0.1, 1, 10, 100], labelW: 96, w: 420, row: 30 }) : `<div class="empty">Too few disclosed rounds.</div>`,
        source: sourceLine("stage as reported in the source article.") })}
      ${exhibit({ n: "2.5", title: "Most active institutional investors", cls: "c5", body: `<div id="m-inv"></div>`, source: sourceLine(`rounds in the last ${st.months} months; angels excluded.`) })}
      ${exhibit({ n: "2.6", title: "Latest deals", cls: "c7", body: `<div id="m-deals"></div>`, source: sourceLine("each row links to its article.") })}
    </div>`;
  return { html, after: async () => {
    document.getElementById("m-sector").onchange = e => { st.sector = e.target.value; route(); };
    document.getElementById("m-months").onchange = e => { st.months = +e.target.value; route(); };
    const counts = {}; recent.forEach(d => d.leads.concat(d.others).forEach(n => { (counts[n] ||= { n: 0, led: 0 }); counts[n].n++; if (d.leads.includes(n)) counts[n].led++; }));
    const invs = (await load("investors")).profiles; const kind = Object.fromEntries(invs.map(p => [p.name, p]));
    const rows = Object.entries(counts).filter(([n]) => kind[n] && kind[n].type !== "Individual").map(([n, c]) => ({ name: n, rounds: c.n, led: c.led, hq: kind[n]?.hq || "" }))
      .sort((a, b) => b.rounds - a.rounds).slice(0, 25);
    table(document.getElementById("m-inv"), rows, [{ key: "name", label: "Investor" }, { key: "rounds", label: "Rounds", n: true }, { key: "led", label: "Led", n: true }, { key: "hq", label: "HQ", muted: true }], { sortKey: "rounds" });
    const latest = ds.filter(d => pick(d) && d.type !== "public_market").slice(0, 60);
    table(document.getElementById("m-deals"), latest, [
      { key: "date", label: "Date", fmt: r => date(r.date), sort: r => r.date },
      { key: "company", label: "Company", fmt: r => `<a href="#/company/${r.cid}">${esc(r.company)}</a>` },
      { key: "stage", label: "Stage", fmt: r => stageLabel(r.type === "acquisition" ? "acquisition" : r.stage) },
      { key: "usd_m", label: "Amount", n: true, fmt: r => usd(r.usd_m) },
      { key: "leads", label: "Led by / buyer", fmt: r => esc(r.acquirer || r.leads.join(", ")) },
      { key: "url", label: "", fmt: r => r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">Article</a>` : "" }], { sortKey: "date" });
  } };
}

// ---------- 3 radar ----------
async function viewRadar() {
  const [s, rd] = await Promise.all([load("summary"), load("radar")]);
  const st = state.radar, focus = new Set(s.focus_sectors), r = s.radar.summary || {}, folds = s.radar.folds || [];
  const last = folds[folds.length - 1];
  const rows = rd.top.filter(c => (st.sector === "all" || (st.sector === "focus" ? focus.has(c.sector) : c.sector === st.sector))
    && (st.stage === "any" || c.stage === st.stage) && (!st.min || (c.last_usd_m || 0) >= st.min));
  const decItems = last ? last.deciles.map((v, i) => ({ x: `D${i + 1}`, v: v * 100, tip: `Decile ${i + 1}: ${(v * 100).toFixed(0)}% raised within 12 months` })) : [];
  const html = h`<div class="sechead"><div><h1><b>3</b>Origination</h1><p>Private Indian tech companies ranked by their likelihood of announcing a new round within 12 months. Call them before another bank does.</p></div>
    <div class="controls"><button class="btn" id="brief">Download this week's brief</button></div></div>
    <div class="grid">
      ${exhibit({ n: "3.1", title: "Does it work? Tested on outcomes the model never saw", cls: "c5",
        body: `<table><thead><tr><th></th><th class="n">Top-100 precision</th><th class="n">Ranking (AUC)</th></tr></thead><tbody>
          <tr><td><b>This model</b></td><td class="n"><b>${pct(r.mean_precision_top100)}</b></td><td class="n"><b>${r.mean_auc?.toFixed(2)}</b></td></tr>
          <tr><td>"Raised 18–24 months ago" rule</td><td class="n">${pct(r.mean_precision_top100_heuristic)}</td><td class="n">${r.mean_auc_heuristic?.toFixed(2)}</td></tr>
          <tr><td>Picking at random</td><td class="n">${pct(r.mean_base_rate)}</td><td class="n">0.50</td></tr></tbody></table>
          <p class="note">Averaged over ${folds.length} quarters. For each test date the model saw only snapshots whose outcome was known before it, then we checked who actually raised. The top of the list is ${r.mean_lift_top100}× better than random; ranking across the whole list is moderate.</p>`,
        source: sourceLine("walk-forward backtest; logistic regression chosen over gradient-boosted trees on the same test.") })}
      ${exhibit({ n: "3.2", title: "Share that actually raised, by score decile", sub: last ? `Test date ${date(last.test_cutoff)}. D1 holds the highest scores.` : "", cls: "c7",
        body: decItems.length ? barChart(decItems, { w: 560, fmt: v => `${Math.round(v)}%`, height: 230 }) : "", source: sourceLine("one test quarter shown; all four in the Method section.") })}
      ${exhibit({ n: "3.3", title: "Companies most likely to raise next", cls: "c12",
        body: `<div class="controls" style="margin-bottom:12px"><label class="f">Sector<select id="r-sector">${sectorOptions(s.all_sectors.filter(x => x !== "Other"), st.sector, [["focus", "Arventum's 20 focus sectors"], ["all", "All sectors"]])}</select></label>
          <label class="f">Last round<select id="r-stage"><option value="any">Any stage</option>${STAGES.concat(["debt", "undisclosed"]).map(x => `<option value="${x}" ${x === st.stage ? "selected" : ""}>${stageLabel(x)}</option>`).join("")}</select></label>
          <label class="f">Last round at least<select id="r-min">${[0, 1, 5, 10, 25, 50].map(v => `<option value="${v}" ${v === st.min ? "selected" : ""}>${v ? "$" + v + "M" : "Any size"}</option>`).join("")}</select></label></div>
          <div id="r-detail"></div><div id="r-table"></div>`,
        source: sourceLine("listed companies excluded. Likelihood is the model's probability of a new primary round within 12 months.") })}
    </div>`;
  return { html, after: () => {
    const set = (k, v) => { st[k] = v; st.sel = null; route(); };
    document.getElementById("r-sector").onchange = e => set("sector", e.target.value);
    document.getElementById("r-stage").onchange = e => set("stage", e.target.value);
    document.getElementById("r-min").onchange = e => set("min", +e.target.value);
    document.getElementById("brief").onclick = () => downloadBrief(rd, s);
    const showDetail = async c => {
      st.sel = c.cid; tbl.render();
      const ds = (await deals()).filter(d => d.cid === c.cid);
      document.getElementById("r-detail").innerHTML = `<div class="detail"><h3>${esc(c.company)}: ${pct(c.p)} likelihood of a round in 12 months</h3>
        <ul>${c.why.map(w => `<li>${esc(w)}</li>`).join("")}</ul>
        <p class="note">${ds.length} deals on record. <a href="#/company/${c.cid}">Open the full company page</a></p></div>`;
    };
    const tbl = table(document.getElementById("r-table"), rows, [
      { key: "company", label: "Company", fmt: c => `<b>${esc(c.company)}</b>` },
      { key: "sector", label: "Sector", muted: true },
      { key: "stage", label: "Last round", fmt: c => stageLabel(c.stage) },
      { key: "last", label: "When", fmt: c => month(c.last), sort: c => c.last },
      { key: "months", label: "Months since", n: true, fmt: c => Math.round(c.months) },
      { key: "last_usd_m", label: "Size", n: true, fmt: c => usd(c.last_usd_m) },
      { key: "rounds", label: "Rounds tracked", n: true },
      { key: "p", label: "Likelihood", fmt: c => `<div class="bar"><i style="width:${Math.round(c.p * 100)}px"></i><span>${pct(c.p)}</span></div>`, sort: c => c.p }],
      { sortKey: "p", onClick: showDetail, selected: c => c.cid === st.sel, max: 100 });
  } };
}
function downloadBrief(rd, s) {
  const focus = new Set(s.focus_sectors);
  const top = rd.top.filter(c => focus.has(c.sector)).slice(0, 10);
  const md = [`# Origination brief, week of ${new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })}`, "",
    `Deal data as of ${date(s.last)}. Arventum's focus sectors.`, "", "## Ten companies to call", "",
    ...top.flatMap((c, i) => [`**${i + 1}. ${c.company}** (${c.sector}): ${pct(c.p)} likelihood of a round in 12 months; last round ${stageLabel(c.stage)}, ${month(c.last)}`, ...c.why.slice(0, 3).map(w => `   - ${w}`), ""]),
    "_Generated from public deal reports. Decision support, not investment advice._"].join("\n");
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([md], { type: "text/markdown" })); a.download = "origination_brief.md"; a.click();
}

// ---------- 4 investors ----------
function rankInvestors(inv, { sector, stage, amount, lead, foreign }) {
  const W = inv.weights, M = 3, eps = 0.02, srank = STAGE_RANK[stage];
  const ms = inv.market_sector[sector] || 0;
  const mst = Object.entries(inv.market_stage_rank).filter(([k]) => Math.abs(+k - srank) <= 1).reduce((a, [, v]) => a + v, 0);
  const pool = inv.profiles.filter(p => p.type !== "Individual" && (!foreign || (p.hq && p.hq !== "India")));
  const maxAct = Math.max(...pool.map(p => p.recent), 1);
  const scored = pool.map(p => {
    const secFit = ((p.sec[sector] || 0) + M * ms) / (p.w + M);
    const near = Object.entries(p.stg).filter(([k]) => Math.abs(+k - srank) <= 1).reduce((a, [, v]) => a + v, 0);
    const stgFit = srank == null ? 0.5 : (near + M * mst) / (p.w + M);
    const cheq = amount && p.med != null ? Math.exp(-Math.abs(Math.log((p.med + 0.1) / (amount + 0.1))) / 1.2) : (amount ? 0.3 : 0.5);
    const act = Math.log1p(p.recent) / Math.log1p(maxAct);
    const ld = lead ? p.lead : 0.5;
    const score = Math.exp(W.sector * Math.log(secFit + eps) + W.stage * Math.log(stgFit + eps) + W.cheque * Math.log(cheq + eps) + W.activity * Math.log(act + eps) + W.lead * Math.log(ld + eps));
    return { ...p, score, inSector: p.ex.filter(e => e[2] === sector).length };
  }).sort((a, b) => b.score - a.score).slice(0, 40);
  const top = scored[0]?.score || 1; scored.forEach(p => p.match = Math.round(100 * p.score / top));
  return scored;
}
async function viewInvestors() {
  const [s, inv] = await Promise.all([load("summary"), load("investors")]);
  const st = state.inv, m = s.matching || {};
  const res = rankInvestors(inv, st);
  if (!res.find(p => p.id === st.sel)) st.sel = res[0]?.id;
  const html = h`<div class="sechead"><div><h1><b>4</b>Investors</h1><p>Describe the client. Get the investors most likely to back it, ranked, with the deals that justify each one.</p></div></div>
    <div class="exhibit c12" style="margin-bottom:24px"><div class="controls">
      <label class="f">Client's sector<select id="i-sector">${sectorOptions(s.all_sectors, st.sector)}</select></label>
      <label class="f">Round<select id="i-stage">${STAGES.slice(0, 9).map(x => `<option value="${x}" ${x === st.stage ? "selected" : ""}>${stageLabel(x)}</option>`).join("")}</select></label>
      <label class="f">Target raise ($M)<input id="i-amount" type="number" min="0.1" step="1" value="${st.amount}"></label>
      <label class="check"><input id="i-lead" type="checkbox" ${st.lead ? "checked" : ""}>Needs a lead investor</label>
      <label class="check"><input id="i-foreign" type="checkbox" ${st.foreign ? "checked" : ""}>Headquartered outside India</label></div></div>
    <div class="grid">
      ${exhibit({ n: "4.1", title: "Investors ranked for this client", cls: "c7", body: `<div id="i-table"></div>`,
        source: sourceLine("blend of sector fit, stage fit, cheque size, recent activity and lead appetite; weights tuned on an earlier period. Small samples are shrunk toward the market average.") })}
      ${exhibit({ n: "4.2", title: "Why this investor", cls: "c5", body: `<div id="i-detail"></div>`, source: sourceLine("recent deals in which this investor participated.") })}
      ${exhibit({ n: "4.3", title: "Does it work? Tested on real rounds", cls: "c12",
        body: `<table><thead><tr><th>A real investor in the round appeared in…</th><th class="n">This ranking</th><th class="n">"Most active investors" list</th></tr></thead><tbody>
          ${["10", "20", "50"].map(k => `<tr><td>the top ${k}</td><td class="n"><b>${pct(m.model_hit_rate?.[k])}</b></td><td class="n">${pct(m.baseline_hit_rate?.[k])}</td></tr>`).join("")}</tbody></table>
          <p class="note">${m.test_deals} rounds since ${date(m.period_start)}, each ranked using only data from before that round.</p>`,
        source: sourceLine("out-of-sample backtest; weights chosen on the preceding six months.") })}
    </div>`;
  return { html, after: () => {
    const upd = () => { st.sel = null; route(); };
    document.getElementById("i-sector").onchange = e => { st.sector = e.target.value; upd(); };
    document.getElementById("i-stage").onchange = e => { st.stage = e.target.value; upd(); };
    document.getElementById("i-amount").onchange = e => { st.amount = Math.max(0.1, +e.target.value || 1); upd(); };
    document.getElementById("i-lead").onchange = e => { st.lead = e.target.checked; upd(); };
    document.getElementById("i-foreign").onchange = e => { st.foreign = e.target.checked; upd(); };
    const detail = p => {
      st.sel = p.id; tbl.render();
      document.getElementById("i-detail").innerHTML = `<h3 style="font-family:var(--serif);margin:0 0 4px">${esc(p.name)}</h3>
        <p class="note" style="margin:0 0 12px">${esc(p.ai_type || p.type)}${p.hq ? " · " + esc(p.hq) : ""} · ${p.recent} deals in 18 months · typical round ${usd(p.med)} · leads ${pct(p.lead)} of its deals</p>
        <table><thead><tr><th>Date</th><th>Company</th><th>Stage</th><th class="n">Round</th></tr></thead><tbody>
        ${[...p.ex].sort((a, b) => (b[2] === st.sector) - (a[2] === st.sector) || b[0].localeCompare(a[0])).slice(0, 10).map(e => `<tr${e[2] === st.sector ? ' class="sel"' : ""}><td class="muted">${month(e[0])}</td><td>${esc(e[1])}${e[5] ? ' <span class="tag teal">led</span>' : ""}</td><td>${stageLabel(e[3])}</td><td class="n">${usd(e[4])}</td></tr>`).join("")}</tbody></table>
        <p class="note">Highlighted rows are in the client's sector.</p>`;
    };
    const tbl = table(document.getElementById("i-table"), res, [
      { key: "name", label: "Investor", fmt: p => `<b>${esc(p.name)}</b>` },
            { key: "match", label: "Match", fmt: p => `<div class="bar"><i style="width:${p.match}px"></i><span>${p.match}</span></div>`, sort: p => p.match },
      { key: "inSector", label: "In sector", n: true }, { key: "recent", label: "Deals, 18m", n: true },
      { key: "med", label: "Typical round", n: true, fmt: p => usd(p.med) }],
      { sortKey: "match", onClick: detail, selected: p => p.id === st.sel, empty: "No investors match these filters." });
    const first = res.find(p => p.id === st.sel); if (first) detail(first);
  } };
}

// ---------- 5 buyers ----------
async function viewBuyers() {
  const b = await load("buyers"); const st = state.buy;
  const sectors = Object.keys(b.by_sector); if (!b.by_sector[st.sector]) st.sector = sectors[0];
  const bs = b.summary;
  const topSec = Object.entries(bs.top_sectors).filter(([k]) => k !== "Unclassified").slice(0, 10).map(([k, v]) => ({ label: k, v }));
  const html = h`<div class="sechead"><div><h1><b>5</b>Buyers</h1><p>Who acquires Indian technology companies, ranked for a target's sector by relevance, appetite and recency.</p></div>
    <div class="controls"><label class="f">Target's sector<select id="b-sector">${sectorOptions(sectors, st.sector)}</select></label></div></div>
    <div class="grid">
      ${exhibit({ n: "5.1", title: `Most likely buyers for a ${st.sector} company`, cls: "c8", body: `<div id="b-table"></div>`,
        source: sourceLine("acquisitions with a named buyer; serial and recent acquirers rank higher.") })}
      ${exhibit({ n: "5.2", title: "Acquisitions by target sector", cls: "c4", body: hbarChart(topSec, { w: 380, labelW: 170, row: 26, fmt: v => int(v) }),
        source: sourceLine(`${bs.disclosed_value_pct}% of these deals disclose a price.`) })}
      ${exhibit({ n: "5.3", title: "Latest acquisitions", cls: "c12", body: `<div id="b-recent"></div>`, source: sourceLine("each row links to its article.") })}
    </div>`;
  return { html, after: () => {
    document.getElementById("b-sector").onchange = e => { st.sector = e.target.value; route(); };
    const rows = b.by_sector[st.sector] || [];
    table(document.getElementById("b-table"), rows, [
      { key: "acquirer", label: "Acquirer", fmt: r => `<b>${esc(r.acquirer)}</b>` },
      { key: "match_pct", label: "Match", fmt: r => `<div class="bar"><i style="width:${r.match_pct}px"></i><span>${r.match_pct}</span></div>` },
      { key: "in_sector", label: "In sector", n: true }, { key: "acquisitions_total", label: "Total buys", n: true },
      { key: "last_24m", label: "Last 24 months", n: true }, { key: "targets", label: "Recent targets", muted: true }], { sortKey: "match_pct" });
    table(document.getElementById("b-recent"), b.recent.map(r => ({ date: r[0], target: r[1], sector: r[2], acquirer: r[3], usd: r[4], url: r[5] })), [
      { key: "date", label: "Date", fmt: r => date(r.date), sort: r => r.date }, { key: "target", label: "Target", fmt: r => `<b>${esc(r.target)}</b>` },
      { key: "sector", label: "Sector", muted: true }, { key: "acquirer", label: "Acquirer" }, { key: "usd", label: "Price", n: true, fmt: r => usd(r.usd) },
      { key: "url", label: "", fmt: r => r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">Article</a>` : "" }], { sortKey: "date" });
  } };
}

// ---------- 6 valuation ----------
const tidy = n => n === n.toUpperCase() ? n.toLowerCase().replace(/\b\w/g, c => c.toUpperCase()).replace(/\bLtd\b/, "Ltd").replace(/\bTechn\b/, "Tech") : n;
function valueCompany(V, { sector, rev, growth, margin, gross, scope }) {
  const comps = V.comps, k = (1 - V.discount) * rev, ranges = [], notes = [];
  if (gross == null) { gross = V.sector_gross[sector] ?? 0.6; notes.push(`Gross margin not given; using the ${sector} peer median of ${pct(gross)}.`); }
  let peers = comps.filter(c => c.sector === sector && (scope === "Both" || c.market === scope));
  if (peers.length < 3) { peers = comps.filter(c => c.sector === sector); if (scope !== "Both") notes.push("Few listed peers in that market; using India and global peers."); }
  if (peers.length >= 2) { const e = peers.map(p => p.ev_revenue); const q1 = quantile(e, .25), q2 = quantile(e, .5), q3 = quantile(e, .75);
    ranges.push({ label: "Listed sector peers", lo: q1 * k, mid: q2 * k, hi: q3 * k, note: `${q1.toFixed(1)}×–${q3.toFixed(1)}× EV/revenue after a ${pct(V.discount)} private-company discount` }); }
  const r = V.regression, india = scope === "India" ? 1 : scope === "Both" ? 0.5 : 0, cl = (x, a, b) => Math.min(b, Math.max(a, x));
  const lm = r.intercept + r.growth * cl(growth, -0.5, 2) + r.margin * cl(margin, -1, 0.7) + r.gross * cl(gross, 0, 1) + r.india * india, sd = r.resid_sd * 0.674;
  ranges.push({ label: "Growth- and margin-adjusted", lo: Math.exp(lm - sd) * k, mid: Math.exp(lm) * k, hi: Math.exp(lm + sd) * k, note: `${Math.exp(lm).toFixed(1)}× implied EV/revenue (regression on ${r.n} listed companies, R² ${r.r2.toFixed(2)})` });
  const seen = new Set();
  let pm = V.private.filter(p => p.ev_revenue > 0.2 && p.ev_revenue < 80 && !seen.has(p.company + p.deal_date) && seen.add(p.company + p.deal_date)); const same = pm.filter(p => p.sector === sector);
  const scopeTxt = same.length >= 4 ? "same sector" : "all sectors"; if (same.length >= 4) pm = same;
  if (pm.length >= 3) { const e = pm.map(p => p.ev_revenue); const q1 = quantile(e, .25), q2 = quantile(e, .5), q3 = quantile(e, .75);
    ranges.push({ label: "Indian private rounds", lo: q1 * rev, mid: q2 * rev, hi: q3 * rev, note: `${q1.toFixed(1)}×–${q3.toFixed(1)}× valuation/revenue, ${pm.length} rounds (${scopeTxt})` }); }
  const blend = ranges.length ? [median(ranges.map(x => x.lo)), median(ranges.map(x => x.mid)), median(ranges.map(x => x.hi))] : null;
  return { ranges, blend, peers, pm, notes };
}
async function viewValuation() {
  const V = await load("valuation"); const st = state.val;
  const sectors = [...new Set(V.comps.map(c => c.sector))].sort();
  const res = valueCompany(V, { sector: st.sector, rev: st.rev, growth: st.growth / 100, margin: st.margin / 100, gross: st.gross == null ? null : st.gross / 100, scope: st.scope });
  const toUsd = cr => cr * 1e7 / V.usd_inr / 1e6;
  const html = h`<div class="sechead"><div><h1><b>6</b>Valuation</h1><p>A defensible value range from three independent methods, drawn as a football field.</p></div></div>
    <div class="exhibit c12" style="margin-bottom:24px"><div class="controls">
      <label class="f">Sector<select id="v-sector">${sectorOptions(sectors, st.sector)}</select></label>
      <label class="f">Annual revenue (₹ crore)<input id="v-rev" type="number" min="1" step="10" value="${st.rev}"></label>
      <label class="f">Revenue growth (%)<input id="v-growth" type="number" step="5" value="${st.growth}"></label>
      <label class="f">EBITDA margin (%)<input id="v-margin" type="number" step="5" value="${st.margin}"></label>
      <label class="f">Gross margin (%), optional<input id="v-gross" type="number" step="5" placeholder="sector median" value="${st.gross ?? ""}"></label>
      <label class="f">Listed peers<div class="seg" id="v-scope">${["Both", "India", "Global"].map(x => `<button type="button" class="${x === st.scope ? "on" : ""}" data-v="${x}">${x}</button>`).join("")}</div></label></div></div>
    ${res.blend ? `<dl class="facts"><div><dt>Indicative enterprise value</dt><dd>${inr(res.blend[0])}–${inr(res.blend[2]).replace("₹", "")}<small>≈ ${usd(toUsd(res.blend[0]), 0)}–${usd(toUsd(res.blend[2]), 0)}</small></dd></div>
      <div><dt>Central estimate</dt><dd>${inr(res.blend[1])}<small>${(res.blend[1] / st.rev).toFixed(1)}× revenue</small></dd></div>
      <div><dt>Listed peers used</dt><dd>${res.peers.length}<small>${st.scope === "Both" ? "India and global" : st.scope}</small></dd></div>
      <div><dt>Indian private rounds</dt><dd>${res.pm.length}<small>with valuation and revenue</small></dd></div></dl>` : ""}
    <div class="grid">
      ${exhibit({ n: "6.1", title: "Football field: enterprise value, ₹ crore", sub: "Each bar is one method's range; the dark tick is its midpoint.", cls: "c12",
        body: rangeChart(res.ranges.map(x => ({ ...x, tip: `${x.label}: ${inr(x.lo)} to ${inr(x.hi)}. ${x.note}` })), { fmt: v => Math.round(v).toLocaleString("en-IN"), labelW: 210, row: 46 })
          + `<ul class="note" style="padding-left:18px">${res.ranges.map(x => `<li><b>${x.label}:</b> ${x.note}</li>`).join("")}${res.notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul>`,
        source: sourceLine(`listed data from Yahoo Finance as of ${V.as_of}; regression specification chosen by leave-one-out cross-validation across six candidates.`) })}
      ${exhibit({ n: "6.2", title: "Listed peers", cls: "c6", body: `<div id="v-peers"></div>`, source: sourceLine("enterprise value over trailing revenue.") })}
      ${exhibit({ n: "6.3", title: "Indian private rounds with a disclosed valuation", cls: "c6", body: `<div id="v-private"></div>`, source: sourceLine("valuation over the latest annual revenue published within six months of the round.") })}
    </div>`;
  return { html, after: () => {
    const num = (id, k) => document.getElementById(id).onchange = e => { const v = e.target.value; st[k] = v === "" ? null : +v; route(); };
    document.getElementById("v-sector").onchange = e => { st.sector = e.target.value; route(); };
    num("v-rev", "rev"); num("v-growth", "growth"); num("v-margin", "margin"); num("v-gross", "gross");
    document.querySelectorAll("#v-scope button").forEach(b => b.onclick = () => { st.scope = b.dataset.v; route(); });
    table(document.getElementById("v-peers"), res.peers, [{ key: "name", label: "Company", fmt: p => esc(tidy(p.name)) }, { key: "market", label: "Market", muted: true },
      { key: "ev_revenue", label: "EV/revenue", n: true, fmt: p => p.ev_revenue.toFixed(1) + "×" },
      { key: "revenue_growth", label: "Growth", n: true, fmt: p => pct(p.revenue_growth) }, { key: "gross_margin", label: "Gross margin", n: true, fmt: p => pct(p.gross_margin) }], { sortKey: "ev_revenue" });
    table(document.getElementById("v-private"), res.pm, [{ key: "company", label: "Company", fmt: p => `<b>${esc(p.company)}</b>` }, { key: "deal_date", label: "Date", fmt: p => month(p.deal_date), sort: p => p.deal_date },
      { key: "valuation_inr_cr", label: "Valuation", n: true, fmt: p => inr(p.valuation_inr_cr) }, { key: "ev_revenue", label: "× revenue", n: true, fmt: p => p.ev_revenue.toFixed(1) + "×" },
      { key: "source_url", label: "", fmt: p => p.source_url ? `<a href="${esc(p.source_url)}" target="_blank" rel="noopener">Article</a>` : "" }], { sortKey: "deal_date" });
  } };
}

// ---------- 7 company ----------
async function viewCompany(cidArg) {
  const [C, ds, rd] = await Promise.all([load("companies"), deals(), load("radar")]);
  const byId = Object.fromEntries(C.list.map(c => [c[0], c]));
  let cid = cidArg ? +cidArg : state.company || rd.top[0]?.cid;
  state.company = cid;
  const c = byId[cid] || C.list[0]; cid = c[0];
  const cd = ds.filter(d => d.cid === cid), prim = cd.filter(d => d.type === "equity" || d.type === "debt");
  const fin = C.fin[cid] || [], p = C.radar[cid], radarRow = rd.top.find(x => x.cid === cid);
  const backers = {}; cd.forEach(d => { d.leads.forEach(n => { (backers[n] ||= { n: 0, led: 0 }); backers[n].n++; backers[n].led++; }); d.others.forEach(n => { (backers[n] ||= { n: 0, led: 0 }); backers[n].n++; }); });
  const html = h`<div class="sechead"><div><h1><b>7</b>${esc(c[1])}</h1><p>${esc(c[2] || "Unclassified")}${c[3] ? " · " + esc(c[3]) : ""}</p></div>
    <div class="controls"><label class="f">Another company<input id="c-find" type="text" placeholder="Type a name" list="c-list"></label><datalist id="c-list">${C.list.slice(0, 4000).map(x => `<option value="${esc(x[1])}">`).join("")}</datalist></div></div>
    <dl class="facts"><div><dt>Raised (tracked)</dt><dd>${usd(prim.reduce((a, d) => a + (d.usd_m || 0), 0))}<small>${prim.length} rounds</small></dd></div>
      <div><dt>Last round</dt><dd>${prim[0] ? month(prim[0].date) : "—"}<small>${prim[0] ? stageLabel(prim[0].stage) : ""}</small></dd></div>
      <div><dt>Latest reported revenue</dt><dd>${fin.length ? inr(fin[fin.length - 1][1]) : "—"}<small>${fin.length ? fin[fin.length - 1][0] : "not reported"}</small></dd></div>
      <div><dt>Likelihood of a round in 12 months</dt><dd>${p != null ? pct(p) : "—"}<small>${p != null ? '<a href="#/radar">Origination Radar</a>' : "listed or not scored"}</small></dd></div></dl>
    ${radarRow ? `<div class="callout" style="margin-bottom:24px"><b>Why the Radar ranks it:</b> ${radarRow.why.map(esc).join("; ")}.</div>` : ""}
    <div class="grid">
      ${exhibit({ n: "7.1", title: "Deal history", cls: "c8", body: `<div id="c-deals"></div>`, source: sourceLine("each row links to its article.") })}
      ${exhibit({ n: "7.2", title: "Backers", cls: "c4", body: `<div id="c-backers"></div>`, source: sourceLine("named investors across tracked rounds.") })}
      ${fin.length ? exhibit({ n: "7.3", title: "Reported revenue, ₹ crore", cls: "c12",
        body: barChart(fin.map(f => ({ x: f[0], v: f[1] || 0, tip: `${f[0]}: revenue ${inr(f[1])}${f[2] != null ? ", profit " + inr(f[2]) : ""}` })), { fmt: v => Math.round(v).toLocaleString("en-IN"), height: 200 }),
        source: sourceLine("full fiscal years only (April to March), as reported in public filings coverage.") }) : ""}
    </div>`;
  return { html, after: () => {
    const f = document.getElementById("c-find");
    f.onchange = () => { const hit = C.list.find(x => x[1].toLowerCase() === f.value.trim().toLowerCase()); if (hit) location.hash = `#/company/${hit[0]}`; };
    table(document.getElementById("c-deals"), cd, [{ key: "date", label: "Date", fmt: r => date(r.date), sort: r => r.date },
      { key: "type", label: "Type", fmt: r => stageLabel(r.type === "equity" || r.type === "debt" ? r.stage : r.type) },
      { key: "usd_m", label: "Amount", n: true, fmt: r => usd(r.usd_m) }, { key: "leads", label: "Led by / buyer", fmt: r => esc(r.acquirer || r.leads.join(", ") || "—") },
      { key: "url", label: "", fmt: r => r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">Article</a>` : "" }], { sortKey: "date", empty: "No deals on record." });
    table(document.getElementById("c-backers"), Object.entries(backers).map(([n, v]) => ({ name: n, ...v })), [{ key: "name", label: "Investor" },
      { key: "n", label: "Rounds", n: true }, { key: "led", label: "Led", n: true }], { sortKey: "n", empty: "No named investors." });
  } };
}

// ---------- 8 method ----------
async function viewMethod() {
  const [s, wk] = await Promise.all([load("summary"), load("coverage_weekly").catch(() => [])]);
  const cc = s.crosscheck || {}, me = s.model_eval || {}, re = s.rules_eval || {}, v = s.validation || {}, cov = s.coverage || {};
  const nice = { record_type: "Deal type", company: "Company", stage: "Stage", amount: "Amount", lead_investors: "Lead investors", sector: "Sector" };
  const agree = Object.entries(cc).map(([k, x]) => ({ label: nice[k] || k, v: x }));
  const extractors = [["OpenCode (GPT-5.6)", cc.company, cc.amount, cc.lead_investors, `${s.crosscheck_n} articles read by both`],
    ...[["gemini", "Gemini Flash-Lite"], ["groq", "Groq gpt-oss-120b"], ["deepseek", "DeepSeek"], ["pickle", "Big Pickle"]].filter(([k]) => me[k]).map(([k, l]) => [l, me[k].company, me[k].amount, me[k].lead_investors, `${me[k].articles} articles compared`]),
    ...(re.company_pct ? [["Headline rules (no AI)", re.company_pct, re.amount_pct, re.lead_precision_pct, `${re.deals_compared} deals; funding and financials only`]] : [])];
  const labels = { headline_amount: "Amount matches the headline", stage_size: "Round size plausible for its stage", missing_core: "Core fields present", company_in_title: "Company named in the article" };
  const byM = {}; [...wk].sort((a, b) => a.week_end.localeCompare(b.week_end)).forEach(w => { const k = w.week_end.slice(0, 7); (byM[k] ||= { r: 0, o: 0 }); byM[k].r += w.reported_usd_m || 0; byM[k].o += w.our_usd_m || 0; });
  const weeks = Object.keys(byM).sort().slice(-36).map(k => ({ week_end: k + "-01", reported_usd_m: byM[k].r, our_usd_m: byM[k].o }));
  const html = h`<div class="sechead"><div><h1><b>8</b>Method and quality</h1><p>How the book is made, and how far to trust it, measured four independent ways.</p></div>
    <div class="controls"><button class="btn ghost" id="csv">Download all deals (CSV)</button></div></div>
    <div class="grid">
      ${exhibit({ n: "8.1", title: "How a deal gets into the book", cls: "c6", body: `<ol class="prose">
        <li><b>Collect.</b> A polite crawler reads Entrackr and Inc42 sitemaps and downloads ${int(s.tables.sources)} relevant articles, slowing down when a site asks it to.</li>
        <li><b>Extract.</b> AI agents (Codex and OpenCode on GPT-5.6, with measured fallbacks) turn each article into a structured record under a strict schema.</li>
        <li><b>Reconcile.</b> Rules check amounts against the headline, drop partial fiscal years and public-market raises, merge spelling variants and de-duplicate across sources. Every change is logged (${int(Object.values(s.corrections || {}).reduce((a, b) => a + b, 0))} so far).</li>
        <li><b>Measure.</b> Agent agreement, rule checks, coverage against published weekly totals, a manual audit and model backtests.</li></ol>`,
        source: sourceLine("pipeline code and engineering log in the repository.") })}
      ${exhibit({ n: "8.2", title: "Two independent AI agents, same articles", sub: "Share of articles where Codex and OpenCode agree.", cls: "c6", body: hbarChart(agree, { w: 500, fmt: x => `${x}%`, labelW: 130, row: 30 }),
        source: sourceLine(`${s.crosscheck_n} articles extracted independently by both agents.`) })}
      ${exhibit({ n: "8.3", title: "Every extractor, measured against Codex", cls: "c7", body: `<table><thead><tr><th>Extractor</th><th class="n">Company</th><th class="n">Amount</th><th class="n">Lead investors</th><th>Sample</th></tr></thead><tbody>
          ${extractors.map(e => `<tr><td>${e[0]}</td><td class="n">${e[1] ?? "—"}%</td><td class="n">${e[2] ?? "—"}%</td><td class="n">${e[3] ?? "—"}%</td><td class="muted">${e[4]}</td></tr>`).join("")}</tbody></table>
          <p class="note">When several extractors read one article, the more accurate one wins. Records from fallbacks are re-queued for the primary agents.</p>`,
        source: sourceLine("agreement with the reference agent on identical articles.") })}
      ${exhibit({ n: "8.4", title: "Rule checks, no AI involved", cls: "c5", body: `<ul class="results-list">${Object.entries(v).map(([k, x]) => `<li><span class="what">${labels[k] || k}</span><span class="fig">${x.pass_rate}%</span><span class="vs">${int(x.passed)} of ${int(x.checked)} records</span></li>`).join("")}</ul>`,
        source: sourceLine("deterministic validators over every extracted record.") })}
      ${weeks.length ? exhibit({ n: "8.5", title: "Capital per month: published weekly totals and what the book captured", sub: `<span class="legend"><span><i style="background:#A86412"></i>Published weekly total</span><span><i style="background:var(--teal)"></i>Captured in the book</span></span>`, cls: "c12",
        body: lineChart([{ name: "published", color: "#A86412", values: weeks.map(w => ({ x: month(w.week_end), v: w.reported_usd_m })) },
          { name: "captured", color: "var(--teal)", values: weeks.map(w => ({ x: month(w.week_end), v: w.our_usd_m })) }], { fmt: x => usd(x, 1), height: 240, labelEvery: 6 }),
        source: sourceLine(`Entrackr weekly round-ups parsed by rules, summed by month; last 36 months shown. Overall ${cov.usd_recall_pct}% of reported capital and ${cov.deal_recall_pct}% of reported deals captured, over ${cov.weeks_compared} weeks; small undisclosed rounds are the gap.`) }) : ""}
      ${exhibit({ n: "8.6", title: "Independent manual audit", cls: "c12", body: `<p class="prose">A random sample of 40 records was graded field by field against the source articles by a reviewer that was not one of the extraction agents: deal type 40 of 40, company 40 of 40, investors 40 of 40, amount 39 of 40, revenue 9 of 9. The weakest field, profit and loss (6 of 9), led to a pipeline fix.</p>`,
        source: sourceLine("docs/MANUAL_AUDIT.md in the repository.") })}
    </div>`;
  return { html, after: () => document.getElementById("csv").onclick = async () => {
    const ds = await deals(); const cols = ["date", "company", "sector", "type", "stage", "usd_m", "leads", "acquirer", "url"];
    const q = x => `"${String(x ?? "").replace(/"/g, '""')}"`;
    const csv = [cols.join(","), ...ds.map(d => cols.map(c => q(Array.isArray(d[c]) ? d[c].join("; ") : d[c])).join(","))].join("\n");
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" })); a.download = "deal_intelligence_deals.csv"; a.click();
  } };
}

// ---------- search ----------
async function initSearch() {
  const [C, inv] = await Promise.all([load("companies"), load("investors")]);
  const items = [...C.list.map(c => ({ t: "Company", name: c[1], sub: c[2], go: `#/company/${c[0]}` })),
    ...inv.profiles.map(p => ({ t: "Investor", name: p.name, sub: p.hq || p.type, inv: p }))];
  const q = document.getElementById("q"), box = document.getElementById("results"); let hits = [], on = 0;
  const show = () => { box.innerHTML = hits.map((x, i) => `<button class="${i === on ? "on" : ""}" data-i="${i}"><span>${esc(x.name)}</span><small>${x.t} · ${esc(x.sub || "")}</small></button>`).join(""); box.classList.toggle("open", hits.length > 0);
    box.querySelectorAll("button").forEach(b => b.onmousedown = () => go(hits[+b.dataset.i])); };
  const go = x => { box.classList.remove("open"); q.value = ""; q.blur();
    if (x.inv) { const top = Object.entries(x.inv.sec).sort((a, b) => b[1] - a[1])[0]; if (top) state.inv.sector = top[0]; state.inv.foreign = false; state.inv.sel = x.inv.id; location.hash = "#/investors"; route(); }
    else location.hash = x.go; };
  q.oninput = () => { const s = q.value.trim().toLowerCase(); on = 0;
    hits = s.length < 2 ? [] : items.filter(x => x.name.toLowerCase().includes(s)).sort((a, b) => a.name.toLowerCase().indexOf(s) - b.name.toLowerCase().indexOf(s) || a.name.length - b.name.length).slice(0, 8); show(); };
  q.onkeydown = e => { if (e.key === "ArrowDown") { on = Math.min(on + 1, hits.length - 1); show(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { on = Math.max(on - 1, 0); show(); e.preventDefault(); } else if (e.key === "Enter" && hits[on]) go(hits[on]); else if (e.key === "Escape") { box.classList.remove("open"); q.blur(); } };
  q.onblur = () => setTimeout(() => box.classList.remove("open"), 120);
  document.addEventListener("keydown", e => { if (e.key === "/" && document.activeElement.tagName !== "INPUT") { e.preventDefault(); q.focus(); } });
}

// ---------- router ----------
const VIEWS = { summary: viewSummary, market: viewMarket, radar: viewRadar, investors: viewInvestors, buyers: viewBuyers, valuation: viewValuation, company: viewCompany, method: viewMethod };
let lastId = null;
async function route() {
  const [, id = "summary", arg] = location.hash.split("/");
  const key = VIEWS[id] ? id : "summary";
  renderTabs(key);
  try {
    const out = await VIEWS[key](arg);
    const html = typeof out === "string" ? out : out.html;
    $main.innerHTML = `<div class="view">${html}</div>`;
    if (out.after) await out.after();
    bindTips($main);
    if (lastId !== key + (arg || "")) window.scrollTo({ top: 0 });
    lastId = key + (arg || "");
    document.title = `${SECTIONS.find(s => s[0] === key)[1]} · Deal Intelligence`;
  } catch (e) { console.error(e); $main.innerHTML = `<div class="empty">This section could not load: ${esc(e.message)}</div>`; }
}
window.addEventListener("hashchange", route);
renderFoot(); initSearch(); route();
