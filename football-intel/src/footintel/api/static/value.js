/* Odds checker: model probability against the odds the user types in. */
const root = document.getElementById("root");
const SRC = root.dataset.src;
const STORE = "fi_value_odds";
const state = { data: null, comp: "all", odds: {}, coupon: [] };

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const pct = (p, d = 0) => `${(100 * p).toFixed(d)} %`;
const two = (x) => (x == null || !isFinite(x) ? "—" : x.toFixed(2));
const COMP = { "ENG-PL": "Premier League", "ESP-LL": "Liga", "ITA-SA": "Serie A", "GER-BL": "Bundesliga",
  "GER-DFB": "Coupe d'Allemagne", "UEFA-CL": "Ligue des champions", "UEFA-EL": "Ligue Europa", "UEFA-ECL": "Ligue Conférence" };

function load() { try { return JSON.parse(localStorage.getItem(STORE) || "{}"); } catch { return {}; } }
function save() { try { localStorage.setItem(STORE, JSON.stringify({ odds: state.odds, coupon: state.coupon })); } catch { /* storage blocked */ } }

function verdict(prob, odds) {
  if (!odds || odds <= 1) return { cls: "v-neutral", text: "—", value: null };
  const v = prob * odds - 1;
  if (v >= 0.05) return { cls: "v-good", text: `+${(100 * v).toFixed(1)} % valeur`, value: v };
  if (v <= -0.05) return { cls: "v-bad", text: `${(100 * v).toFixed(1)} % défavorable`, value: v };
  return { cls: "v-neutral", text: `${v >= 0 ? "+" : ""}${(100 * v).toFixed(1)} % neutre`, value: v };
}

const BEST = { "1": "H", X: "D", "2": "A" };
function marketCell(mk, key) {
  if (!mk || mk[key] == null) return "—";
  const best = BEST[key] ? `<br><span class="note">meilleure ${two(mk.best[BEST[key]])}</span>` : "";
  return `${pct(mk[key], 1)}${best}`;
}

function matchCard(m) {
  const p = Object.fromEntries(m.markets.map((x) => [x.key, x.prob]));
  const when = m.kickoff_utc ? new Date(m.kickoff_utc).toLocaleString("fr-FR", { weekday: "short", hour: "2-digit", minute: "2-digit" }) : m.kickoff_date;
  const inCoupon = state.coupon.find((c) => c.match === m.id);
  const GROUPS = { "1x2": "Résultat et double chance", goals: "Nombre de buts", btts: "Les deux équipes marquent", "1up": "1X2 1UP" };
  let group = "";
  const rows = m.markets.map((x) => {
    const head = x.note !== group
      ? `<tr class="group"><td colspan="7"><strong>${esc(GROUPS[x.note] || x.note)}</strong> <span class="note">${esc(state.data.reliability[x.note] || "")}</span></td></tr>`
      : "";
    group = x.note;
    const key = `${m.id}:${x.key}`;
    const odds = state.odds[key];
    const v = verdict(x.prob, odds);
    const chosen = inCoupon && inCoupon.key === x.key;
    return `${head}<tr class="mk">
      <td class="label">${esc(x.label)}</td>
      <td class="r num" data-h="Modèle">${pct(x.prob, 1)}</td>
      <td class="r num" data-h="Cote juste">${two(1 / x.prob)}</td>
      <td class="r num" data-h="Marché">${marketCell(m.market, x.key)}</td>
      <td class="r"><input type="number" step="0.01" min="1.01" inputmode="decimal" aria-label="Cote ${esc(x.label)}"
           id="o-${m.id}-${esc(x.key)}" data-key="${esc(key)}" value="${odds ?? ""}"></td>
      <td><span class="verdict ${v.cls}" id="v-${m.id}-${esc(x.key)}">${v.text}</span></td>
      <td><button class="add" data-match="${m.id}" data-market="${esc(x.key)}" ${inCoupon && !chosen ? "disabled" : ""}>
        ${chosen ? "retirer" : "+ combiné"}</button></td></tr>`;
  }).join("");
  return `<details class="match" ${inCoupon ? "open" : ""}>
    <summary><span class="teams">${esc(m.home)} – ${esc(m.away)}</span>
      <span class="meta">${esc(COMP[m.competition] || m.competition)} · ${esc(when)}</span>
      ${m.has_odds ? '<span class="pill ok">avec cotes de référence</span>' : `<span class="pill warn" title="${esc(state.data.reliability.no_odds)}">sans cotes : moins fiable</span>`}
      ${m.market ? `<span class="pill ok" title="${esc(state.data.reliability.market || "")}">marché : ${m.market.n_bookmakers} bookmakers</span>` : ""}
      <span class="probs" aria-label="Probabilités 1, X, 2"><span>1 ${pct(p["1"])}</span><span>X ${pct(p["X"])}</span><span>2 ${pct(p["2"])}</span></span>
    </summary>
    <div class="table-wrap"><table>
      <thead><tr><th>Sélection</th><th class="r">Modèle</th><th class="r">Cote juste</th><th class="r">Marché</th><th class="r">Ta cote</th><th>Verdict</th><th></th></tr></thead>
      <tbody>${rows}</tbody></table></div></details>`;
}

function renderList() {
  const ms = state.data.matches.filter((m) => state.comp === "all" || m.competition === state.comp);
  if (!ms.length) { document.getElementById("list").innerHTML = '<p class="empty">Aucun match prédit dans cette sélection.</p>'; return; }
  let html = "", day = "";
  for (const m of ms) {
    const d = new Date(m.kickoff_utc || m.kickoff_date).toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long" });
    if (d !== day) { html += `<h3 class="day">${esc(d)}</h3>`; day = d; }
    html += matchCard(m);
  }
  document.getElementById("list").innerHTML = html;
}

function renderFilters() {
  const comps = [...new Set(state.data.matches.map((m) => m.competition))];
  const btn = (c, label) => `<button aria-pressed="${state.comp === c}" data-comp="${esc(c)}">${esc(label)}</button>`;
  document.getElementById("filters").innerHTML = btn("all", "Toutes") + comps.map((c) => btn(c, COMP[c] || c)).join("");
}

function renderCoupon() {
  const list = state.coupon.map((c) => {
    const m = state.data.matches.find((x) => x.id === c.match);
    const mk = m && m.markets.find((x) => x.key === c.key);
    return m && mk ? { c, m, mk, odds: state.odds[`${m.id}:${mk.key}`] } : null;
  }).filter(Boolean);
  document.getElementById("sel").innerHTML = list.map(({ m, mk, odds }) =>
    `<li><span>${esc(m.home)} – ${esc(m.away)}<br><span class="muted small">${esc(mk.label)} · ${pct(mk.prob)} · cote ${odds ? two(odds) : "à saisir"}</span></span>
     <button data-remove="${m.id}" aria-label="Retirer">×</button></li>`).join("");
  document.getElementById("sel-empty").hidden = list.length > 0;
  document.getElementById("sum").hidden = list.length === 0;
  if (!list.length) { document.getElementById("c-note").textContent = ""; return; }
  const prob = list.reduce((a, x) => a * x.mk.prob, 1);
  const allOdds = list.every((x) => x.odds > 1);
  const odds = allOdds ? list.reduce((a, x) => a * x.odds, 1) : null;
  const payInput = parseFloat(document.getElementById("c-pay").value);
  const pay = payInput > 1 ? payInput : odds;
  document.getElementById("c-prob").textContent = `${pct(prob, prob < 0.01 ? 2 : 1)} (1 sur ${Math.round(1 / prob)})`;
  document.getElementById("c-fair").textContent = two(1 / prob);
  document.getElementById("c-odds").textContent = odds ? two(odds) : "cotes manquantes";
  const ev = pay ? prob * pay - 1 : null;
  const el = document.getElementById("c-ev");
  el.textContent = ev == null ? "—" : `${ev >= 0 ? "+" : ""}${(100 * ev).toFixed(1)} %`;
  el.style.color = ev == null ? "" : ev >= 0 ? "var(--good)" : "var(--bad)";
  document.getElementById("c-note").textContent = ev == null ? "Saisis la cote de chaque sélection."
    : `Sur 100 combinés identiques à 1 de mise, le modèle attend environ ${(100 * (1 + ev)).toFixed(0)} de retour. `
      + (list.length >= 5 ? "Plus le combiné est long, plus la marge du bookmaker se cumule." : "");
}

function render() { renderFilters(); renderList(); renderCoupon(); }

document.addEventListener("input", (e) => {
  const key = e.target.dataset && e.target.dataset.key;
  if (key) {
    const v = parseFloat(e.target.value);
    if (v > 1) state.odds[key] = v; else delete state.odds[key];
    const [mid, mkey] = key.split(":");
    const m = state.data.matches.find((x) => String(x.id) === mid);
    const mk = m.markets.find((x) => x.key === mkey);
    const vd = verdict(mk.prob, state.odds[key]);
    const cell = document.getElementById(`v-${mid}-${mkey}`);
    cell.className = `verdict ${vd.cls}`; cell.textContent = vd.text;
    save(); renderCoupon();
  }
  if (e.target.id === "c-pay") renderCoupon();
});
document.addEventListener("click", (e) => {
  const t = e.target.closest("button");
  if (!t) return;
  if (t.dataset.comp) { state.comp = t.dataset.comp; renderFilters(); renderList(); }
  if (t.dataset.match) {
    const id = Number(t.dataset.match), key = t.dataset.market;
    const i = state.coupon.findIndex((c) => c.match === id);
    if (i >= 0 && state.coupon[i].key === key) state.coupon.splice(i, 1);
    else if (i < 0) state.coupon.push({ match: id, key });
    save(); renderList(); renderCoupon();
  }
  if (t.dataset.remove) { state.coupon = state.coupon.filter((c) => c.match !== Number(t.dataset.remove)); save(); renderList(); renderCoupon(); }
});

(async () => {
  const saved = load();
  state.odds = saved.odds || {};
  try {
    if (window.fiGet) {
      await window.fiReady;
      state.data = await window.fiGet("/value-board");
    } else {
      const r = await fetch(SRC);
      if (!r.ok) throw new Error(r.status);
      state.data = await r.json();
    }
  } catch (err) {
    document.getElementById("stamp").textContent = "Prédictions indisponibles pour le moment.";
    return;
  }
  const ids = new Set(state.data.matches.map((m) => m.id));
  state.coupon = (saved.coupon || []).filter((c) => ids.has(c.match));
  const last = state.data.matches.map((m) => m.predicted_at).sort().pop();
  document.getElementById("stamp").textContent = `${state.data.matches.length} matchs prédits sur ${state.data.generated_for_days} jours`
    + (last ? ` · dernière prédiction le ${new Date(last).toLocaleString("fr-FR")}` : "")
    + (state.data.matches[0] ? ` · modèle ${state.data.matches[0].model}` : "");
  render();
})();
