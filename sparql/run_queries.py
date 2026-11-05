import rdflib, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
g = rdflib.Graph(); g.parse(os.path.join(HERE, "..", "ontology", "flood_ontology.ttl"), format="turtle")
print(f"Loaded {len(g)} triples from flood_ontology.ttl\n")
def short(x): return str(x).split("#")[-1] if "#" in str(x) else str(x)
for q in sorted(glob.glob(os.path.join(HERE, "cq*.rq"))):
    text = open(q).read()
    print("=" * 78); print(os.path.basename(q)); print(text.splitlines()[0]); print("-" * 78)
    res = g.query(text); cols = [str(v) for v in res.vars]
    rows = [[short(c) for c in r] for r in res]
    widths = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows: print("  ".join(v.ljust(w) for v, w in zip(r, widths)))
    print(f"({len(rows)} rows)\n")
