"""Prints class hierarchy, properties (domain/range) and individual counts of the ontology."""
import os
from owlready2 import *
w = World()
o = w.get_ontology("file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "flood_ontology.owl"))).load()
def nm(x):
    if hasattr(x, "Classes"): return "(" + " or ".join(nm(c) for c in x.Classes) + ")"
    return getattr(x, "name", str(x))
def tree(c, depth=0):
    print("  " * depth + ("+- " if depth else "") + c.name + f"   [{len(list(c.instances()))} ind.]")
    for s in sorted(c.subclasses(), key=lambda x: x.name): tree(s, depth + 1)
print("CLASS HIERARCHY (asserted + defined)")
for c in sorted([c for c in o.classes() if Thing in c.is_a], key=lambda x: x.name): tree(c)
print("\nOBJECT PROPERTIES                    DOMAIN -> RANGE")
for p in sorted(o.object_properties(), key=lambda x: x.name):
    ch = [t.__name__.replace("Property", "") for t in p.is_a if t in (TransitiveProperty, FunctionalProperty)]
    print(f"  {p.name:14s} {nm(p.domain[0]) if p.domain else '-':32s} -> {nm(p.range[0]) if p.range else '-'}"
          + (f"  {ch}" if ch else "") + (f"  inverse={p.inverse_property.name}" if p.inverse_property else ""))
print("\nDATA PROPERTIES                      DOMAIN -> RANGE")
for p in sorted(o.data_properties(), key=lambda x: x.name):
    print(f"  {p.name:22s} {nm(p.domain[0]):14s} -> {p.range[0].__name__}")
print(f"\nTOTALS: {len(list(o.classes()))} classes, {len(list(o.object_properties()))} object properties, "
      f"{len(list(o.data_properties()))} data properties, {len(list(o.individuals()))} individuals")
