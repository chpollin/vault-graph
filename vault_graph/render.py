"""Render-MVP: eine HTML-Visualisierung des Linkgraphen.

Eine Force-Directed-Visualisierung mit D3.js (vom CDN, keine npm-Dependency).
Knoten gefaerbt nach Louvain-Community, Groesse nach PageRank, Bruecken-
knoten markiert. Tooltips zeigen Titel, Community, Centrality-Werte.

Bewusst minimal: ein selfcontained HTML-File, keine externen Assets,
oeffnen im Browser, fertig.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import networkx as nx


def render_topology_html(
    graph: nx.DiGraph,
    topology: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _build_payload(graph, topology)
    html_doc = _wrap_html(payload, topology)
    output_path.write_text(html_doc, encoding="utf-8")


def _build_payload(graph: nx.DiGraph, topology: dict[str, Any]) -> dict:
    centralities = topology["centralities"]
    communities = topology["communities"]
    bridges = set(topology["bridges"])
    k_core = topology["k_core"]

    nodes = []
    for key, attrs in graph.nodes(data=True):
        c = centralities.get(key, {})
        nodes.append({
            "id": key,
            "title": attrs.get("title", key),
            "path": attrs.get("path", ""),
            "is_moc": bool(attrs.get("is_moc")),
            "anon": bool(attrs.get("privacy_anonymized")),
            "community": communities.get(key, -1),
            "pagerank": c.get("pagerank", 0.0),
            "degree": int(c.get("degree", 0)),
            "in_degree": int(c.get("in_degree", 0)),
            "out_degree": int(c.get("out_degree", 0)),
            "betweenness": c.get("betweenness", 0.0),
            "k_core": k_core.get(key, 0),
            "is_bridge": key in bridges,
        })

    edges = [{"source": u, "target": v} for u, v in graph.edges]
    return {"nodes": nodes, "edges": edges}


def _wrap_html(payload: dict, topology: dict[str, Any]) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False)
    stats = topology["stats"]
    modularity = topology["modularity"]
    return _TEMPLATE.replace("__PAYLOAD__", payload_json) \
        .replace("__N_NODES__", str(stats["n_nodes"])) \
        .replace("__N_EDGES__", str(stats["n_edges"])) \
        .replace("__N_COMMUNITIES__", str(stats["n_communities"])) \
        .replace("__MODULARITY__", f"{modularity:.3f}") \
        .replace("__N_BRIDGES__", str(stats["n_bridges"]))


_TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>vault-graph: Topology</title>
<style>
  html, body {
    margin: 0; padding: 0; height: 100%;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #fafafa; color: #222;
  }
  #app { display: flex; height: 100vh; }
  #graph { flex: 1; position: relative; background: white; }
  #sidebar {
    width: 320px; padding: 16px; overflow-y: auto;
    border-left: 1px solid #ddd; background: #f5f5f5;
  }
  h1 { font-size: 16px; margin: 0 0 8px 0; }
  h2 { font-size: 13px; margin: 16px 0 4px 0; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }
  .stat { font-size: 13px; margin: 2px 0; }
  .stat b { font-variant-numeric: tabular-nums; }
  .detail { font-size: 12px; line-height: 1.5; }
  .detail dt { font-weight: 600; color: #555; margin-top: 6px; }
  .detail dd { margin: 0 0 2px 0; }
  .empty { color: #888; font-style: italic; }
  .legend { font-size: 12px; }
  .legend span { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
  svg { width: 100%; height: 100%; cursor: grab; }
  svg:active { cursor: grabbing; }
  .node { stroke: white; stroke-width: 0.5px; cursor: pointer; }
  .node.bridge { stroke: #111; stroke-width: 2px; }
  .node.anon { stroke: #c00; stroke-width: 1.5px; stroke-dasharray: 2,2; }
  .link { stroke: #ccc; stroke-opacity: 0.4; }
  .node:hover { stroke: #000; stroke-width: 2px; }
  .controls { padding: 8px; border-bottom: 1px solid #ddd; background: white; font-size: 12px; display: flex; gap: 12px; align-items: center; }
  .controls input[type=search] { flex: 1; padding: 4px 8px; border: 1px solid #ccc; border-radius: 3px; font-size: 13px; }
  .controls label { white-space: nowrap; }
  .label { font-size: 10px; fill: #333; pointer-events: none; user-select: none; }
</style>
</head>
<body>
<div id="app">
  <div style="flex: 1; display: flex; flex-direction: column;">
    <div class="controls">
      <input type="search" id="search" placeholder="Knoten suchen ...">
      <label><input type="checkbox" id="show-labels"> Labels (Top-Knoten)</label>
      <label><input type="checkbox" id="bridges-only"> nur Bruecken</label>
    </div>
    <div id="graph"><svg></svg></div>
  </div>
  <aside id="sidebar">
    <h1>vault-graph</h1>
    <p class="stat">Topologische Sicht auf den Linkgraph. Klick auf einen Knoten fuer Details.</p>

    <h2>Globalmasse</h2>
    <div class="stat"><b>__N_NODES__</b> Knoten</div>
    <div class="stat"><b>__N_EDGES__</b> Kanten (gerichtet)</div>
    <div class="stat"><b>__N_COMMUNITIES__</b> Louvain-Communities</div>
    <div class="stat">Modularity <b>__MODULARITY__</b></div>
    <div class="stat"><b>__N_BRIDGES__</b> Brueckenknoten</div>

    <h2>Legende</h2>
    <div class="legend">
      <div>Groesse: PageRank</div>
      <div>Farbe: Louvain-Community</div>
      <div>Schwarzer Rand: Brueckenknoten</div>
      <div>Rot gestrichelt: anonymisiert (Privacy)</div>
    </div>

    <h2>Auswahl</h2>
    <div id="detail" class="detail empty">Kein Knoten ausgewaehlt.</div>
  </aside>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const PAYLOAD = __PAYLOAD__;

const svg = d3.select("svg");
const width = svg.node().clientWidth;
const height = svg.node().clientHeight;

// Color scale per community
const communities = [...new Set(PAYLOAD.nodes.map(n => n.community))].sort((a,b)=>a-b);
const color = d3.scaleOrdinal()
  .domain(communities)
  .range(d3.schemeTableau10.concat(d3.schemeSet3));

// Node radius from PageRank (sqrt scale for area perception)
const prMax = d3.max(PAYLOAD.nodes, n => n.pagerank) || 1;
const radius = d3.scaleSqrt().domain([0, prMax]).range([2.5, 18]);

const link = svg.append("g").attr("class","links").selectAll("line")
  .data(PAYLOAD.edges).join("line")
    .attr("class","link")
    .attr("stroke-width", 0.7);

const nodeG = svg.append("g").attr("class","nodes");
const node = nodeG.selectAll("circle")
  .data(PAYLOAD.nodes).join("circle")
    .attr("class", d => "node" + (d.is_bridge ? " bridge":"") + (d.anon ? " anon":""))
    .attr("r", d => radius(d.pagerank))
    .attr("fill", d => color(d.community))
    .on("click", (_, d) => showDetail(d))
    .call(drag());

node.append("title").text(d => `${d.title} (Community ${d.community})`);

const labelG = svg.append("g").attr("class","labels");

const sim = d3.forceSimulation(PAYLOAD.nodes)
  .force("link", d3.forceLink(PAYLOAD.edges).id(d => d.id).distance(45).strength(0.6))
  .force("charge", d3.forceManyBody().strength(-90))
  .force("center", d3.forceCenter(width/2, height/2))
  .force("collide", d3.forceCollide().radius(d => radius(d.pagerank)+1))
  .on("tick", ticked);

function ticked() {
  link
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("cx", d => d.x).attr("cy", d => d.y);
  labelG.selectAll("text").attr("x", d => d.x).attr("y", d => d.y);
}

function drag() {
  return d3.drag()
    .on("start", (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on("drag", (e, d) => { d.fx = e.x; d.fy = e.y; })
    .on("end", (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; });
}

// Zoom
svg.call(d3.zoom().scaleExtent([0.15, 6]).on("zoom", ev => {
  svg.selectAll("g.nodes, g.links, g.labels").attr("transform", ev.transform);
}));

// Search
d3.select("#search").on("input", function() {
  const q = this.value.toLowerCase().trim();
  node.style("opacity", d => !q || d.title.toLowerCase().includes(q) ? 1 : 0.1);
  link.style("opacity", d => !q ? 0.4 : 0.05);
});

// Toggle labels for top nodes
d3.select("#show-labels").on("change", function() {
  if (this.checked) {
    const top = [...PAYLOAD.nodes].sort((a,b) => b.pagerank - a.pagerank).slice(0, 30);
    labelG.selectAll("text").data(top, d => d.id).join("text")
      .attr("class","label").text(d => d.title)
      .attr("text-anchor","middle").attr("dy", -10);
  } else {
    labelG.selectAll("text").remove();
  }
});

// Bridges-only filter
d3.select("#bridges-only").on("change", function() {
  const only = this.checked;
  node.style("display", d => !only || d.is_bridge ? null : "none");
  link.style("display", d => !only || (d.source.is_bridge || d.target.is_bridge) ? null : "none");
});

function showDetail(d) {
  const inn = PAYLOAD.edges.filter(e => (e.target.id||e.target) === d.id).length;
  const out = PAYLOAD.edges.filter(e => (e.source.id||e.source) === d.id).length;
  const el = document.getElementById("detail");
  el.classList.remove("empty");
  el.innerHTML = `
    <dl>
      <dt>Titel</dt><dd>${escape(d.title)}</dd>
      <dt>Pfad</dt><dd>${escape(d.path)}</dd>
      <dt>Community</dt><dd>${d.community}</dd>
      <dt>PageRank</dt><dd>${d.pagerank.toFixed(4)}</dd>
      <dt>Degree</dt><dd>${d.degree} (in ${d.in_degree}, out ${d.out_degree})</dd>
      <dt>Betweenness</dt><dd>${d.betweenness.toFixed(4)}</dd>
      <dt>K-Core</dt><dd>${d.k_core}</dd>
      <dt>MOC-Heuristik</dt><dd>${d.is_moc ? "ja" : "nein"}</dd>
      <dt>Brueckenknoten</dt><dd>${d.is_bridge ? "ja" : "nein"}</dd>
      <dt>Anonymisiert</dt><dd>${d.anon ? "ja (Privacy)" : "nein"}</dd>
    </dl>
  `;
}

function escape(s) { return (s||"").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch])); }
</script>
</body>
</html>"""
