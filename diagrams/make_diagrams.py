import graphviz, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")

# ---------- Task 4 : semantic network ----------
d = graphviz.Digraph("semnet", format="png")
d.attr(rankdir="BT", dpi="130", fontname="Helvetica", nodesep="0.35", ranksep="0.6", labelloc="t",
       label="Semantic network - flood response (is-a / part-of / causes)", fontsize="18")
d.attr("node", shape="box", style="rounded,filled", fontname="Helvetica", fontsize="11")
cls = {"Resource": "#E3F2FD", "Pump": "#E3F2FD", "PortablePump": "#E3F2FD", "RescueBoat": "#E3F2FD",
       "Infrastructure": "#E8F5E9", "PumpStation": "#E8F5E9", "StormwaterDrain": "#E8F5E9", "Road": "#E8F5E9",
       "GeographicArea": "#FFF8E1", "Ward": "#FFF8E1", "LowLyingWard": "#FFF8E1", "WaterBody": "#FFF8E1", "River": "#FFF8E1",
       "Facility": "#F3E5F5", "ReliefCamp": "#F3E5F5", "Hospital": "#F3E5F5"}
for n, c in cls.items(): d.node(n, fillcolor=c)
for n in ["HeavyRainfall", "FloodEvent", "WaterLogging", "RiverOverflow", "DrainBlockage", "TrafficDisruption", "EvacuationOrder"]:
    d.node(n, fillcolor="#FFEBEE", shape="ellipse")
for n in ["DrainageNetwork", "City"]: d.node(n, fillcolor="#ECEFF1")
for n in ["Velachery", "PP_01"]: d.node(n, fillcolor="#FFFFFF", shape="box", style="filled,bold")
isa = [("Pump", "Resource"), ("PortablePump", "Pump"), ("RescueBoat", "Resource"), ("PumpStation", "Infrastructure"),
       ("StormwaterDrain", "Infrastructure"), ("Road", "Infrastructure"), ("Ward", "GeographicArea"),
       ("LowLyingWard", "Ward"), ("WaterBody", "GeographicArea"), ("River", "WaterBody"), ("ReliefCamp", "Facility"),
       ("Hospital", "Facility"), ("Velachery", "LowLyingWard"), ("PP_01", "PortablePump")]
for a, b in isa: d.edge(a, b, label="is-a", color="#37474F", fontsize="9", arrowhead="empty")
for a, b in [("Pump", "PumpStation"), ("PumpStation", "DrainageNetwork"), ("StormwaterDrain", "DrainageNetwork"),
             ("Ward", "City"), ("DrainageNetwork", "City")]:
    d.edge(a, b, label="part-of", color="#1565C0", fontcolor="#1565C0", style="dashed", fontsize="9", arrowhead="odiamond")
for a, b in [("HeavyRainfall", "FloodEvent"), ("HeavyRainfall", "RiverOverflow"), ("RiverOverflow", "FloodEvent"),
             ("FloodEvent", "WaterLogging"), ("DrainBlockage", "WaterLogging"), ("WaterLogging", "TrafficDisruption"),
             ("FloodEvent", "EvacuationOrder")]:
    d.edge(a, b, label="causes", color="#C62828", fontcolor="#C62828", penwidth="1.8", fontsize="9")
d.render(os.path.join(OUT, "fig_semantic_network"), cleanup=True)

# ---------- Task 5 : inheritance examples ----------
h = graphviz.Digraph("inh", format="png")
h.attr(rankdir="BT", dpi="130", fontname="Helvetica", labelloc="t", fontsize="16",
       label="Inheritance (is-a) and property inheritance", nodesep="0.5")
h.attr("node", shape="record", style="filled", fontname="Helvetica", fontsize="11")
h.node("Resource", "{Resource|may be deployedIn a Ward}", fillcolor="#E3F2FD")
h.node("Pump", "{Pump|slot: hasPumpingCapacityLps (int)\\lslot: partOf (PumpStation)\\l}", fillcolor="#E3F2FD")
h.node("PortablePump", "{PortablePump|(adds no new slots - inherits all)\\l}", fillcolor="#E3F2FD")
h.node("PP_01", "{PP_01 (individual)|hasPumpingCapacityLps = 500  (inherited slot, local value)\\l}", fillcolor="#FFFFFF")
h.node("GeographicArea", "{GeographicArea|}", fillcolor="#FFF8E1")
h.node("Ward", "{Ward|slot: hasPopulation (int)\\lslot: hasElevationM (float)\\lslot: hasAlertLevel\\l}", fillcolor="#FFF8E1")
h.node("LowLyingWard", "{LowLyingWard|(inherits all Ward slots)\\l}", fillcolor="#FFF8E1")
h.node("Velachery", "{Velachery (individual)|hasPopulation = 142000\\lhasElevationM = 2.5\\lhasAlertLevel = AL_Orange\\l}", fillcolor="#FFFFFF")
for a, b in [("Pump", "Resource"), ("PortablePump", "Pump"), ("PP_01", "PortablePump"), ("Ward", "GeographicArea"),
             ("LowLyingWard", "Ward"), ("Velachery", "LowLyingWard")]:
    h.edge(a, b, label="is-a", arrowhead="empty")
h.render(os.path.join(OUT, "fig_inheritance"), cleanup=True)
print("diagrams done")
