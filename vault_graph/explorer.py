"""Render-Stufe v0: die analytische Werkbank (Variante A, read-only).

Aufbauend auf der schlanken topology.html. Drei methodisch getrennte Flaechen
ueber eine geteilte Selektion verbunden:

- Befunde: sortierbare Knotentabelle (datengestuetzt, reproduzierbar)
- Pflege: tote Links nach Quellknoten und Orphans (Diagnose, Pflege-Auffaelligkeit)
- Kontext: Force-Graph als Uebersicht, Community und Bruecken sind Hypothesen

Zusaetzlich zur Topologie traegt das PAYLOAD die Inhalts-Schicht (tags, type),
damit Facetten-Filter nach Community, Tag und type moeglich sind, ohne die
Pipeline neu zu laufen. Pro Knoten ein obsidian-Sprung ins echte Atom.

Read-only: schreibt nur das eigene output, ruehrt den Vault nicht an. Privacy
laeuft ueber denselben build_key_remap wie graph.json, anonymisierte
Business-Knoten tragen weder Klartext-Key noch Inhalts-Metadaten und werden aus
der Pflege-Triage herausgehalten.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

from vault_graph.parse import build_key_remap, export_path_for, normalize_tags


def render_explorer_html(
    graph: nx.DiGraph,
    topology: dict[str, Any],
    pragmatics: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _build_payload(graph, topology, pragmatics)
    vault_name = Path(graph.graph.get("vault_path", "obsidian")).name or "obsidian"
    html_doc = (
        _TEMPLATE
        .replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False))
        .replace("__VAULT_NAME__", json.dumps(vault_name))
    )
    output_path.write_text(html_doc, encoding="utf-8")


def _build_payload(
    graph: nx.DiGraph, topology: dict[str, Any], pragmatics: dict[str, Any]
) -> dict:
    centralities = topology["centralities"]
    communities = topology["communities"]
    bridges = set(topology["bridges"])
    k_core = topology["k_core"]

    folder_of = pragmatics["folder_of"]
    community_folder = pragmatics["community_folder"]
    outlier_keys = {o["key"] for o in pragmatics["outliers"]}

    key_remap = build_key_remap(graph)

    nodes = []
    for key, attrs in graph.nodes(data=True):
        c = centralities.get(key, {})
        export_key = key_remap[key]
        anon = bool(attrs.get("privacy_anonymized"))
        fm = attrs.get("frontmatter", {}) or {}
        cid = communities.get(key, -1)
        cf = community_folder.get(cid, {})
        # Privacy: anonymisierte Knoten geben keine Inhalts-Metadaten aus.
        tags = [] if anon else normalize_tags(fm)
        node_type = "" if anon else (str(fm.get("type")) if fm.get("type") else "")
        nodes.append({
            "id": export_key,
            "title": attrs.get("title", export_key),
            "path": export_path_for(key, export_key, attrs),
            "is_moc": bool(attrs.get("is_moc")),
            "anon": anon,
            "community": cid,
            "pagerank": round(c.get("pagerank", 0.0), 6),
            "degree": int(c.get("degree", 0)),
            "in_degree": int(c.get("in_degree", 0)),
            "out_degree": int(c.get("out_degree", 0)),
            "betweenness": round(c.get("betweenness", 0.0), 6),
            "k_core": k_core.get(key, 0),
            "is_bridge": key in bridges,
            "tags": tags,
            "type": node_type,
            "folder": folder_of.get(key, "(Wurzel)"),
            "outlier": key in outlier_keys,
            "comm_folder": cf.get("dominant_folder", ""),
            "comm_purity": round(cf.get("purity", 0.0), 3),
        })

    edges = [
        {"source": key_remap[u], "target": key_remap[v]} for u, v in graph.edges
    ]

    anon_keys = {k for k, a in graph.nodes(data=True) if a.get("privacy_anonymized")}
    # Pflege-Triage ist ein Vault-Pflegesignal. Tote Links und Orphans aus
    # anonymisierten Business-Knoten gehoeren nicht in diesen Scope und werden
    # ausgelassen, das haelt das Signal sauber und vermeidet jede Restleakage
    # ueber den toten Link-Text.
    dead_links = [
        {"from": key_remap[d["from"]], "to": d["to"]}
        for d in graph.graph.get("dead_links", [])
        if d["from"] not in anon_keys
    ]
    orphans = [
        key_remap[o] for o in graph.graph.get("orphans", []) if o not in anon_keys
    ]

    stats = topology["stats"]
    prag_stats = pragmatics["stats"]
    return {
        "nodes": nodes,
        "edges": edges,
        "dead_links": dead_links,
        "orphans": orphans,
        "stats": {
            "n_nodes": stats["n_nodes"],
            "n_edges": stats["n_edges"],
            "n_communities": stats["n_communities"],
            "modularity": round(topology["modularity"], 3),
            "n_bridges": stats["n_bridges"],
            "n_dead_links": len(dead_links),
            "n_orphans": len(orphans),
            "nmi": round(prag_stats["nmi_community_folder"], 3),
            "mean_purity": round(prag_stats["mean_community_purity"], 3),
            "n_outliers": prag_stats["n_outliers"],
        },
    }


_TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>vault-graph: Explorer</title>
<style>
  :root { --bg:#fafafa; --panel:#f5f5f5; --line:#ddd; --ink:#222; --muted:#666; --accent:#1d6fb8; --warn:#b8541d; }
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; height:100%; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--ink); }
  #app { display:flex; flex-direction:column; height:100vh; }
  header { padding:8px 14px; border-bottom:1px solid var(--line); background:white; }
  header h1 { font-size:15px; margin:0 0 6px 0; display:inline-block; }
  .stats { font-size:12px; color:var(--muted); display:inline-block; margin-left:14px; }
  .stats b { color:var(--ink); font-variant-numeric:tabular-nums; }
  .filters { display:flex; gap:8px; align-items:center; margin-top:8px; flex-wrap:wrap; }
  .filters input[type=search], .filters select { padding:4px 6px; border:1px solid #ccc; border-radius:3px; font-size:12px; background:white; }
  .filters input[type=search] { min-width:200px; }
  .filters label { font-size:12px; color:var(--muted); white-space:nowrap; }
  .legend { font-size:11px; color:var(--muted); margin-left:auto; }
  .legend b { color:var(--ink); }
  main { flex:1; display:flex; min-height:0; }
  #left { flex:1; min-width:440px; display:flex; flex-direction:column; border-right:1px solid var(--line); min-height:0; }
  .tabs { display:flex; border-bottom:1px solid var(--line); background:var(--panel); }
  .tab { padding:7px 14px; font-size:12px; cursor:pointer; border:none; background:none; color:var(--muted); border-bottom:2px solid transparent; }
  .tab.active { color:var(--ink); border-bottom-color:var(--accent); font-weight:600; }
  .tab .kind { font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:#999; margin-left:5px; }
  .panel { flex:1; overflow:auto; min-height:0; }
  .panel.hidden { display:none; }
  table { border-collapse:collapse; width:100%; font-size:12px; }
  thead th { position:sticky; top:0; background:#eee; text-align:left; padding:5px 8px; border-bottom:1px solid #ccc; cursor:pointer; white-space:nowrap; user-select:none; }
  thead th.hyp { color:var(--accent); }
  thead th .arrow { color:#999; font-size:10px; }
  tbody td { padding:4px 8px; border-bottom:1px solid #eee; white-space:nowrap; }
  tbody td.num { text-align:right; font-variant-numeric:tabular-nums; }
  tbody tr { cursor:pointer; }
  tbody tr:hover { background:#eef4fb; }
  tbody tr.sel { background:#d7e8f8; }
  tbody tr.anon td.title { color:var(--warn); font-style:italic; }
  .badge { display:inline-block; font-size:10px; padding:0 5px; border-radius:8px; background:#e3e3e3; color:#555; margin-left:4px; }
  .badge.moc { background:#dfe8d6; color:#3a6b2a; }
  .badge.bridge { background:#222; color:white; }
  .badge.outlier { background:#b8541d; color:white; }
  tbody tr.outlier td.folder { background:#fbf0e8; }
  #triage { padding:10px 12px; }
  #triage h3 { font-size:12px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); margin:14px 0 6px 0; }
  #triage h3:first-child { margin-top:0; }
  .triage-note { font-size:11px; color:#999; margin:0 0 8px 0; }
  .triage-row { display:flex; justify-content:space-between; gap:8px; font-size:12px; padding:3px 6px; border-bottom:1px solid #eee; cursor:pointer; }
  .triage-row:hover { background:#eef4fb; }
  .triage-row .cnt { color:var(--warn); font-variant-numeric:tabular-nums; font-weight:600; }
  .triage-sub { font-size:11px; color:var(--muted); padding:2px 6px 2px 18px; }
  #right { width:430px; display:flex; flex-direction:column; min-height:0; }
  #graph { flex:1; position:relative; background:white; border-bottom:1px solid var(--line); min-height:0; }
  #graph svg { width:100%; height:100%; cursor:grab; }
  #graph svg:active { cursor:grabbing; }
  .node { stroke:white; stroke-width:.5px; cursor:pointer; }
  .node.bridge { stroke:#111; stroke-width:2px; }
  .node.anon { stroke:#c00; stroke-width:1.5px; stroke-dasharray:2,2; }
  .node.dim { opacity:.08; }
  .node.hot { stroke:#000; stroke-width:2.5px; }
  .link { stroke:#ccc; stroke-opacity:.35; }
  .link.hot { stroke:var(--accent); stroke-opacity:.9; }
  .link.dim { stroke-opacity:.04; }
  #detail { height:240px; overflow:auto; padding:10px 12px; background:var(--panel); font-size:12px; }
  #detail.empty { color:#888; font-style:italic; }
  #detail dl { margin:0; }
  #detail dt { font-weight:600; color:var(--muted); margin-top:6px; font-size:11px; }
  #detail dd { margin:0; }
  #detail .title { font-size:14px; font-weight:600; margin:0 0 2px 0; }
  #detail .kindline { font-size:11px; color:#999; margin-bottom:8px; }
  #obs-jump { display:inline-block; margin-top:10px; padding:5px 10px; background:var(--accent); color:white; text-decoration:none; border-radius:3px; font-size:12px; }
  #obs-jump.disabled { background:#bbb; pointer-events:none; }
  .tagchip { display:inline-block; font-size:10px; padding:0 5px; border-radius:8px; background:#e7eef5; color:#3a5a78; margin:0 3px 3px 0; }
  .nbr { color:var(--accent); cursor:pointer; }
  .nbr:hover { text-decoration:underline; }
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>vault-graph Explorer</h1>
    <span class="stats" id="stats"></span>
    <div class="filters">
      <input type="search" id="f-q" placeholder="Titel suchen ...">
      <label>Community <select id="f-comm"></select></label>
      <label>Tag <select id="f-tag"></select></label>
      <label>type <select id="f-type"></select></label>
      <label>Ordner <select id="f-folder"></select></label>
      <label><input type="checkbox" id="f-bridge"> nur Bruecken</label>
      <label><input type="checkbox" id="f-orphan"> nur Orphans</label>
      <label><input type="checkbox" id="f-outlier"> nur Ausreisser</label>
      <span class="legend">Befund datengestuetzt &middot; Diagnose Pflege &middot; <b>Hypothese</b> topologisch ohne semantische Stuetze</span>
    </div>
  </header>
  <main>
    <div id="left">
      <div class="tabs">
        <button class="tab active" data-tab="befunde">Befunde <span class="kind">datengestuetzt</span></button>
        <button class="tab" data-tab="pflege">Pflege <span class="kind">Diagnose</span></button>
      </div>
      <div class="panel" id="panel-befunde">
        <table>
          <thead><tr id="thead-row"></tr></thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
      <div class="panel hidden" id="panel-pflege">
        <div id="triage"></div>
      </div>
    </div>
    <div id="right">
      <div id="graph"><svg></svg></div>
      <div id="detail" class="empty">Kein Knoten ausgewaehlt. Klick in Tabelle, Triage oder Graph.</div>
    </div>
  </main>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const PAYLOAD = __PAYLOAD__;
const VAULT = __VAULT_NAME__;
const NODES = PAYLOAD.nodes;
const byId = new Map(NODES.map(n => [n.id, n]));

// Adjacency for neighbour lookup and graph highlighting
const outAdj = new Map(), inAdj = new Map();
NODES.forEach(n => { outAdj.set(n.id, []); inAdj.set(n.id, []); });
PAYLOAD.edges.forEach(e => {
  if (outAdj.has(e.source)) outAdj.get(e.source).push(e.target);
  if (inAdj.has(e.target)) inAdj.get(e.target).push(e.source);
});

const state = {
  selected: null,
  sortKey: "pagerank",
  sortDir: -1,
  filter: { q:"", comm:"", tag:"", type:"", folder:"", bridge:false, orphan:false, outlier:false },
};
const orphanSet = new Set(PAYLOAD.orphans);

// --- Stats line ---
const s = PAYLOAD.stats;
document.getElementById("stats").innerHTML =
  `<b>${s.n_nodes}</b> Knoten &middot; <b>${s.n_edges}</b> Kanten &middot; ` +
  `<b>${s.n_communities}</b> Communities &middot; Modularity <b>${s.modularity}</b> &middot; ` +
  `<b>${s.n_bridges}</b> Bruecken &middot; <b>${s.n_dead_links}</b> tote Links &middot; <b>${s.n_orphans}</b> Orphans &middot; ` +
  `NMI <b>${s.nmi}</b> &middot; Reinheit <b>${s.mean_purity}</b> &middot; <b>${s.n_outliers}</b> Ausreisser`;

// --- Facets ---
function fillSelect(id, values, label) {
  const sel = document.getElementById(id);
  sel.innerHTML = `<option value="">alle</option>` +
    values.map(v => `<option value="${escapeAttr(String(v))}">${escapeHtml(label ? label(v) : String(v))}</option>`).join("");
}
const commValues = [...new Set(NODES.map(n => n.community))].filter(c => c >= 0).sort((a,b)=>a-b);
fillSelect("f-comm", commValues, c => `Community ${c}`);
const tagCounts = new Map();
NODES.forEach(n => n.tags.forEach(t => tagCounts.set(t, (tagCounts.get(t)||0)+1)));
const tagValues = [...tagCounts.keys()].sort((a,b) => tagCounts.get(b)-tagCounts.get(a) || a.localeCompare(b));
fillSelect("f-tag", tagValues, t => `${t} (${tagCounts.get(t)})`);
const typeValues = [...new Set(NODES.map(n => n.type).filter(Boolean))].sort();
fillSelect("f-type", typeValues);
const folderCounts = new Map();
NODES.forEach(n => folderCounts.set(n.folder, (folderCounts.get(n.folder)||0)+1));
const folderValues = [...folderCounts.keys()].sort((a,b) => folderCounts.get(b)-folderCounts.get(a) || a.localeCompare(b));
fillSelect("f-folder", folderValues, f => `${f} (${folderCounts.get(f)})`);

// --- Table ---
const COLS = [
  { key:"title", label:"Titel", hyp:false, fmt:n => titleCell(n) },
  { key:"type", label:"type", hyp:false, fmt:n => escapeHtml(n.type||"") },
  { key:"folder", label:"Ordner", hyp:false, fmt:n => folderCell(n) },
  { key:"community", label:"Comm.", hyp:true, num:true, fmt:n => n.community },
  { key:"pagerank", label:"PageRank", hyp:false, num:true, fmt:n => n.pagerank.toFixed(4) },
  { key:"degree", label:"Degree", hyp:false, num:true, fmt:n => `${n.degree}` },
  { key:"in_degree", label:"in", hyp:false, num:true, fmt:n => n.in_degree },
  { key:"out_degree", label:"out", hyp:false, num:true, fmt:n => n.out_degree },
  { key:"betweenness", label:"Betw.", hyp:false, num:true, fmt:n => n.betweenness.toFixed(4) },
  { key:"k_core", label:"K-Core", hyp:false, num:true, fmt:n => n.k_core },
  { key:"is_bridge", label:"Bruecke", hyp:true, num:false, fmt:n => n.is_bridge ? '<span class="badge bridge">Bruecke</span>' : "" },
];

function titleCell(n) {
  let h = escapeHtml(n.title);
  if (n.is_moc) h += '<span class="badge moc">MOC</span>';
  return h;
}

function folderCell(n) {
  let h = escapeHtml(n.folder);
  if (n.outlier) h += '<span class="badge outlier" title="liegt in fremdem Ordner trotz reiner Community">Ausreisser</span>';
  return h;
}

document.getElementById("thead-row").innerHTML = COLS.map(c =>
  `<th data-key="${c.key}" class="${c.hyp?'hyp':''}" title="${c.hyp?'Hypothese, topologisch ohne semantische Stuetze':'Befund'}">${c.label} <span class="arrow" data-arrow="${c.key}"></span></th>`
).join("");

function passesFilter(n) {
  const f = state.filter;
  if (f.q && !n.title.toLowerCase().includes(f.q)) return false;
  if (f.comm !== "" && String(n.community) !== f.comm) return false;
  if (f.tag && !n.tags.includes(f.tag)) return false;
  if (f.type && n.type !== f.type) return false;
  if (f.folder && n.folder !== f.folder) return false;
  if (f.bridge && !n.is_bridge) return false;
  if (f.orphan && !orphanSet.has(n.id)) return false;
  if (f.outlier && !n.outlier) return false;
  return true;
}

function visibleNodes() { return NODES.filter(passesFilter); }

function renderTable() {
  const rows = visibleNodes();
  const k = state.sortKey, dir = state.sortDir;
  rows.sort((a,b) => {
    let va = a[k], vb = b[k];
    if (typeof va === "string") return dir * va.localeCompare(vb);
    return dir * ((va||0) - (vb||0));
  });
  const tbody = document.getElementById("tbody");
  tbody.innerHTML = rows.map(n =>
    `<tr data-id="${escapeAttr(n.id)}" class="${n.anon?'anon':''} ${n.outlier?'outlier':''} ${n.id===state.selected?'sel':''}">` +
    COLS.map(c => `<td class="${c.num?'num':''} ${c.key==='title'?'title':''}">${c.fmt(n)}</td>`).join("") +
    `</tr>`
  ).join("");
  document.querySelectorAll("[data-arrow]").forEach(a => a.textContent = "");
  const arrow = document.querySelector(`[data-arrow="${state.sortKey}"]`);
  if (arrow) arrow.textContent = state.sortDir < 0 ? "v" : "^";
}

document.getElementById("tbody").addEventListener("click", e => {
  const tr = e.target.closest("tr");
  if (tr) selectNode(tr.dataset.id, false);
});

document.getElementById("thead-row").addEventListener("click", e => {
  const th = e.target.closest("th");
  if (!th) return;
  const key = th.dataset.key;
  if (state.sortKey === key) state.sortDir *= -1;
  else { state.sortKey = key; state.sortDir = (key==="title"||key==="type") ? 1 : -1; }
  renderTable();
});

// --- Triage (Diagnose) ---
function renderTriage() {
  const grouped = new Map();
  PAYLOAD.dead_links.forEach(d => {
    if (!grouped.has(d.from)) grouped.set(d.from, []);
    grouped.get(d.from).push(d.to);
  });
  const sources = [...grouped.entries()].sort((a,b) => b[1].length - a[1].length);
  let h = `<h3>Tote Links nach Quellknoten</h3>`;
  h += `<p class="triage-note">${PAYLOAD.dead_links.length} tote Links in ${sources.length} Quellknoten. Diagnose, kein Werturteil. Anonymisierte Business-Knoten ausgenommen.</p>`;
  h += sources.map(([from, tos]) =>
    `<div class="triage-row" data-id="${escapeAttr(from)}"><span>${escapeHtml(titleOf(from))}</span><span class="cnt">${tos.length}</span></div>`
  ).join("");
  h += `<h3>Orphans</h3>`;
  h += `<p class="triage-note">${PAYLOAD.orphans.length} Knoten ohne ein- oder ausgehende Links.</p>`;
  h += PAYLOAD.orphans.map(id =>
    `<div class="triage-row" data-id="${escapeAttr(id)}"><span>${escapeHtml(titleOf(id))}</span><span class="cnt">0</span></div>`
  ).join("");
  document.getElementById("triage").innerHTML = h;
}
function titleOf(id) { const n = byId.get(id); return n ? n.title : id; }

document.getElementById("triage").addEventListener("click", e => {
  const row = e.target.closest(".triage-row");
  if (row) selectNode(row.dataset.id, true);
});

// --- Tabs ---
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active");
  const tab = t.dataset.tab;
  document.getElementById("panel-befunde").classList.toggle("hidden", tab!=="befunde");
  document.getElementById("panel-pflege").classList.toggle("hidden", tab!=="pflege");
}));

// --- Filters ---
function bindFilter(id, key, ev, fn) {
  document.getElementById(id).addEventListener(ev, function() {
    state.filter[key] = fn(this);
    renderTable();
    applyGraphFilter();
  });
}
bindFilter("f-q", "q", "input", el => el.value.toLowerCase().trim());
bindFilter("f-comm", "comm", "change", el => el.value);
bindFilter("f-tag", "tag", "change", el => el.value);
bindFilter("f-type", "type", "change", el => el.value);
bindFilter("f-folder", "folder", "change", el => el.value);
bindFilter("f-bridge", "bridge", "change", el => el.checked);
bindFilter("f-orphan", "orphan", "change", el => el.checked);
bindFilter("f-outlier", "outlier", "change", el => el.checked);

// --- Graph (Kontext) ---
const svg = d3.select("#graph svg");
let gWidth = svg.node().clientWidth, gHeight = svg.node().clientHeight;
const communities = [...new Set(NODES.map(n => n.community))].sort((a,b)=>a-b);
const color = d3.scaleOrdinal().domain(communities).range(d3.schemeTableau10.concat(d3.schemeSet3));
const prMax = d3.max(NODES, n => n.pagerank) || 1;
const radius = d3.scaleSqrt().domain([0, prMax]).range([2.5, 16]);

const linkSel = svg.append("g").selectAll("line").data(PAYLOAD.edges).join("line").attr("class","link");
const nodeSel = svg.append("g").selectAll("circle").data(NODES).join("circle")
  .attr("class", d => "node" + (d.is_bridge?" bridge":"") + (d.anon?" anon":""))
  .attr("r", d => radius(d.pagerank))
  .attr("fill", d => color(d.community))
  .on("click", (_, d) => selectNode(d.id, false))
  .call(d3.drag()
    .on("start", (e,d) => { if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
    .on("drag", (e,d) => { d.fx=e.x; d.fy=e.y; })
    .on("end", (e,d) => { if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }));
nodeSel.append("title").text(d => `${d.title} (Community ${d.community})`);

const sim = d3.forceSimulation(NODES)
  .force("link", d3.forceLink(PAYLOAD.edges).id(d => d.id).distance(42).strength(0.55))
  .force("charge", d3.forceManyBody().strength(-85))
  .force("center", d3.forceCenter(gWidth/2, gHeight/2))
  .force("collide", d3.forceCollide().radius(d => radius(d.pagerank)+1))
  .alphaDecay(0.035)
  .on("tick", () => {
    linkSel.attr("x1", d=>d.source.x).attr("y1", d=>d.source.y).attr("x2", d=>d.target.x).attr("y2", d=>d.target.y);
    nodeSel.attr("cx", d=>d.x).attr("cy", d=>d.y);
  });

svg.call(d3.zoom().scaleExtent([0.12, 6]).on("zoom", ev => svg.selectAll("g").attr("transform", ev.transform)));

function applyGraphFilter() {
  const vis = new Set(visibleNodes().map(n => n.id));
  nodeSel.classed("dim", d => !vis.has(d.id));
  linkSel.classed("dim", d => !vis.has(d.source.id) || !vis.has(d.target.id));
}

// --- Shared selection ---
function selectNode(id, switchToBefunde) {
  state.selected = id;
  // table highlight without full rerender
  document.querySelectorAll("#tbody tr.sel").forEach(tr => tr.classList.remove("sel"));
  const tr = document.querySelector(`#tbody tr[data-id="${cssEscape(id)}"]`);
  if (tr) { tr.classList.add("sel"); tr.scrollIntoView({block:"nearest"}); }
  // graph highlight: selected + neighbours
  const nbrs = new Set([id, ...(outAdj.get(id)||[]), ...(inAdj.get(id)||[])]);
  nodeSel.classed("hot", d => d.id===id).classed("dim", d => !nbrs.has(d.id));
  linkSel.classed("hot", d => d.source.id===id || d.target.id===id)
         .classed("dim", d => !(d.source.id===id || d.target.id===id));
  renderDetail(id);
}

function renderDetail(id) {
  const n = byId.get(id);
  const el = document.getElementById("detail");
  if (!n) { el.className = "empty"; el.textContent = "Kein Knoten."; return; }
  el.className = "";
  const inN = inAdj.get(id)||[], outN = outAdj.get(id)||[];
  const tagsHtml = n.tags.length ? n.tags.map(t => `<span class="tagchip">${escapeHtml(t)}</span>`).join("") : '<span style="color:#999">keine</span>';
  const nbrLinks = arr => arr.length
    ? arr.slice(0,12).map(x => `<span class="nbr" data-id="${escapeAttr(x)}">${escapeHtml(titleOf(x))}</span>`).join(", ") + (arr.length>12?` (+${arr.length-12})`:"")
    : '<span style="color:#999">keine</span>';
  el.innerHTML = `
    <div class="title">${escapeHtml(n.title)}${n.is_moc?'<span class="badge moc">MOC</span>':''}${n.is_bridge?'<span class="badge bridge">Bruecke</span>':''}</div>
    <div class="kindline">${escapeHtml(n.path)}</div>
    <dl>
      <dt>type / tags</dt><dd>${escapeHtml(n.type||"-")} ${tagsHtml}</dd>
      <dt>Ordner</dt><dd>${escapeHtml(n.folder)}${n.outlier?' <span class="badge outlier">Ausreisser</span>':''}</dd>
      <dt>Community <span style="color:#1d6fb8">(Hypothese)</span></dt><dd>${n.community}</dd>
      <dt>Triangulation <span style="color:#b8541d">(Diagnose)</span></dt><dd>Community-Ordner ${escapeHtml(n.comm_folder||"-")}, Reinheit ${n.comm_purity}${n.outlier?', dieser Knoten liegt im fremden Ordner':''}</dd>
      <dt>PageRank / Betweenness</dt><dd>${n.pagerank.toFixed(4)} / ${n.betweenness.toFixed(4)}</dd>
      <dt>Degree</dt><dd>${n.degree} (in ${n.in_degree}, out ${n.out_degree}), K-Core ${n.k_core}</dd>
      <dt>verweist auf</dt><dd>${nbrLinks(outN)}</dd>
      <dt>referenziert von</dt><dd>${nbrLinks(inN)}</dd>
    </dl>
    <a id="obs-jump" class="${n.anon?'disabled':''}" href="${n.anon?'#':obsidianUri(n.path)}">${n.anon?'anonymisiert, kein Sprung':'In Obsidian oeffnen'}</a>
  `;
}

document.getElementById("detail").addEventListener("click", e => {
  const nbr = e.target.closest(".nbr");
  if (nbr) selectNode(nbr.dataset.id, true);
});

function obsidianUri(path) {
  const file = path.replace(/\.md$/, "");
  return `obsidian://open?vault=${encodeURIComponent(VAULT)}&file=${encodeURIComponent(file)}`;
}

// --- helpers ---
function escapeHtml(s){ return (s==null?"":String(s)).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function escapeAttr(s){ return escapeHtml(s); }
function cssEscape(s){ return (window.CSS && CSS.escape) ? CSS.escape(s) : String(s).replace(/["\\\]]/g, "\\$&"); }

// --- init ---
renderTable();
renderTriage();
window.addEventListener("resize", () => {
  gWidth = svg.node().clientWidth; gHeight = svg.node().clientHeight;
  sim.force("center", d3.forceCenter(gWidth/2, gHeight/2)).alpha(0.2).restart();
});
</script>
</body>
</html>"""
