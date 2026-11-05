"""Task 10: run the HermiT reasoner (via owlready2) on seeded-fault ontologies, then on the fixed one."""
import os, sys
from owlready2 import *
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ontology")

def run(label, fname):
    print("=" * 74); print(f"RUN: {label}\nFILE: {fname}"); print("-" * 74)
    w = World()
    onto = w.get_ontology("file://" + os.path.abspath(os.path.join(ROOT, fname))).load()
    try:
        with onto:
            sync_reasoner_hermit(w, infer_property_values=True, debug=0)
    except OwlReadyInconsistentOntologyError:
        print("HermiT result : ONTOLOGY IS INCONSISTENT"); return w, onto, False
    bad = list(w.inconsistent_classes())
    print("HermiT result : ontology is consistent")
    print("Unsatisfiable classes (equivalent to owl:Nothing):",
          [c.name for c in bad if c is not Nothing] or "none")
    return w, onto, True

def report_inferences(w, onto):
    print("\nInferred classification (defined classes -> members):")
    for cname in ["ServedWard", "UnprotectedWard", "OperationalPumpStation"]:
        c = onto[cname]
        print(f"  {cname:24s}", sorted(i.name for i in c.instances()))
    print("\nInferred inverse property isServedBy:")
    for ward in sorted(onto.Ward.instances(), key=lambda x: x.name):
        print(f"  {ward.name:15s} isServedBy ->", [p.name for p in ward.isServedBy])
    print("\nInferred transitive flowsInto (drain -> ... -> water body):")
    for d in sorted(onto.StormwaterDrain.instances(), key=lambda x: x.name):
        print(f"  {d.name:17s} flowsInto ->", sorted(x.name for x in d.flowsInto))

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("1", "all"):
        run("Test 1 - seeded unsatisfiable class (AmphibiousRoad = Road AND WaterBody)", "test_fault1.owl")
    if which in ("2", "all"):
        run("Test 2 - seeded individual typed LowLyingWard AND HighGroundWard", "test_fault2.owl")
    if which in ("3", "all"):
        run("Test 3 - seeded functional-property clash (two alert levels for one ward)", "test_fault3.owl")
    if which in ("4", "all"):
        w, onto, ok = run("Test 4 - FIXED ontology (final deliverable)", "flood_ontology.owl")
        if ok: report_inferences(w, onto)
