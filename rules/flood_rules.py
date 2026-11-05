"""Task 7/8: 12 production rules (IF-THEN) executed by a small forward-chaining engine.
Facts about wards, camps, pumps, hospitals come from ontology/flood_ontology.ttl (via rdflib);
live-scenario sensor values (rainfall, river level, water depth) are supplied in SCENARIO.
Conflict resolution: (1) highest priority (salience), (2) most specific rule (more conditions),
(3) most severe instance (higher alert level, then more at-risk residents / deeper water),
(4) declaration order. Each rule instance fires at most once (refraction)."""
import os, rdflib
from rdflib.namespace import RDF
F = rdflib.Namespace("http://example.org/flood#")
HERE = os.path.dirname(os.path.abspath(__file__))
g = rdflib.Graph(); g.parse(os.path.join(HERE, "..", "ontology", "flood_ontology.ttl"), format="turtle")
n = lambda x: str(x).split("#")[-1]
val = lambda s, p: next(iter(g.objects(s, p)), None)
LEVELS = ["GREEN", "YELLOW", "ORANGE", "RED"]

# ------------------------------------------------------------------ knowledge from ontology
wards = {}
for w in g.subjects(RDF.type, F.LowLyingWard): wards[n(w)] = dict(uri=w, low=True)
for w in g.subjects(RDF.type, F.HighGroundWard): wards[n(w)] = dict(uri=w, low=False)
for k, d in wards.items():
    d["atrisk"] = int(val(d["uri"], F.hasAtRiskPopulation))
    d["station"] = next((s for s in g.subjects(F.servesWard, d["uri"])), None)
    d["station_ok"] = bool(val(d["station"], F.isOperational)) if d["station"] is not None else None
    d["camps"] = [n(c) for c in g.objects(d["uri"], F.evacuatesTo)]
    d["river"] = next((n(r) for dr in g.subjects(F.locatedIn, d["uri"]) if (dr, RDF.type, F.StormwaterDrain) in g
                       for r in g.objects(dr, F.flowsInto)), None)
    d["hospitals"] = [n(h) for h in g.subjects(F.locatedIn, d["uri"]) if (h, RDF.type, F.Hospital) in g]
camp_cap = {n(c): int(val(c, F.hasCapacity)) for c in g.subjects(RDF.type, F.ReliefCamp)}
danger = {n(w): float(val(w, F.hasDangerLevelM)) for w in g.subjects(F.hasDangerLevelM, None)}
free_pumps = sorted(n(p) for p in g.subjects(RDF.type, F.PortablePump) if val(p, F.deployedIn) is None)
boats_in = {k: [n(b) for b in g.subjects(F.deployedIn, d["uri"]) if (b, RDF.type, F.RescueBoat) in g]
            for k, d in wards.items()}
roads = {n(r): n(val(r, F.locatedIn)) for r in g.subjects(RDF.type, F.Road)}
subways = {n(r): n(val(r, F.locatedIn)) for r in g.subjects(RDF.type, F.Subway)}

# ------------------------------------------------------------------ scenario (live sensor data)
SCENARIO = dict(
    rain24h={"Velachery": 132.4, "Pallikaranai": 218.0, "Saidapet": 90.0, "Perungudi": 125.0,
             "Sholinganallur": 118.0, "AnnaNagar": 70.0, "Kilpauk": 60.0, "Mylapore": 66.0},
    river_level={"AdyarRiver": 5.4, "CooumRiver": 2.4, "BuckinghamCanal": 3.9},
    depth_m={"RD_VelacheryMainRd": 0.45, "RD_OMR": 0.10, "RD_GST": 0.35, "SW_SaidapetSubway": 0.60,
             "SW_KilpaukUnderpass": 0.05},
    camp_occupancy={"RC_VelacheryHS": 300, "RC_PallikaranaiSchool": 0, "RC_SaidapetCommunity": 0,
                    "RC_AnnaNagarHall": 0})
wm = dict(alert={k: 0 for k in wards}, evac={}, unplaced={}, pumps=list(free_pumps),
          occ=dict(SCENARIO["camp_occupancy"]), closed=set())

# ------------------------------------------------------------------ the 12 rules
class Rule:
    def __init__(s, rid, name, prio, nconds, kind, cond, act, text):
        s.rid, s.name, s.prio, s.nconds, s.kind, s.cond, s.act, s.text = rid, name, prio, nconds, kind, cond, act, text
rain = lambda w: SCENARIO["rain24h"][w]
def river_high(w):
    r = wards[w]["river"]; return r in SCENARIO["river_level"] and SCENARIO["river_level"][r] >= danger[r]
def once(key): wm["closed"].add(key)
def done(key): return key in wm["closed"]

def set_alert(lvl):
    def f(w): wm["alert"][w] = lvl; return f"alert[{w}] = {LEVELS[lvl]}"
    return f
def a_escalate(w):
    once(("esc", w)); wm["alert"][w] += 1
    return f"receiving water body above danger level -> escalate {w} to {LEVELS[wm['alert'][w]]}"
def a_evac(level):
    def f(w):
        wm["evac"][w] = level; left = wards[w]["atrisk"]; placed = []
        for c in wards[w]["camps"]:                       # fill designated camps in order
            k = min(left, camp_cap[c] - wm["occ"][c]); wm["occ"][c] += k; left -= k
            placed.append(f"{k}->{c}")
        wm["unplaced"][w] = left
        return f"{level} evacuation of {wards[w]['atrisk']} residents of {w}: placed {', '.join(placed)}; unplaced {left}"
    return f
def a_overflow(w):
    once(("ovf", w)); left = wm["unplaced"][w]
    return f"{left} residents of {w} have no camp space: open overflow shelter in a high-ground ward, alert camp officers"
def a_deploy(w):
    once(("pump", w)); p = wm["pumps"].pop(0)
    return f"deploy portable pump {p} to {w} (station {n(wards[w]['station'])} is DOWN)"
def a_standby(w):
    once(("pump", w)); p = wm["pumps"].pop(0)
    return f"pre-position portable pump {p} on standby in {w}"
def a_road(r):
    once(r); return f"close {r} in {roads[r]} (depth {SCENARIO['depth_m'][r]} m) and divert traffic"
def a_subway(s):
    once(s); return f"close {s} in {subways[s]} (depth {SCENARIO['depth_m'][s]} m) and dispatch dewatering pump"
def a_hosp(w):
    once(("hosp", w))
    return f"hospital(s) {wards[w]['hospitals']} on emergency footing; boats on station: {boats_in[w] or 'NONE - request one'}"

RULES = [
 Rule("R01", "Red alert", 90, 2, "ward", lambda w: rain(w) >= 204.5 and wm["alert"][w] < 3, set_alert(3),
      "IF rainfall_24h >= 204.5 mm AND alert < RED THEN alert := RED"),
 Rule("R02", "Orange alert", 80, 2, "ward", lambda w: rain(w) >= 115.6 and wm["alert"][w] < 2, set_alert(2),
      "IF rainfall_24h >= 115.6 mm AND alert < ORANGE THEN alert := ORANGE"),
 Rule("R03", "Yellow alert", 70, 2, "ward", lambda w: rain(w) >= 64.5 and wm["alert"][w] < 1, set_alert(1),
      "IF rainfall_24h >= 64.5 mm AND alert < YELLOW THEN alert := YELLOW"),
 Rule("R04", "River-level escalation", 85, 3, "ward",
      lambda w: wm["alert"][w] in (1, 2) and river_high(w) and not done(("esc", w)), a_escalate,
      "IF alert is YELLOW or ORANGE AND receiving river level >= danger level THEN raise alert by one level (once)"),
 Rule("R05", "Mandatory evacuation", 100, 4, "ward",
      lambda w: wm["alert"][w] == 3 and wards[w]["low"] and wards[w]["atrisk"] > 0 and w not in wm["evac"],
      a_evac("MANDATORY"),
      "IF alert = RED AND ward is low-lying AND at-risk residents > 0 AND no evacuation ordered THEN order MANDATORY evacuation to designated camps"),
 Rule("R06", "Advisory evacuation", 60, 4, "ward",
      lambda w: wm["alert"][w] == 2 and wards[w]["low"] and wards[w]["atrisk"] > 0 and w not in wm["evac"],
      a_evac("ADVISORY"),
      "IF alert = ORANGE AND ward is low-lying AND at-risk residents > 0 AND no evacuation ordered THEN issue ADVISORY evacuation"),
 Rule("R07", "Camp overflow", 88, 2, "ward", lambda w: wm["unplaced"].get(w, 0) > 0 and not done(("ovf", w)), a_overflow,
      "IF evacuation ordered AND residents left unplaced (designated camps full) THEN open overflow shelter"),
 Rule("R08", "Deploy portable pump", 95, 4, "ward",
      lambda w: wm["alert"][w] >= 2 and wards[w]["low"] and wards[w]["station_ok"] is False and wm["pumps"] and not done(("pump", w)),
      a_deploy, "IF alert >= ORANGE AND ward low-lying AND its pump station NOT operational AND a portable pump is free THEN deploy portable pump"),
 Rule("R09", "Standby pump", 50, 4, "ward",
      lambda w: wm["alert"][w] >= 1 and wards[w]["low"] and wards[w]["station_ok"] is True and wm["pumps"] and not done(("pump", w)),
      a_standby, "IF alert >= YELLOW AND ward low-lying AND station operational AND a portable pump is free THEN pre-position pump on standby"),
 Rule("R10", "Road closure", 75, 1, "road", lambda r: SCENARIO["depth_m"][r] >= 0.30 and not done(r), a_road,
      "IF water depth on road >= 0.30 m THEN close road and divert traffic"),
 Rule("R11", "Subway closure", 78, 1, "subway", lambda s: SCENARIO["depth_m"][s] >= 0.15 and not done(s), a_subway,
      "IF water depth in subway >= 0.15 m THEN close subway and dispatch dewatering pump"),
 Rule("R12", "Hospital protection", 92, 3, "ward",
      lambda w: wm["alert"][w] == 3 and wards[w]["hospitals"] and not done(("hosp", w)), a_hosp,
      "IF alert = RED AND ward contains a hospital THEN put hospital on emergency footing, confirm rescue boat, notify officer"),
]
KIND = {"ward": list(wards), "road": list(roads), "subway": list(subways)}
def severity(kind, e):
    if kind == "ward": return wm["alert"][e] * 10**7 + wards[e]["atrisk"]
    return SCENARIO["depth_m"][e]

def run():
    fired, cycle = set(), 0
    print(f"Working memory: {len(wards)} wards, {len(roads)} roads, {len(subways)} subways; free portable pumps {free_pumps}\n")
    while True:
        cs = [(r, e) for r in RULES for e in KIND[r.kind] if (r.rid, e) not in fired and r.cond(e)]
        if not cs: break
        key = lambda x: (x[0].prio, x[0].nconds, severity(x[0].kind, x[1]), -RULES.index(x[0]))
        cs.sort(key=key, reverse=True); r, e = cs[0]
        cycle += 1; fired.add((r.rid, e))
        nxt = f"{cs[1][0].rid}:{cs[1][1]}" if len(cs) > 1 else "-"
        print(f"[{cycle:02d}] FIRE {r.rid} {r.name} (P{r.prio}) on {e}\n     -> {r.act(e)}\n     conflict set={len(cs)}, runner-up={nxt}")
    print("\n" + "=" * 72 + "\nFINAL STATE")
    for w in sorted(wards, key=lambda w: -wm["alert"][w]):
        print(f"  {w:15s} alert={LEVELS[wm['alert'][w]]:7s} evacuation={wm['evac'].get(w, '-'):10s} unplaced={wm['unplaced'].get(w, '-')}")
    print("  free portable pumps left :", wm["pumps"] or "none")
    print("  camp occupancy / capacity:", {k: f"{wm['occ'][k]}/{camp_cap[k]}" for k in camp_cap})
    print(f"  total rule firings       : {cycle}")
if __name__ == "__main__":
    run()
