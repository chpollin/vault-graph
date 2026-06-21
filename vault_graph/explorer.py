"""Render-Stufe: die analytische Werkbank explorer.html (Phase A, read-only).

Flaechenumkehr gegenueber der ersten Werkbank: der Graph ist die Hauptflaeche,
Tabelle und Detail sind Begleiter, die sich aus der Graph-Auswahl speisen.

- Graph als ruhige Buehne. Kanten im Ruhezustand ausgeblendet, erst bei
  Knoten-Auswahl gezeigt (De-Hairball). Stabile Positionen ueber eine geseedete
  Zufallsquelle der Simulation, gleicher Vault-Stand fuehrt zu gleichem Layout.
- Drei Linsen ueber dieselbe Karte. Struktur (Communities, Bruecken, Hubs),
  Pflege (tote Links, Orphans, Ausreisser) und Wachstum (Geruest fuer die
  semantische Schicht ab Phase B, vorerst leer und so benannt).
- Aussagetyp als durchgehendes Farbsystem. Befund, Diagnose und Hypothese tragen
  je einen festen Akzent als Knotenring, in Graph, Tabelle und Detail dieselbe
  Bedeutung. Die Community traegt die Knotenfuellung, die Akzente sind die
  einzigen kraeftigen Farben.
- Begleittabelle als eingeklappte Schublade unter dem Graphen, im Ruhezustand
  zwei tragende Spalten plus ein Leitmass, der Rest hinter einer Aufklapp-Option.

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
<title>vault-graph</title>
<style>
  :root {
    --bg:#fafafa; --panel:#f4f4f5; --line:#dddddd; --ink:#222; --muted:#6b6b6b;
    --befund:#3a6ea5; --diagnose:#b8541d; --hypothese:#7a5ea5; --anon:#c0392b;
  }
  * { box-sizing:border-box; }
  html, body { margin:0; height:100%; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--ink); }
  #app { display:flex; flex-direction:column; height:100vh; }

  /* header */
  header { display:flex; align-items:center; gap:18px; padding:8px 16px; border-bottom:1px solid var(--line); background:#fff; }
  header .brand { font-size:14px; font-weight:600; letter-spacing:.2px; }
  .lenses { display:flex; gap:5px; }
  .lens { padding:5px 13px; font-size:12px; border:1px solid var(--line); background:#fff; color:var(--muted); border-radius:14px; cursor:pointer; }
  .lens:hover { border-color:#bbb; }
  .lens.active { color:#fff; border-color:transparent; }
  .lens[data-lens=struktur].active { background:var(--befund); }
  .lens[data-lens=pflege].active { background:var(--diagnose); }
  .lens[data-lens=wachstum].active { background:var(--hypothese); }
  .statgroups { margin-left:auto; display:flex; gap:20px; }
  .statgroups .g { display:flex; flex-direction:column; line-height:1.35; }
  .statgroups .lab { text-transform:uppercase; letter-spacing:.5px; font-size:9px; color:#a0a0a0; }
  .statgroups .val { font-size:11px; color:var(--muted); font-variant-numeric:tabular-nums; white-space:nowrap; }
  .statgroups .val b { color:var(--ink); font-weight:600; }

  /* main: rail | stage | detail */
  main { flex:1; display:flex; min-height:0; }
  #rail { width:214px; flex:none; border-right:1px solid var(--line); background:var(--panel); padding:11px 11px 16px; overflow:auto; display:flex; flex-direction:column; gap:9px; }
  #rail h4 { font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:#a0a0a0; margin:6px 0 1px; }
  #rail input[type=search], #rail select { width:100%; padding:4px 6px; border:1px solid #ccc; border-radius:3px; font-size:12px; background:#fff; }
  #rail label.chk { display:flex; align-items:center; gap:7px; font-size:12px; color:var(--muted); cursor:pointer; }
  .legend { display:flex; flex-direction:column; gap:4px; font-size:11px; color:var(--muted); margin-top:2px; }
  .legend .row { display:flex; align-items:center; gap:7px; }
  .legend .dot { width:11px; height:11px; border-radius:50%; background:#e9e9ea; border:2px solid; flex:none; }
  .legend .dot.befund { border-color:var(--befund); }
  .legend .dot.diagnose { border-color:var(--diagnose); }
  .legend .dot.hypothese { border-color:var(--hypothese); }
  .legend .dot.anon { border-color:var(--anon); border-style:dashed; background:#fff; }

  #stage { flex:1; position:relative; background:#fff; min-width:0; }
  #stage svg { width:100%; height:100%; cursor:grab; }
  #stage svg:active { cursor:grabbing; }
  .lens-note { position:absolute; left:50%; top:12px; transform:translateX(-50%); font-size:11px; color:var(--muted); background:rgba(255,255,255,.86); padding:4px 12px; border:1px solid var(--line); border-radius:12px; pointer-events:none; max-width:80%; text-align:center; }
  .node { cursor:pointer; stroke:#c2c8cf; stroke-width:1px; }
  .node.s-befund { stroke:var(--befund); stroke-width:1px; }
  .node.s-diagnose { stroke:var(--diagnose); stroke-width:2.2px; }
  .node.s-hypothese { stroke:var(--hypothese); stroke-width:2.2px; }
  .node.anon { stroke:var(--anon); stroke-width:1.6px; stroke-dasharray:2,2; }
  .node.dim { opacity:.09; }
  .node.hot { stroke:#000; stroke-width:2.6px; }
  .link { stroke:#c9c9c9; stroke-opacity:0; }
  .link.shown { stroke-opacity:.16; }
  .link.hot { stroke:var(--befund); stroke-opacity:.85; stroke-width:1.4px; }

  #detail { width:300px; flex:none; border-left:1px solid var(--line); background:var(--panel); overflow:auto; padding:13px; font-size:12px; }
  #detail.empty { color:#9a9a9a; font-style:italic; display:flex; align-items:center; text-align:center; }
  #detail .stype { display:inline-block; font-size:10px; text-transform:uppercase; letter-spacing:.5px; padding:1px 7px; border-radius:9px; color:#fff; margin-bottom:7px; }
  #detail .stype.befund { background:var(--befund); }
  #detail .stype.diagnose { background:var(--diagnose); }
  #detail .stype.hypothese { background:var(--hypothese); }
  #detail .title { font-size:14px; font-weight:600; margin:0 0 2px; }
  #detail .pathline { font-size:11px; color:#999; margin-bottom:9px; word-break:break-all; }
  #detail dl { margin:0; }
  #detail dt { font-weight:600; color:var(--muted); margin-top:7px; font-size:11px; }
  #detail dd { margin:0; }
  .badge { display:inline-block; font-size:10px; padding:0 5px; border-radius:8px; background:#e3e3e3; color:#555; margin-left:4px; }
  .badge.moc { background:#dfe8d6; color:#3a6b2a; }
  .badge.bridge { background:#ece4f4; color:#5a3f86; }
  .badge.outlier { background:#f4e2d6; color:#9a4516; }
  .tagchip { display:inline-block; font-size:10px; padding:0 5px; border-radius:8px; background:#e7eef5; color:#3a5a78; margin:0 3px 3px 0; }
  .nbr { color:var(--befund); cursor:pointer; }
  .nbr:hover { text-decoration:underline; }
  #obs-jump { display:inline-block; margin-top:12px; padding:5px 11px; background:var(--befund); color:#fff; text-decoration:none; border-radius:3px; font-size:12px; }
  #obs-jump.disabled { background:#bbb; pointer-events:none; }

  /* table dock */
  #dock { flex:none; border-top:1px solid var(--line); background:#fff; display:flex; flex-direction:column; max-height:44vh; }
  #dock.collapsed { max-height:none; }
  #dock.collapsed .dock-body { display:none; }
  .dock-bar { display:flex; align-items:center; gap:10px; padding:6px 14px; cursor:pointer; font-size:12px; color:var(--muted); user-select:none; }
  #dock:not(.collapsed) .dock-bar { border-bottom:1px solid var(--line); }
  .dock-bar .caret { color:#999; font-size:10px; width:10px; }
  .dock-bar .dock-count { color:#999; }
  .dock-bar .cols { margin-left:auto; }
  .dock-body { overflow:auto; min-height:0; }
  .hidden { display:none; }
  table { border-collapse:collapse; width:100%; font-size:12px; }
  thead th { position:sticky; top:0; background:#f0f0f0; text-align:left; padding:5px 9px; border-bottom:1px solid #ccc; cursor:pointer; white-space:nowrap; user-select:none; }
  thead th.acc { color:var(--hypothese); }
  thead th .arrow { color:#999; font-size:10px; }
  tbody td { padding:4px 9px; border-bottom:1px solid #eee; white-space:nowrap; }
  tbody td.num { text-align:right; font-variant-numeric:tabular-nums; }
  tbody tr { cursor:pointer; }
  tbody tr:hover { background:#eef4fb; }
  tbody tr.sel { background:#d7e8f8; }
  tbody td.title .sdot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; vertical-align:middle; }
  tbody td.title .sdot.befund { background:var(--befund); }
  tbody td.title .sdot.diagnose { background:var(--diagnose); }
  tbody td.title .sdot.hypothese { background:var(--hypothese); }
  tbody tr.anon td.title { color:var(--anon); font-style:italic; }
  #triage { padding:10px 14px; }
  #triage h3 { font-size:11px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); margin:14px 0 5px; }
  #triage h3:first-child { margin-top:0; }
  .triage-note { font-size:11px; color:#999; margin:0 0 7px; }
  .triage-row { display:flex; justify-content:space-between; gap:8px; font-size:12px; padding:3px 7px; border-bottom:1px solid #eee; cursor:pointer; }
  .triage-row:hover { background:#fbf0e8; }
  .triage-row .cnt { color:var(--diagnose); font-variant-numeric:tabular-nums; font-weight:600; }
  #wachstum-note { padding:18px 16px; font-size:12px; color:var(--muted); max-width:640px; }
</style>
</head>
<body>
<div id="app">
  <header>
    <span class="brand">vault-graph</span>
    <div class="lenses">
      <button class="lens active" data-lens="struktur">Struktur</button>
      <button class="lens" data-lens="pflege">Pflege</button>
      <button class="lens" data-lens="wachstum">Wachstum</button>
    </div>
    <div class="statgroups" id="statgroups"></div>
  </header>
  <main>
    <aside id="rail">
      <h4>Suche</h4>
      <input type="search" id="f-q" placeholder="Titel ...">
      <h4>Facetten</h4>
      <select id="f-comm"></select>
      <select id="f-tag"></select>
      <select id="f-type"></select>
      <select id="f-folder"></select>
      <label class="chk"><input type="checkbox" id="f-bridge"> nur Bruecken</label>
      <label class="chk"><input type="checkbox" id="f-orphan"> nur Orphans</label>
      <label class="chk"><input type="checkbox" id="f-outlier"> nur Ausreisser</label>
      <h4>Graph</h4>
      <label class="chk"><input type="checkbox" id="f-edges"> Kanten schwach zeigen</label>
      <h4>Aussagetyp</h4>
      <div class="legend">
        <div class="row"><span class="dot befund"></span>Befund, datengestuetzt</div>
        <div class="row"><span class="dot diagnose"></span>Diagnose, Pflege</div>
        <div class="row"><span class="dot hypothese"></span>Hypothese, topologisch</div>
        <div class="row"><span class="dot anon"></span>anonymisiert, kein Sprung</div>
      </div>
    </aside>
    <section id="stage">
      <svg></svg>
      <div class="lens-note" id="lens-note"></div>
    </section>
    <aside id="detail" class="empty">Kein Knoten gewaehlt. Klick einen Knoten im Graphen, in der Tabelle oder in der Triage.</aside>
  </main>
  <section id="dock" class="collapsed">
    <div class="dock-bar" id="dock-bar">
      <span class="caret" id="dock-caret">&#9654;</span>
      <span id="dock-title">Tabelle</span>
      <span class="dock-count" id="dock-count"></span>
      <label class="chk cols" id="cols-wrap"><input type="checkbox" id="cols-toggle"> mehr Spalten</label>
    </div>
    <div class="dock-body" id="dock-body">
      <div id="dock-table">
        <table><thead><tr id="thead-row"></tr></thead><tbody id="tbody"></tbody></table>
      </div>
      <div id="dock-triage" class="hidden"><div id="triage"></div></div>
      <div id="dock-wachstum" class="hidden">
        <div id="wachstum-note">
          Wachstums-Linse. Hier wird ab Phase B die semantische Schicht liegen,
          inhaltliche Aehnlichkeit ueber Embeddings als billiger Scout und darueber
          eine getypte, menschlich bestaetigte Relationskarte. Noch nicht gebaut,
          die Karte zeigt in dieser Linse vorerst nur den ruhenden Graphen.
        </div>
      </div>
    </div>
  </section>
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

const orphanSet = new Set(PAYLOAD.orphans);
const deadSourceSet = new Set(PAYLOAD.dead_links.map(d => d.from));

// Statement type per node. Diagnose (Pflege-Auffaelligkeit) dominiert, dann
// Hypothese (topologische Bruecke), sonst Befund. Anon wird separat als Ring
// gezeigt und ueberschreibt die Aussagetyp-Farbe nicht inhaltlich.
function statementOf(n) {
  if (n.outlier || orphanSet.has(n.id) || deadSourceSet.has(n.id)) return "diagnose";
  if (n.is_bridge) return "hypothese";
  return "befund";
}

const state = {
  lens: "struktur",
  selected: null,
  sortKey: "pagerank",
  sortDir: -1,
  showExtra: false,
  showEdges: false,
  filter: { q:"", comm:"", tag:"", type:"", folder:"", bridge:false, orphan:false, outlier:false },
};

// --- Grouped status line ---
const s = PAYLOAD.stats;
function statGroup(lab, html) { return `<div class="g"><span class="lab">${lab}</span><span class="val">${html}</span></div>`; }
document.getElementById("statgroups").innerHTML =
  statGroup("Struktur", `<b>${s.n_nodes}</b> Knoten &middot; <b>${s.n_edges}</b> Kanten &middot; <b>${s.n_communities}</b> Communities &middot; Mod. <b>${s.modularity}</b>`) +
  statGroup("Pflege", `<b>${s.n_dead_links}</b> tote Links &middot; <b>${s.n_orphans}</b> Orphans`) +
  statGroup("Triangulation", `NMI <b>${s.nmi}</b> &middot; Reinheit <b>${s.mean_purity}</b> &middot; <b>${s.n_outliers}</b> Ausreisser &middot; <b>${s.n_bridges}</b> Bruecken`);

// --- Facets ---
function fillSelect(id, values, label) {
  const sel = document.getElementById(id);
  sel.innerHTML = `<option value="">${label ? label.all : "alle"}</option>` +
    values.map(v => `<option value="${escapeAttr(String(v))}">${escapeHtml(label && label.fmt ? label.fmt(v) : String(v))}</option>`).join("");
}
const commValues = [...new Set(NODES.map(n => n.community))].filter(c => c >= 0).sort((a,b)=>a-b);
fillSelect("f-comm", commValues, { all:"alle Communities", fmt:c => `Community ${c}` });
const tagCounts = new Map();
NODES.forEach(n => n.tags.forEach(t => tagCounts.set(t, (tagCounts.get(t)||0)+1)));
const tagValues = [...tagCounts.keys()].sort((a,b) => tagCounts.get(b)-tagCounts.get(a) || a.localeCompare(b));
fillSelect("f-tag", tagValues, { all:"alle Tags", fmt:t => `${t} (${tagCounts.get(t)})` });
const typeValues = [...new Set(NODES.map(n => n.type).filter(Boolean))].sort();
fillSelect("f-type", typeValues, { all:"alle types" });
const folderCounts = new Map();
NODES.forEach(n => folderCounts.set(n.folder, (folderCounts.get(n.folder)||0)+1));
const folderValues = [...folderCounts.keys()].sort((a,b) => folderCounts.get(b)-folderCounts.get(a) || a.localeCompare(b));
fillSelect("f-folder", folderValues, { all:"alle Ordner", fmt:f => `${f} (${folderCounts.get(f)})` });

// --- Table: base columns always, extra columns behind a toggle ---
const COLS = [
  { key:"title", label:"Titel", base:true, fmt:n => titleCell(n) },
  { key:"community", label:"Comm.", base:true, acc:true, num:true, fmt:n => n.community },
  { key:"pagerank", label:"PageRank", base:true, num:true, fmt:n => n.pagerank.toFixed(4) },
  { key:"type", label:"type", base:false, fmt:n => escapeHtml(n.type||"") },
  { key:"folder", label:"Ordner", base:false, fmt:n => folderCell(n) },
  { key:"degree", label:"Degree", base:false, num:true, fmt:n => `${n.degree}` },
  { key:"in_degree", label:"in", base:false, num:true, fmt:n => n.in_degree },
  { key:"out_degree", label:"out", base:false, num:true, fmt:n => n.out_degree },
  { key:"betweenness", label:"Betw.", base:false, num:true, fmt:n => n.betweenness.toFixed(4) },
  { key:"k_core", label:"K-Core", base:false, num:true, fmt:n => n.k_core },
  { key:"is_bridge", label:"Bruecke", base:false, acc:true, fmt:n => n.is_bridge ? '<span class="badge bridge">Bruecke</span>' : "" },
];
function activeCols() { return COLS.filter(c => c.base || state.showExtra); }

function titleCell(n) {
  let h = `<span class="sdot ${statementOf(n)}"></span>` + escapeHtml(n.title);
  if (n.is_moc) h += '<span class="badge moc">MOC</span>';
  return h;
}
function folderCell(n) {
  let h = escapeHtml(n.folder);
  if (n.outlier) h += '<span class="badge outlier" title="liegt in fremdem Ordner trotz reiner Community">Ausreisser</span>';
  return h;
}

function renderHead() {
  document.getElementById("thead-row").innerHTML = activeCols().map(c =>
    `<th data-key="${c.key}" class="${c.acc?'acc':''}" title="${c.acc?'Hypothese, topologisch ohne semantische Stuetze':'Befund'}">${c.label} <span class="arrow" data-arrow="${c.key}"></span></th>`
  ).join("");
}

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
  const cols = activeCols();
  const rows = visibleNodes();
  const k = state.sortKey, dir = state.sortDir;
  rows.sort((a,b) => {
    let va = a[k], vb = b[k];
    if (typeof va === "string") return dir * va.localeCompare(vb);
    return dir * ((va||0) - (vb||0));
  });
  document.getElementById("tbody").innerHTML = rows.map(n =>
    `<tr data-id="${escapeAttr(n.id)}" class="${n.anon?'anon':''} ${n.id===state.selected?'sel':''}">` +
    cols.map(c => `<td class="${c.num?'num':''} ${c.key==='title'?'title':''}">${c.fmt(n)}</td>`).join("") +
    `</tr>`
  ).join("");
  document.querySelectorAll("[data-arrow]").forEach(a => a.textContent = "");
  const arrow = document.querySelector(`[data-arrow="${state.sortKey}"]`);
  if (arrow) arrow.textContent = state.sortDir < 0 ? "v" : "^";
  if (state.lens !== "pflege" && state.lens !== "wachstum")
    document.getElementById("dock-count").textContent = `${rows.length} Knoten`;
}

document.getElementById("tbody").addEventListener("click", e => {
  const tr = e.target.closest("tr");
  if (tr) selectNode(tr.dataset.id);
});
document.getElementById("thead-row").addEventListener("click", e => {
  const th = e.target.closest("th");
  if (!th) return;
  const key = th.dataset.key;
  if (state.sortKey === key) state.sortDir *= -1;
  else { state.sortKey = key; state.sortDir = (key==="title"||key==="type"||key==="folder") ? 1 : -1; }
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
  if (row) selectNode(row.dataset.id);
});

// --- Lenses ---
const LENS_NOTE = {
  struktur: "Struktur. Communities als Knotenfarbe, Bruecken violett, Groesse nach PageRank. Kante bei Auswahl.",
  pflege: "Pflege. Tote Links, Orphans und Ausreisser hervorgehoben, alles uebrige zurueckgenommen.",
  wachstum: "Wachstum. Geruest fuer die semantische Schicht ab Phase B, noch leer.",
};
function setLens(lens) {
  state.lens = lens;
  document.querySelectorAll(".lens").forEach(b => b.classList.toggle("active", b.dataset.lens===lens));
  document.getElementById("lens-note").textContent = LENS_NOTE[lens];
  const title = { struktur:"Tabelle", pflege:"Triage", wachstum:"Wachstum" }[lens];
  document.getElementById("dock-title").textContent = title;
  document.getElementById("dock-table").classList.toggle("hidden", lens!=="struktur");
  document.getElementById("dock-triage").classList.toggle("hidden", lens!=="pflege");
  document.getElementById("dock-wachstum").classList.toggle("hidden", lens!=="wachstum");
  document.getElementById("cols-wrap").style.display = lens==="struktur" ? "" : "none";
  const dc = document.getElementById("dock-count");
  if (lens==="pflege") dc.textContent = `${PAYLOAD.dead_links.length} tote Links, ${PAYLOAD.orphans.length} Orphans`;
  else if (lens==="wachstum") dc.textContent = "";
  else renderTable();
  updateGraph();
}
document.querySelectorAll(".lens").forEach(b => b.addEventListener("click", () => setLens(b.dataset.lens)));

// --- Dock ---
const dock = document.getElementById("dock");
document.getElementById("dock-bar").addEventListener("click", e => {
  if (e.target.closest("#cols-wrap")) return; // toggle handled separately
  dock.classList.toggle("collapsed");
  document.getElementById("dock-caret").innerHTML = dock.classList.contains("collapsed") ? "&#9654;" : "&#9660;";
});
document.getElementById("cols-toggle").addEventListener("change", function() {
  state.showExtra = this.checked;
  renderHead(); renderTable();
});

// --- Filters ---
function bindFilter(id, key, ev, fn) {
  document.getElementById(id).addEventListener(ev, function() {
    state.filter[key] = fn(this);
    renderTable();
    updateGraph();
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
document.getElementById("f-edges").addEventListener("change", function() {
  state.showEdges = this.checked; updateGraph();
});

// --- Graph (the stage) ---
const svg = d3.select("#stage svg");
let gWidth = svg.node().clientWidth || 800, gHeight = svg.node().clientHeight || 600;
const communities = [...new Set(NODES.map(n => n.community))].sort((a,b)=>a-b);
const color = d3.scaleOrdinal().domain(communities).range(d3.schemeTableau10.concat(d3.schemeSet3));
const prMax = d3.max(NODES, n => n.pagerank) || 1;
const radius = d3.scaleSqrt().domain([0, prMax]).range([3, 15]);

// Seeded random source -> deterministic layout for a given vault state.
function mulberry32(a) {
  return function() {
    a |= 0; a = a + 0x6D2B79F5 | 0;
    let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

const linkSel = svg.append("g").selectAll("line").data(PAYLOAD.edges).join("line").attr("class","link");
const nodeSel = svg.append("g").selectAll("circle").data(NODES).join("circle")
  .attr("r", d => radius(d.pagerank))
  .attr("fill", d => color(d.community))
  .on("click", (_, d) => selectNode(d.id))
  .call(d3.drag()
    .on("start", (e,d) => { if(!e.active) sim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
    .on("drag", (e,d) => { d.fx=e.x; d.fy=e.y; })
    .on("end", (e,d) => { if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }));
nodeSel.append("title").text(d => `${d.title} (Community ${d.community})`);

const sim = d3.forceSimulation(NODES)
  .randomSource(mulberry32(0x9e3779b9))
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

function idOf(x) { return (x && typeof x === "object") ? x.id : x; }

// Single source of node/link styling from lens + filter + selection.
function lensActive(n) {
  if (state.lens === "pflege") return statementOf(n) === "diagnose";
  return true; // struktur and wachstum show all (wachstum dims via selection-less rest)
}
function updateGraph() {
  const sel = state.selected;
  let nbrs = null;
  if (sel) nbrs = new Set([sel, ...(outAdj.get(sel)||[]), ...(inAdj.get(sel)||[])]);
  nodeSel
    .attr("class", d => {
      let c = "node s-" + statementOf(d);
      if (d.anon) c += " anon";
      if (sel && d.id === sel) c += " hot";
      const dim = sel ? !nbrs.has(d.id) : (!passesFilter(d) || !lensActive(d));
      if (dim) c += " dim";
      return c;
    });
  linkSel
    .classed("hot", d => sel && (idOf(d.source)===sel || idOf(d.target)===sel))
    .classed("shown", d => !sel && state.showEdges);
}

// --- Shared selection ---
function selectNode(id) {
  state.selected = id;
  document.querySelectorAll("#tbody tr.sel").forEach(tr => tr.classList.remove("sel"));
  const tr = document.querySelector(`#tbody tr[data-id="${cssEscape(id)}"]`);
  if (tr) {
    tr.classList.add("sel");
    if (dock.classList.contains("collapsed") && state.lens === "struktur") {
      dock.classList.remove("collapsed");
      document.getElementById("dock-caret").innerHTML = "&#9660;";
    }
    tr.scrollIntoView({ block:"nearest" });
  }
  updateGraph();
  renderDetail(id);
}

function renderDetail(id) {
  const n = byId.get(id);
  const el = document.getElementById("detail");
  if (!n) { el.className = "empty"; el.textContent = "Kein Knoten."; return; }
  el.className = "";
  const st = statementOf(n);
  const stLabel = { befund:"Befund", diagnose:"Diagnose", hypothese:"Hypothese" }[st];
  const inN = inAdj.get(id)||[], outN = outAdj.get(id)||[];
  const tagsHtml = n.tags.length ? n.tags.map(t => `<span class="tagchip">${escapeHtml(t)}</span>`).join("") : '<span style="color:#999">keine</span>';
  const nbrLinks = arr => arr.length
    ? arr.slice(0,12).map(x => `<span class="nbr" data-id="${escapeAttr(x)}">${escapeHtml(titleOf(x))}</span>`).join(", ") + (arr.length>12?` (+${arr.length-12})`:"")
    : '<span style="color:#999">keine</span>';
  el.innerHTML = `
    <span class="stype ${st}">${stLabel}</span>
    <div class="title">${escapeHtml(n.title)}${n.is_moc?'<span class="badge moc">MOC</span>':''}${n.is_bridge?'<span class="badge bridge">Bruecke</span>':''}${n.outlier?'<span class="badge outlier">Ausreisser</span>':''}</div>
    <div class="pathline">${escapeHtml(n.path)}</div>
    <dl>
      <dt>type / tags</dt><dd>${escapeHtml(n.type||"-")} ${tagsHtml}</dd>
      <dt>Ordner</dt><dd>${escapeHtml(n.folder)}</dd>
      <dt>Community <span style="color:var(--hypothese)">(Hypothese)</span></dt><dd>${n.community}</dd>
      <dt>Triangulation <span style="color:var(--diagnose)">(Diagnose)</span></dt><dd>Community-Ordner ${escapeHtml(n.comm_folder||"-")}, Reinheit ${n.comm_purity}${n.outlier?', dieser Knoten liegt im fremden Ordner':''}</dd>
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
  if (nbr) selectNode(nbr.dataset.id);
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
renderHead();
renderTable();
renderTriage();
setLens("struktur");
window.addEventListener("resize", () => {
  gWidth = svg.node().clientWidth; gHeight = svg.node().clientHeight;
  sim.force("center", d3.forceCenter(gWidth/2, gHeight/2)).alpha(0.2).restart();
});
</script>
</body>
</html>"""
