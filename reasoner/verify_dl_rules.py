"""Task 9: three production rules re-expressed as OWL/DL defined classes and classified by HermiT.
(DL covers the CONDITION part of a rule; the action part stays in the rule engine.)"""
import os
from owlready2 import *
w = World()
o = w.get_ontology("file://" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ontology", "flood_ontology.owl"))).load()
with o:
    AL_Red, AL_Orange = o.AL_Red, o.AL_Orange
    # R05: MandatoryEvacuationWard == LowLyingWard AND hasAlertLevel value AL_Red AND hasAtRiskPopulation some int[>=1]
    class MandatoryEvacuationWard(o.Ward):
        equivalent_to = [o.LowLyingWard & o.hasAlertLevel.value(AL_Red) &
                         o.hasAtRiskPopulation.some(ConstrainedDatatype(int, min_inclusive=1))]
    # R08: PortablePumpNeededWard == LowLyingWard AND hasAlertLevel some {AL_Orange, AL_Red}
    #                                AND isServedBy some (PumpStation AND isOperational value false)
    class PortablePumpNeededWard(o.Ward):
        equivalent_to = [o.LowLyingWard & o.hasAlertLevel.some(OneOf([AL_Orange, AL_Red])) &
                         o.isServedBy.some(o.PumpStation & o.isOperational.value(False))]
    # R12: EmergencyHospital == Hospital AND locatedIn some (Ward AND hasAlertLevel value AL_Red)
    class EmergencyHospital(o.Hospital):
        equivalent_to = [o.Hospital & o.locatedIn.some(o.Ward & o.hasAlertLevel.value(AL_Red))]
    sync_reasoner_hermit(w, infer_property_values=True, debug=0)
print("Classification by HermiT on the current alert snapshot stored in the ontology:")
for c in (MandatoryEvacuationWard, PortablePumpNeededWard, EmergencyHospital):
    print(f"  {c.name:26s}", sorted(i.name for i in c.instances()) or "(no members)")
print("Snapshot alert levels:", {x.name: x.hasAlertLevel.name for x in sorted(o.Ward.instances(), key=lambda x: x.name)})
print("Inconsistent classes :", [c.name for c in w.inconsistent_classes()] or "none")
