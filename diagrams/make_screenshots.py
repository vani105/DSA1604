"""Runs each project script and renders its REAL console output as a terminal-style PNG."""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "screenshots")
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 15)

def sh(cmd):
    r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    return "\n".join(l for l in r.stdout.splitlines() if not l.startswith("* Owlready"))

def render(title, prompt, text, fname):
    import textwrap
    lines = [f"$ {prompt}"]
    for l in text.splitlines():
        lines += textwrap.wrap(l, 118, subsequent_indent="    ", replace_whitespace=False, drop_whitespace=False) or [""]
    cw = FONT.getlength("M"); lh = 21; pad = 18; top = 38
    W = int(max(len(l) for l in lines) * cw + 2 * pad); W = max(W, 760); H = top + len(lines) * lh + pad
    im = Image.new("RGB", (W, H), "#1e1e2e"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 30], fill="#313244")
    for i, c in enumerate(["#f38ba8", "#f9e2af", "#a6e3a1"]): d.ellipse([12 + i * 20, 9, 24 + i * 20, 21], fill=c)
    d.text((W // 2 - len(title) * cw / 2, 7), title, font=FONT, fill="#cdd6f4")
    for i, l in enumerate(lines):
        col = "#cdd6f4"
        if i == 0: col = "#89b4fa"
        elif "INCONSISTENT" in l or "SHORTFALL" in l or "'AmphibiousRoad'" in l: col = "#f38ba8"
        elif "is consistent" in l or "none" == l.strip()[-4:] or "ENOUGH" in l: col = "#a6e3a1"
        elif l.startswith(("RUN:", "FIRE", "[")) or " FIRE " in l or l.startswith("=") and False: col = "#f9e2af"
        d.text((pad, top + i * lh), l, font=BOLD if i == 0 else FONT, fill=col)
    im.save(os.path.join(OUT, fname)); print("saved", fname, im.size)

def chunks(text, n):
    ls = text.splitlines(); return ["\n".join(ls[i:i + n]) for i in range(0, len(ls), n)]

# --- reasoner
txt = sh("python reasoner/run_reasoner.py all")
blocks = txt.split("=" * 74)
faults = "=" * 74 + ("=" * 74).join(blocks[1:4]); fixed = "=" * 74 + blocks[4]
render("HermiT reasoner - seeded faults", "python reasoner/run_reasoner.py 1 2 3", faults.strip("\n"), "ss_reasoner_faults.png")
render("HermiT reasoner - fixed ontology", "python reasoner/run_reasoner.py 4", fixed.strip("\n"), "ss_reasoner_fixed.png")
# --- ontology
render("Ontology summary", "python ontology/inspect_ontology.py", sh("python ontology/inspect_ontology.py"), "ss_ontology_summary.png")
# --- sparql (one image per query)
q = sh("python sparql/run_queries.py").split("=" * 78)
for i in (1, 2, 3):
    qtext = open(os.path.join(ROOT, "sparql", f"cq{i}.rq")).read().rstrip()
    render(f"SPARQL - competency question {i}", f"cat sparql/cq{i}.rq && python sparql/run_queries.py",
           qtext + "\n\n" + "\n".join(q[i].splitlines()[3:]).strip(), f"ss_sparql_cq{i}.png")
# --- rules
rt = sh("python rules/flood_rules.py"); parts = rt.split("=" * 72)
trace = parts[0]
for i, c in enumerate(chunks(trace, 38), 1):
    render(f"Rule engine trace ({i}/{len(chunks(trace, 38))})", "python rules/flood_rules.py", c, f"ss_rules_trace{i}.png")
render("Rule engine - final state", "python rules/flood_rules.py  (end of output)", ("=" * 72 + parts[1]).strip("\n"), "ss_rules_final.png")
# --- inheritance check
code = '''
import rdflib
F="http://example.org/flood#"; g=rdflib.Graph(); g.parse("ontology/flood_ontology.ttl")
print("PP_01 type       :", [str(o).split("#")[-1] for o in g.objects(rdflib.URIRef(F+"PP_01"), rdflib.RDF.type)])
for q,l in [("rdfs:subClassOf* path from PortablePump", "ASK/SELECT ?c WHERE { flood:PortablePump rdfs:subClassOf* ?c }"),
            ("rdfs:subClassOf* path from LowLyingWard", "SELECT ?c WHERE { flood:LowLyingWard rdfs:subClassOf* ?c }")]:
    r=g.query("PREFIX flood:<"+F+"> PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> "+l.replace("ASK/",""))
    print(f"{q:42s}:", [str(x[0]).split('#')[-1] for x in r if str(x[0]).startswith(F)])
print("domain of hasPumpingCapacityLps :", [str(o).split("#")[-1] for o in g.objects(rdflib.URIRef(F+"hasPumpingCapacityLps"), rdflib.RDFS.domain)])
print("PP_01 hasPumpingCapacityLps     :", [str(o) for o in g.objects(rdflib.URIRef(F+"PP_01"), rdflib.URIRef(F+"hasPumpingCapacityLps"))], " (slot defined on Pump, used by PortablePump)")
print("domain of hasPopulation         :", [str(o).split("#")[-1] for o in g.objects(rdflib.URIRef(F+"hasPopulation"), rdflib.RDFS.domain)])
print("Velachery hasPopulation         :", [str(o) for o in g.objects(rdflib.URIRef(F+"Velachery"), rdflib.URIRef(F+"hasPopulation"))], " (slot defined on Ward, used by LowLyingWard individual)")
'''
open(os.path.join(ROOT, "ontology", "inheritance_check.py"), "w").write(code.strip() + "\n")
render("Inheritance check (rdflib)", "python ontology/inheritance_check.py", sh("python ontology/inheritance_check.py"), "ss_inheritance_check.png")
render("Task 9 - DL rules classified by HermiT", "python reasoner/verify_dl_rules.py", sh("python reasoner/verify_dl_rules.py"), "ss_dl_rules.png")
