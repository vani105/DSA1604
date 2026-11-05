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
