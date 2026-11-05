"""Build the Flood-Response ontology (OWL 2) with owlready2.
Usage: python build_ontology.py            -> ontology/flood_ontology.owl/.ttl (clean, consistent)
       python build_ontology.py --fault N  -> ontology/test_faultN.owl (seeded errors for Task 10)
"""
import sys, os
from owlready2 import *
import rdflib

BASE = "http://example.org/flood#"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontology")

def build(faults=()):
    onto = get_ontology(BASE)
    with onto:
        # ---------- TASK 1 : 25 concepts in a class hierarchy ----------
        class GeographicArea(Thing): pass                      # 1
        class Ward(GeographicArea): pass                       # 2
        class LowLyingWard(Ward): pass                         # 3
        class HighGroundWard(Ward): pass                       # 4
        class WaterBody(GeographicArea): pass                  # 5
        class River(WaterBody): pass                           # 6
        class Canal(WaterBody): pass                           # 7
        class Reservoir(WaterBody): pass                       # 8
        class Infrastructure(Thing): pass                      # 9
        class PumpStation(Infrastructure): pass                # 10
        class StormwaterDrain(Infrastructure): pass            # 11
        class Road(Infrastructure): pass                       # 12
        class Subway(Infrastructure): pass                     # 13
        class Facility(Thing): pass                            # 14
        class ReliefCamp(Facility): pass                       # 15
        class Hospital(Facility): pass                         # 16
        class Resource(Thing): pass                            # 17
        class Pump(Resource): pass                             # 18
        class PortablePump(Pump): pass                         # 19
        class RescueBoat(Resource): pass                       # 20
        class Officer(Thing): pass                             # 21
        class RainfallAlertLevel(Thing): pass                  # 22
        class FloodEvent(Thing): pass                          # 23
        class EvacuationOrder(Thing): pass                     # 24
        class HeavyRainfall(Thing): pass                       # 25

        AllDisjoint([GeographicArea, Infrastructure, Facility, Resource, Officer,
                     RainfallAlertLevel, FloodEvent, EvacuationOrder, HeavyRainfall])
        AllDisjoint([LowLyingWard, HighGroundWard])
        AllDisjoint([River, Canal, Reservoir])
        AllDisjoint([Ward, WaterBody])
        AllDisjoint([PumpStation, StormwaterDrain, Road, Subway])
        AllDisjoint([ReliefCamp, Hospital])
        AllDisjoint([Pump, RescueBoat])

        # ---------- TASK 2 : object properties (domain, range) ----------
        class servesWard(ObjectProperty):
            domain = [PumpStation]; range = [Ward]
        class isServedBy(ObjectProperty):
            domain = [Ward]; range = [PumpStation]; inverse_property = servesWard
        class locatedIn(ObjectProperty):
            domain = [Infrastructure | Facility]; range = [Ward]
        class flowsInto(ObjectProperty, TransitiveProperty):
            domain = [StormwaterDrain | WaterBody]; range = [WaterBody]
        class hasAlertLevel(ObjectProperty, FunctionalProperty):
            domain = [Ward]; range = [RainfallAlertLevel]
        class causes(ObjectProperty):
            domain = [HeavyRainfall]; range = [FloodEvent]
        class affects(ObjectProperty):
            domain = [FloodEvent]; range = [Ward]
        class inundates(ObjectProperty):
            domain = [FloodEvent]; range = [Road | Subway]
        class evacuatesTo(ObjectProperty):
            domain = [Ward]; range = [ReliefCamp]
        class deployedIn(ObjectProperty):
            domain = [PortablePump | RescueBoat]; range = [Ward]
        class managedBy(ObjectProperty):
            domain = [Facility | PumpStation]; range = [Officer]
        class partOf(ObjectProperty):
            domain = [Pump]; range = [PumpStation]
        class issuedFor(ObjectProperty):
            domain = [EvacuationOrder]; range = [Ward]

        # data properties
        class hasElevationM(DataProperty, FunctionalProperty):
            domain = [Ward]; range = [float]
        class hasPopulation(DataProperty, FunctionalProperty):
            domain = [Ward]; range = [int]
        class hasAtRiskPopulation(DataProperty, FunctionalProperty):
            domain = [Ward]; range = [int]
        class hasCapacity(DataProperty, FunctionalProperty):
            domain = [ReliefCamp]; range = [int]
        class hasPumpingCapacityLps(DataProperty, FunctionalProperty):
            domain = [Pump]; range = [int]
        class hasRainfallMm(DataProperty, FunctionalProperty):
            domain = [HeavyRainfall]; range = [float]
        class hasThresholdMm(DataProperty, FunctionalProperty):
            domain = [RainfallAlertLevel]; range = [float]
        class hasWaterLevelM(DataProperty, FunctionalProperty):
            domain = [WaterBody]; range = [float]
        class hasDangerLevelM(DataProperty, FunctionalProperty):
            domain = [WaterBody]; range = [float]
        class isOperational(DataProperty, FunctionalProperty):
            domain = [PumpStation]; range = [bool]
        class hasPhone(DataProperty, FunctionalProperty):
            domain = [Officer]; range = [str]

        # defined (inferred) classes -> exercised by the reasoner
        class ServedWard(Ward):
            equivalent_to = [Ward & isServedBy.some(PumpStation)]
        class UnprotectedWard(Ward):
            equivalent_to = [Ward & isServedBy.some(PumpStation & isOperational.value(False))]
        class OperationalPumpStation(PumpStation):
            equivalent_to = [PumpStation & isOperational.value(True)]

        # ---------- TASK 3 : individuals (49) ----------
        wards = {}
        for n, el, pop, cls in [
            ("Velachery", 2.5, 142000, LowLyingWard), ("Pallikaranai", 1.8, 98000, LowLyingWard),
            ("Saidapet", 3.2, 121000, LowLyingWard), ("Perungudi", 2.1, 87000, LowLyingWard),
            ("Sholinganallur", 2.9, 134000, LowLyingWard), ("AnnaNagar", 11.5, 165000, HighGroundWard),
            ("Kilpauk", 9.8, 76000, HighGroundWard), ("Mylapore", 6.4, 110000, HighGroundWard)]:
            w = cls(n); w.hasElevationM = el; w.hasPopulation = pop; wards[n] = w
            w.hasAtRiskPopulation = {"Velachery": 2200, "Pallikaranai": 1400, "Saidapet": 450,
                                     "Perungudi": 900, "Sholinganallur": 1200}.get(n, 0)

        wb = {}
        for n, cls, lvl in [("AdyarRiver", River, 3.1), ("CooumRiver", River, 2.4),
                            ("BuckinghamCanal", Canal, 1.9), ("ChembarambakkamLake", Reservoir, 21.4)]:
            o = cls(n); o.hasWaterLevelM = lvl; wb[n] = o
            o.hasDangerLevelM = {"AdyarRiver": 5.0, "CooumRiver": 4.0, "BuckinghamCanal": 4.5,
                                 "ChembarambakkamLake": 24.0}[n]
        wb["AdyarRiver"].flowsInto = [wb["BuckinghamCanal"]]
        wb["CooumRiver"].flowsInto = [wb["BuckinghamCanal"]]

        drains = {}
        for n, tgt, ward in [("SWD_Velachery", "AdyarRiver", "Velachery"),
                             ("SWD_Pallikaranai", "BuckinghamCanal", "Pallikaranai"),
                             ("SWD_Saidapet", "AdyarRiver", "Saidapet")]:
            d = StormwaterDrain(n); d.flowsInto = [wb[tgt]]; d.locatedIn = [wards[ward]]; drains[n] = d

        officers = {}
        for n, ph in [("OFF_Ramesh", "+91-44-2500-0101"), ("OFF_Priya", "+91-44-2500-0102"),
                      ("OFF_Karthik", "+91-44-2500-0103")]:
            o = Officer(n); o.hasPhone = ph; officers[n] = o

        ps = {}
        for n, ward, op, off in [("PS_Velachery", "Velachery", True, "OFF_Ramesh"),
                                 ("PS_Pallikaranai", "Pallikaranai", True, "OFF_Ramesh"),
                                 ("PS_Saidapet", "Saidapet", True, "OFF_Priya"),
                                 ("PS_Perungudi", "Perungudi", False, "OFF_Karthik")]:
            p = PumpStation(n); p.isOperational = op; p.servesWard = [wards[ward]]
            p.locatedIn = [wards[ward]]; p.managedBy = [officers[off]]; ps[n] = p

        for n, cls, cap, st in [("FP_Velachery1", Pump, 1500, "PS_Velachery"),
                                ("FP_Pallikaranai1", Pump, 2000, "PS_Pallikaranai")]:
            p = cls(n); p.hasPumpingCapacityLps = cap; p.partOf = [ps[st]]
        for n, cap, ward in [("PP_01", 500, None), ("PP_02", 500, None), ("PP_03", 500, "Sholinganallur")]:
            p = PortablePump(n); p.hasPumpingCapacityLps = cap
            if ward: p.deployedIn = [wards[ward]]

        camps = {}
        for n, cap, ward, off in [("RC_VelacheryHS", 800, "Velachery", "OFF_Ramesh"),
                                  ("RC_PallikaranaiSchool", 600, "Pallikaranai", "OFF_Priya"),
                                  ("RC_SaidapetCommunity", 500, "Saidapet", "OFF_Priya"),
                                  ("RC_AnnaNagarHall", 1500, "AnnaNagar", "OFF_Karthik")]:
            c = ReliefCamp(n); c.hasCapacity = cap; c.locatedIn = [wards[ward]]
            c.managedBy = [officers[off]]; camps[n] = c
        for ward, cs in [("Velachery", ["RC_VelacheryHS", "RC_AnnaNagarHall"]),
                         ("Pallikaranai", ["RC_PallikaranaiSchool"]), ("Saidapet", ["RC_SaidapetCommunity"]),
                         ("Perungudi", ["RC_VelacheryHS"]), ("Sholinganallur", ["RC_AnnaNagarHall"])]:
            wards[ward].evacuatesTo = [camps[c] for c in cs]

        for n, ward, off in [("HOS_VelacheryGH", "Velachery", "OFF_Ramesh"),
                             ("HOS_AnnaNagarGH", "AnnaNagar", "OFF_Karthik")]:
            h = Hospital(n); h.locatedIn = [wards[ward]]; h.managedBy = [officers[off]]

        roads = {}
        for n, ward in [("RD_VelacheryMainRd", "Velachery"), ("RD_OMR", "Sholinganallur"),
                        ("RD_GST", "Pallikaranai")]:
            r = Road(n); r.locatedIn = [wards[ward]]; roads[n] = r
        subs = {}
        for n, ward in [("SW_SaidapetSubway", "Saidapet"), ("SW_KilpaukUnderpass", "Kilpauk")]:
            s = Subway(n); s.locatedIn = [wards[ward]]; subs[n] = s

        rb1 = RescueBoat("RB_01"); rb1.deployedIn = [wards["Velachery"]]
        RescueBoat("RB_02")

        alerts = {}
        for n, thr in [("AL_Green", 0.0), ("AL_Yellow", 64.5), ("AL_Orange", 115.6), ("AL_Red", 204.5)]:
            a = RainfallAlertLevel(n); a.hasThresholdMm = thr; alerts[n] = a
        AllDifferent(list(alerts.values()))
        for w, a in [("Velachery", "AL_Orange"), ("Pallikaranai", "AL_Red"), ("Saidapet", "AL_Yellow"),
                     ("Perungudi", "AL_Red"), ("Sholinganallur", "AL_Orange"), ("AnnaNagar", "AL_Green"),
                     ("Kilpauk", "AL_Green"), ("Mylapore", "AL_Green")]:
            wards[w].hasAlertLevel = alerts[a]

        hrA = HeavyRainfall("HR_Event_A"); hrA.hasRainfallMm = 132.4
        hrB = HeavyRainfall("HR_Event_B"); hrB.hasRainfallMm = 218.0
        feA = FloodEvent("FE_01"); feB = FloodEvent("FE_02")
        hrA.causes = [feA]; hrB.causes = [feB]
        feA.affects = [wards["Velachery"], wards["Saidapet"]]
        feA.inundates = [roads["RD_VelacheryMainRd"], subs["SW_SaidapetSubway"]]
        feB.affects = [wards["Pallikaranai"], wards["Perungudi"], wards["Sholinganallur"]]
        feB.inundates = [roads["RD_OMR"], roads["RD_GST"]]
        eo = EvacuationOrder("EO_01"); eo.issuedFor = [wards["Pallikaranai"]]

        # ---------- seeded faults for Task 10 (never in the clean ontology) ----------
        if 1 in faults:   # unsatisfiable class: a Road that is also a WaterBody
            class AmphibiousRoad(Road, WaterBody): pass
            AllDisjoint([Infrastructure, WaterBody])
        if 2 in faults:   # inconsistency: one ward asserted low-lying AND high-ground
            wards["Velachery"].is_a.append(HighGroundWard)
        if 3 in faults:   # inconsistency: functional property with two different values
            wards["Saidapet"].hasAlertLevel = alerts["AL_Yellow"]
            wards["Saidapet"].is_a.append(hasAlertLevel.value(alerts["AL_Red"]))
    return onto

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if "--fault" in sys.argv:
        k = int(sys.argv[sys.argv.index("--fault") + 1])
        o = build({k}); o.save(os.path.join(OUT, f"test_fault{k}.owl"), format="rdfxml")
    else:
        o = build(); o.save(os.path.join(OUT, "flood_ontology.owl"), format="rdfxml")
        g = rdflib.Graph(); g.parse(os.path.join(OUT, "flood_ontology.owl"), format="xml")
        g.bind("flood", BASE); g.serialize(os.path.join(OUT, "flood_ontology.ttl"), format="turtle")
        print("classes:", len(list(o.classes())), "obj props:", len(list(o.object_properties())),
              "data props:", len(list(o.data_properties())), "individuals:", len(list(o.individuals())))
