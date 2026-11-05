# DSA1604 - KEDS Assignment 1 (CO1): Flood-Response Knowledge Base

Ontology + semantic network + production rules + reasoner tests for urban flood response in a coastal city.
All data values are illustrative samples, not official municipal data.

| Path | Content |
|---|---|
| `report/Assignment1_KEDS_Report.docx` | Report with answers to all 12 tasks and embedded screenshots |
| `ontology/flood_ontology.owl`, `.ttl` | The ontology (25 classes + 3 defined, 13 object props, 11 data props, 49 individuals) |
| `build_ontology.py` | Builds the ontology (`--fault N` builds seeded-fault test files for Task 10) |
| `sparql/` | Competency-question queries `cq1-3.rq` and `run_queries.py` |
| `rules/` | 12 rules (`flood_rules.txt`) and the executable rule engine (`flood_rules.py`) |
| `reasoner/` | HermiT tests (`run_reasoner.py`) and DL-rule verification (`verify_dl_rules.py`) |
| `screenshots/` | Figures and console-output screenshots |

## Run
```
pip install rdflib owlready2 graphviz pillow     # plus Java (for HermiT) and Graphviz
python build_ontology.py
python sparql/run_queries.py
python rules/flood_rules.py
python reasoner/run_reasoner.py all
python reasoner/verify_dl_rules.py
python diagrams/make_diagrams.py && python diagrams/make_screenshots.py
```
