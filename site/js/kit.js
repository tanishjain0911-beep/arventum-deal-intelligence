// Shared toolkit: data, formatting, tables, hand-built SVG charts.
const cache = {};
export async function load(name) {
  if (!cache[name]) cache[name] = fetch(`data/${name}.json`).then(r => r.json());
  return cache[name];
}
export async function deals() {
  const d = await load("deals");
  if (!d._rows) d._rows = d.rows.map(r => Object.fromEntries(d.cols.map((c, i) => [c, r[i]])));
  return d._rows;
}

export const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
export const h = (strings, ...vals) => strings.reduce((a, s, i) => a + s + (i < vals.length ? vals[i] : ""), "");

export function usd(m, d = 1) {
  if (m == null || isNaN(m)) return "—";
  if (m === 0) return "$0";
  if (Math.abs(m) >= 1000) return `$${(m / 1000).toFixed(d)}B`;
  if (Math.abs(m) >= 1) return `$${m.toFixed(m >= 100 ? 0 : d)}M`;
  return `$${Math.round(m * 1000)}K`;
}
export const inr = cr => cr == null ? "—" : `₹${Math.round(cr).toLocaleString("en-IN")} Cr`;
export const pct = (x, d = 0) => x == null ? "—" : `${(100 * x).toFixed(d)}%`;
export const int = x => x == null ? "—" : Math.round(x).toLocaleString("en-IN");
export const date = s => s ? new Date(s + "T00:00:00").toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).replace("Sept", "Sep").replace(/ /g, "\u00a0") : "—";
export const month = s => s ? new Date(s + "T00:00:00").toLocaleDateString("en-GB", { month: "short", year: "numeric" }).replace("Sept", "Sep").replace(/ /g, "\u00a0") : "—";
export const stageLabel = s => ({ "pre-seed": "Pre-seed", "seed": "Seed", "pre-series-a": "Pre-Series A", "series-a": "Series A",
  "series-b": "Series B", "series-c": "Series C", "series-d": "Series D", "series-e+": "Series E+", "growth": "Growth",
  "pre-ipo": "Pre-IPO", "debt": "Debt", "acquisition": "Acquisition", "undisclosed": "Undisclosed", "secondary": "Secondary",
  "bridge": "Bridge", "ipo": "IPO" }[s] || s || "—");

export function quantile(arr, q) {
  const a = arr.filter(v => v != null && !isNaN(v)).sort((x, y) => x - y);
  if (!a.length) return null;
  const pos = (a.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
  return a[lo] + (a[hi] - a[lo]) * (pos - lo);
}
export const median = a => quantile(a, 0.5);

// ---------- tooltip ----------
const tip = () => document.getElementById("tip");
export function bindTips(root) {
  root.querySelectorAll("[data-tip]").forEach(el => {
    el.addEventListener("mousemove", e => { const t = tip(); t.textContent = el.dataset.tip; t.classList.add("on");
      t.style.left = Math.min(e.clientX + 14, innerWidth - t.offsetWidth - 8) + "px"; t.style.top = (e.clientY - 34) + "px"; });
    el.addEventListener("mouseleave", () => tip().classList.remove("on"));
  });
}

// ---------- exhibit ----------
export function exhibit({ n, title, sub, body, source, cls = "c12", id }) {
  return h`<section class="exhibit ${cls}" ${id ? `id="${id}"` : ""}>
    <h2><span class="xn">${n}</span>${esc(title)}</h2>${sub ? `<p class="sub">${sub}</p>` : ""}
    <div class="body">${body}</div>${source ? `<p class="source">${source}</p>` : ""}</section>`;
}

// ---------- table ----------
// cols: [{key,label,n:bool,fmt:fn(row)->html,sort:fn(row)->value}]
export function table(el, rows, cols, { sortKey, desc = true, onClick, selected, max = 400, empty = "No rows match." } = {}) {
  let sk = sortKey, sd = desc;
  function render() {
    const col = cols.find(c => c.key === sk);
    const sorted = col ? [...rows].sort((a, b) => {
      const va = col.sort ? col.sort(a) : a[col.key], vb = col.sort ? col.sort(b) : b[col.key];
      if (va == null) return 1; if (vb == null) return -1;
      return (va < vb ? -1 : va > vb ? 1 : 0) * (sd ? -1 : 1);
    }) : rows;
    const head = cols.map(c => `<th class="${c.n ? "n " : ""}sortable" data-k="${c.key}">${esc(c.label)}<span class="arrow">${c.key === sk ? (sd ? "↓" : "↑") : ""}</span></th>`).join("");
    const body = sorted.slice(0, max).map((r, i) => `<tr class="${onClick ? "click" : ""} ${selected && selected(r) ? "sel" : ""}" data-i="${rows.indexOf(r)}">${cols.map(c =>
      `<td class="${c.n ? "n" : ""} ${c.muted ? "muted" : ""}">${c.fmt ? c.fmt(r) : esc(r[c.key] ?? "—")}</td>`).join("")}</tr>`).join("");
    el.innerHTML = rows.length ? `<div class="tablewrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`
      : `<div class="empty">${empty}</div>`;
    el.querySelectorAll("th.sortable").forEach(th => th.onclick = () => { if (sk === th.dataset.k) sd = !sd; else { sk = th.dataset.k; sd = true; } render(); });
    if (onClick) el.querySelectorAll("tbody tr").forEach(tr => tr.onclick = () => onClick(rows[+tr.dataset.i]));
  }
  render();
  return { render };
}

// ---------- charts ----------
let W = 760; // set per call via the w option, so text keeps its size in narrow exhibits
function ticks(max, n = 4) {
  if (!max) return [0];
  const raw = max / n, mag = Math.pow(10, Math.floor(Math.log10(raw))), step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= raw);
  const out = []; for (let v = 0; v < max + step; v += step) { out.push(v); if (v >= max) break; } return out;
}
// vertical bars over time. items: [{x:label, v:number, tip}]
export function barChart(items, { w = 760, height = 260, fmt = v => v, labelEvery = 1, color } = {}) {
  W = w;
  const pad = { l: 48, r: 8, t: 10, b: 26 }, iw = W - pad.l - pad.r, ih = height - pad.t - pad.b;
  const max = Math.max(...items.map(d => d.v), 0) * 1.05, tk = ticks(max), top = tk[tk.length - 1] || 1;
  const slot = iw / items.length, bw = Math.min(slot, 72), gap = Math.min(4, bw * 0.25), x0 = pad.l + (iw - bw * items.length) / 2;
  const y = v => pad.t + ih - (v / top) * ih;
  return `<svg class="chart" viewBox="0 0 ${W} ${height}" role="img">
    <g class="grid">${tk.map(t => `<line x1="${pad.l}" x2="${W - pad.r}" y1="${y(t)}" y2="${y(t)}"/><text x="${pad.l - 8}" y="${y(t) + 4}" text-anchor="end">${fmt(t)}</text>`).join("")}</g>
    ${items.map((d, i) => `<rect class="b${d.alt ? " alt" : ""}" ${color ? `style="fill:${color}"` : ""} x="${x0 + i * bw + gap / 2}" y="${y(d.v)}" width="${Math.max(1, bw - gap)}" height="${Math.max(0, pad.t + ih - y(d.v))}" rx="2" data-tip="${esc(d.tip || `${d.x}: ${fmt(d.v)}`)}"/>`).join("")}
    ${items.map((d, i) => i % labelEvery === 0 ? `<text x="${x0 + i * bw + bw / 2}" y="${height - 8}" text-anchor="middle">${esc(d.x)}</text>` : "").join("")}
    <line class="axis" x1="${pad.l}" x2="${W - pad.r}" y1="${pad.t + ih}" y2="${pad.t + ih}"/></svg>`;
}
// horizontal bars. items: [{label, v, tip, alt}]
export function hbarChart(items, { w = 760, fmt = v => v, row = 26, labelW = 190 } = {}) {
  W = w;
  const height = items.length * row + 8, iw = W - labelW - 64;
  const max = Math.max(...items.map(d => d.v), 0) || 1;
  return `<svg class="chart" viewBox="0 0 ${W} ${height}" role="img">${items.map((d, i) => {
    const y = 4 + i * row, w = Math.max(1, (d.v / max) * iw);
    return `<text class="lbl" x="${labelW - 10}" y="${y + row / 2 + 4}" text-anchor="end">${esc(d.label)}</text>
      <rect class="b${d.alt ? " alt" : ""}" x="${labelW}" y="${y + 5}" width="${w}" height="${row - 10}" rx="2" data-tip="${esc(d.tip || `${d.label}: ${fmt(d.v)}`)}"/>
      <text class="val" x="${labelW + w + 6}" y="${y + row / 2 + 4}">${fmt(d.v)}</text>`;
  }).join("")}</svg>`;
}
// ranges (p25..p75 with a median tick). items:[{label, lo, mid, hi, tip}], log scale optional
export function rangeChart(items, { w = 760, fmt = v => v, log = false, row = 34, labelW = 160, xmax, ticksAt } = {}) {
  W = w;
  const height = items.length * row + 30, iw = W - labelW - 20;
  const hi = xmax || Math.max(...items.map(d => d.hi)) * 1.08;
  const lo0 = log ? Math.min(...items.map(d => d.lo).filter(v => v > 0)) / 1.5 : 0;
  const x = v => labelW + (log ? (Math.log(Math.max(v, lo0)) - Math.log(lo0)) / (Math.log(hi) - Math.log(lo0)) : v / hi) * iw;
  const tk = ticksAt || (log ? [] : ticks(hi, 5));
  return `<svg class="chart" viewBox="0 0 ${W} ${height}" role="img">
    <g class="grid">${tk.filter(t => t >= lo0 && t <= hi).map(t => `<line x1="${x(t)}" x2="${x(t)}" y1="0" y2="${height - 24}"/><text x="${x(t)}" y="${height - 8}" text-anchor="middle">${fmt(t)}</text>`).join("")}</g>
    ${items.map((d, i) => { const y = 4 + i * row;
      return `<text class="lbl" x="${labelW - 12}" y="${y + row / 2 + 2}" text-anchor="end">${esc(d.label)}</text>
        <rect class="b" x="${x(d.lo)}" y="${y + 7}" width="${Math.max(2, x(d.hi) - x(d.lo))}" height="${row - 16}" rx="2" style="fill:var(--teal-soft)" data-tip="${esc(d.tip || "")}"/>
        <rect x="${x(d.mid) - 1.5}" y="${y + 3}" width="3" height="${row - 8}" fill="var(--navy)"/>`; }).join("")}</svg>`;
}
// two-series line chart. series:[{name,color,values:[{x,v}]}]
export function lineChart(series, { w = 760, height = 240, fmt = v => v, labelEvery = 26 } = {}) {
  W = w;
  const pad = { l: 52, r: 10, t: 10, b: 24 }, iw = W - pad.l - pad.r, ih = height - pad.t - pad.b;
  const n = series[0].values.length, max = Math.max(...series.flatMap(s => s.values.map(p => p.v))) * 1.05;
  const tk = ticks(max), top = tk[tk.length - 1] || 1;
  const x = i => pad.l + (i / Math.max(1, n - 1)) * iw, y = v => pad.t + ih - (v / top) * ih;
  return `<svg class="chart" viewBox="0 0 ${W} ${height}" role="img">
    <g class="grid">${tk.map(t => `<line x1="${pad.l}" x2="${W - pad.r}" y1="${y(t)}" y2="${y(t)}"/><text x="${pad.l - 8}" y="${y(t) + 4}" text-anchor="end">${fmt(t)}</text>`).join("")}</g>
    ${series.map(s => `<polyline fill="none" stroke="${s.color}" stroke-width="1.75" stroke-linejoin="round" points="${s.values.map((p, i) => `${x(i)},${y(p.v)}`).join(" ")}"/>`).join("")}
    ${series[0].values.map((p, i) => i % labelEvery === 0 ? `<text x="${x(i)}" y="${height - 6}" text-anchor="middle">${esc(p.x)}</text>` : "").join("")}
    ${series[0].values.map((p, i) => `<rect class="hit" x="${x(i) - iw / n / 2}" y="${pad.t}" width="${iw / n}" height="${ih}" data-tip="${esc(`${p.x}: ` + series.map(s => `${s.name} ${fmt(s.values[i].v)}`).join(" · "))}"/>`).join("")}</svg>`;
}
