const fs = require('fs'); const path = require('path');
const D = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, HeadingLevel, AlignmentType,
  BorderStyle, WidthType, ShadingType, LevelFormat, PageBreak, Footer, PageNumber } = D;
const SS = path.join(__dirname, '..', 'screenshots');
const W = 9638; // content width (A4, 2 cm margins)
const FONT = 'Calibri', MONO = 'Consolas';

function runs(text, base = {}) {            // **bold** and `code` inline markup
  const out = []; const re = /(\*\*[^*]+\*\*|`[^`]+`)/g; let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const t = m[0];
    if (t.startsWith('**')) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: 20, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o.run), spacing: { after: 120, line: 276 }, alignment: o.align, keepNext: o.keepNext });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const B = t => new Paragraph({ numbering: { reference: 'bul', level: 0 }, children: runs(t), spacing: { after: 60, line: 264 } });
let NREF = 'num';
const N = t => new Paragraph({ numbering: { reference: NREF, level: 0 }, children: runs(t), spacing: { after: 60, line: 264 } });
const CAP = t => new Paragraph({ children: [new TextRun({ text: t, italics: true, size: 18, color: '555555', font: FONT })], alignment: AlignmentType.CENTER, spacing: { after: 200 } });
function code(text) {
  const lines = text.replace(/\n$/, '').split('\n');
  return lines.map((l, i) => new Paragraph({
    children: [new TextRun({ text: l === '' ? ' ' : l, font: MONO, size: 17 })],
    shading: { type: ShadingType.CLEAR, fill: 'F3F4F6' }, spacing: { after: 0, line: 240 },
    border: i === 0 ? { top: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 4 } } : (i === lines.length - 1 ? { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'CCCCCC', space: 4 } } : undefined),
    indent: { left: 100, right: 100 }
  })).concat([new Paragraph({ children: [], spacing: { after: 120 } })]);
}
function pngSize(f) { const b = fs.readFileSync(f); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function img(name, caption, maxW = 620, maxH = 880) {
  const f = path.join(SS, name); const { w, h } = pngSize(f);
  let sc = Math.min(maxW / w, maxH / h, 1.0); if (w * sc < 300 && w < maxW) sc = Math.min(maxW / w, maxH / h, 1.6);
  return [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 40 }, keepNext: true,
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(f), transformation: { width: Math.round(w * sc), height: Math.round(h * sc) },
      altText: { title: name, description: caption, name } })] }), CAP(caption)];
}
const cellB = { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF' };
const borders = { top: cellB, bottom: cellB, left: cellB, right: cellB };
function table(headers, rows, widths, opts = {}) {
  const tot = widths.reduce((a, b) => a + b, 0);
  const mk = (txt, wd, hdr, i) => new TableCell({
    width: { size: wd, type: WidthType.DXA }, borders,
    shading: { type: ShadingType.CLEAR, fill: hdr ? '1F3864' : (opts.zebra && i % 2 ? 'F2F6FC' : 'FFFFFF') },
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: String(txt).split('\n').map(line => new Paragraph({ spacing: { after: 0 },
      children: hdr ? [new TextRun({ text: line, bold: true, color: 'FFFFFF', size: 19, font: FONT })] : runs(line, { size: opts.size || 19 }) }))
  });
  return new Table({ width: { size: tot, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => mk(h, widths[i], true)) }),
      ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => mk(c, widths[i], false, ri)) }))] });
}
const gap = () => new Paragraph({ children: [], spacing: { after: 120 } });
const PB = () => new Paragraph({ children: [new PageBreak()] });

// =============================================================== CONTENT
const c = [];
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: 'Knowledge Engineering and Data Science', bold: true, size: 36, font: FONT, color: '1F3864' })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: 'Assignment 1 (CO1): Flood-Response Knowledge Base for a Coastal City', bold: true, size: 28, font: FONT })] }));
c.push(table(['Field', 'Details'], [['Student name', ''], ['Register number', ''], ['Department and section', ''], ['Faculty', ''], ['Date of issue', ''], ['Date of submission', '']], [3200, 6438]));
c.push(gap());
c.push(P('**Course outcome covered (CO1):** apply knowledge engineering principles to model, represent and manage domain knowledge using ontologies, semantic networks and rule-based systems.'));
c.push(P('**Scenario:** a municipal corporation needs a knowledge base to help officers respond to urban flooding during the northeast monsoon. The sample data uses Chennai-region ward names; every number in the individuals (elevation, population, camp capacity, pump status) is **illustrative sample data written by me, not official municipal data**.'));
c.push(P('**Tools used (all stated, equivalent tools permitted):** Python 3 with **owlready2** (ontology construction, OWL 2 RDF/XML output) and the **HermiT** reasoner it bundles (Java 21); **rdflib** for Turtle and SPARQL 1.1; a small **forward-chaining rule engine written in Python** for the production rules (CLIPS was not used); **Graphviz** for the semantic network. Protégé was not used: the .owl file opens directly in Protégé, but all reasoning in this report was run with HermiT from Python.'));
c.push(P('**Source code and data:** https://github.com/vani105/DSA1604  (folders: ontology, sparql, rules, reasoner, screenshots, report).'));
c.push(P('**About the "screenshots":** each screenshot is a rendered capture of the real console output of the script named in its title bar (generated by `diagrams/make_screenshots.py`), not a photo of a GUI window. Re-running the scripts reproduces them.', { run: { italics: true } }));

// ---------------- Task 1
c.push(H1('Task 1. Domain concepts and class hierarchy (3 marks)'));
c.push(P('Twenty-five domain concepts were modelled as OWL classes. Sibling classes are declared **disjoint** so the reasoner can detect modelling mistakes (Task 10). Three further *defined* classes (ServedWard, UnprotectedWard, OperationalPumpStation) are added for inference and are not counted among the 25.'));
const concepts = [
  ['1', 'GeographicArea', 'Thing', 'Any spatial unit relevant to flooding'],
  ['2', 'Ward', 'GeographicArea', 'Municipal administrative ward'],
  ['3', 'LowLyingWard', 'Ward', 'Ward prone to water-logging (sample elevations 1.8 - 3.2 m)'],
  ['4', 'HighGroundWard', 'Ward', 'Ward on higher ground (sample elevations 6.4 - 11.5 m); hosts camps'],
  ['5', 'WaterBody', 'GeographicArea', 'Any river, canal or reservoir'],
  ['6', 'River', 'WaterBody', 'Natural river channel (e.g., Adyar)'],
  ['7', 'Canal', 'WaterBody', 'Man-made canal (e.g., Buckingham Canal)'],
  ['8', 'Reservoir', 'WaterBody', 'Lake or storage reservoir'],
  ['9', 'Infrastructure', 'Thing', 'Physical drainage and transport assets'],
  ['10', 'PumpStation', 'Infrastructure', 'Fixed station that pumps water out of a ward'],
  ['11', 'StormwaterDrain', 'Infrastructure', 'Drain carrying runoff to a water body'],
  ['12', 'Road', 'Infrastructure', 'Road that can be inundated and closed'],
  ['13', 'Subway', 'Infrastructure', 'Underpass / pedestrian or vehicle subway'],
  ['14', 'Facility', 'Thing', 'Building that serves the public'],
  ['15', 'ReliefCamp', 'Facility', 'Shelter for evacuees (has capacity)'],
  ['16', 'Hospital', 'Facility', 'Critical facility that must stay accessible'],
  ['17', 'Resource', 'Thing', 'Deployable asset'],
  ['18', 'Pump', 'Resource', 'Any pump (fixed or portable)'],
  ['19', 'PortablePump', 'Pump', 'Mobile pump that can be sent to a ward'],
  ['20', 'RescueBoat', 'Resource', 'Boat for rescue in inundated areas'],
  ['21', 'Officer', 'Thing', 'Municipal officer managing facilities'],
  ['22', 'RainfallAlertLevel', 'Thing', 'Green / Yellow / Orange / Red with mm threshold'],
  ['23', 'FloodEvent', 'Thing', 'An occurrence of flooding'],
  ['24', 'EvacuationOrder', 'Thing', 'Order to evacuate a ward'],
  ['25', 'HeavyRainfall', 'Thing', 'Rainfall episode with measured mm'],
];
c.push(table(['No.', 'Class', 'Parent (is-a)', 'Meaning'], concepts, [600, 2300, 2200, 4538], { zebra: true, size: 18 }));
c.push(gap()); c.push(P('**Class hierarchy** (asserted; indentation = subclass):', { keepNext: true }));
c.push(...code(`Thing
+- GeographicArea
|   +- Ward
|   |   +- LowLyingWard        (disjoint with HighGroundWard)
|   |   +- HighGroundWard
|   |   +- [defined] ServedWard, UnprotectedWard
|   +- WaterBody
|       +- River | Canal | Reservoir    (pairwise disjoint)
+- Infrastructure
|   +- PumpStation  [defined subclass: OperationalPumpStation]
|   +- StormwaterDrain | Road | Subway
+- Facility
|   +- ReliefCamp | Hospital
+- Resource
|   +- Pump
|   |   +- PortablePump
|   +- RescueBoat
+- Officer | RainfallAlertLevel | FloodEvent | EvacuationOrder | HeavyRainfall`));

// ---------------- Task 2
c.push(H1('Task 2. Object and data properties (3 marks)'));
c.push(P('Thirteen object properties (requirement: at least 8) and eleven data properties (requirement: at least 6). Where a domain or range is a union it is written (A or B).'));
c.push(table(['Object property', 'Domain', 'Range', 'Characteristics'], [
  ['servesWard', 'PumpStation', 'Ward', 'inverse of isServedBy'],
  ['isServedBy', 'Ward', 'PumpStation', 'inverse of servesWard'],
  ['locatedIn', '(Infrastructure or Facility)', 'Ward', ''],
  ['flowsInto', '(StormwaterDrain or WaterBody)', 'WaterBody', 'transitive'],
  ['hasAlertLevel', 'Ward', 'RainfallAlertLevel', 'functional'],
  ['causes', 'HeavyRainfall', 'FloodEvent', ''],
  ['affects', 'FloodEvent', 'Ward', ''],
  ['inundates', 'FloodEvent', '(Road or Subway)', ''],
  ['evacuatesTo', 'Ward', 'ReliefCamp', ''],
  ['deployedIn', '(PortablePump or RescueBoat)', 'Ward', ''],
  ['managedBy', '(Facility or PumpStation)', 'Officer', ''],
  ['partOf', 'Pump', 'PumpStation', 'part-whole'],
  ['issuedFor', 'EvacuationOrder', 'Ward', ''],
], [2100, 3100, 2300, 2138], { zebra: true, size: 18 }));
c.push(gap());
c.push(table(['Data property', 'Domain', 'Range', 'Meaning / unit'], [
  ['hasElevationM', 'Ward', 'xsd:float', 'ground elevation, metres (functional)'],
  ['hasPopulation', 'Ward', 'xsd:integer', 'total residents'],
  ['hasAtRiskPopulation', 'Ward', 'xsd:integer', 'residents in flood-prone pockets'],
  ['hasCapacity', 'ReliefCamp', 'xsd:integer', 'persons the camp can hold'],
  ['hasPumpingCapacityLps', 'Pump', 'xsd:integer', 'litres per second'],
  ['hasRainfallMm', 'HeavyRainfall', 'xsd:float', '24-hour rainfall, mm'],
  ['hasThresholdMm', 'RainfallAlertLevel', 'xsd:float', 'rainfall at which the level starts'],
  ['hasWaterLevelM', 'WaterBody', 'xsd:float', 'current level, metres'],
  ['hasDangerLevelM', 'WaterBody', 'xsd:float', 'danger mark, metres'],
  ['isOperational', 'PumpStation', 'xsd:boolean', 'working / failed'],
  ['hasPhone', 'Officer', 'xsd:string', 'contact number'],
], [2500, 2100, 1700, 3338], { zebra: true, size: 18 }));
c.push(gap());
c.push(P('Alert thresholds follow the India Meteorological Department 24-hour rainfall categories (heavy from 64.5 mm, very heavy from 115.6 mm, extremely heavy from 204.5 mm), mapped to Yellow, Orange and Red. A municipality should confirm its own thresholds; they are data in the ontology, so changing them needs no code change.'));

// ---------------- Task 3
c.push(H1('Task 3. Ontology with at least 40 individuals (6 marks)'));
c.push(P('The ontology is built by `build_ontology.py` (owlready2) and saved as **ontology/flood_ontology.owl** (RDF/XML, loadable in Protégé) and **ontology/flood_ontology.ttl** (Turtle, 484 triples). It contains **49 individuals**:'));
c.push(table(['Class', 'No.', 'Individuals'], [
  ['LowLyingWard', '5', 'Velachery, Pallikaranai, Saidapet, Perungudi, Sholinganallur'],
  ['HighGroundWard', '3', 'AnnaNagar, Kilpauk, Mylapore'],
  ['River / Canal / Reservoir', '4', 'AdyarRiver, CooumRiver, BuckinghamCanal, ChembarambakkamLake'],
  ['StormwaterDrain', '3', 'SWD_Velachery, SWD_Pallikaranai, SWD_Saidapet'],
  ['PumpStation', '4', 'PS_Velachery, PS_Pallikaranai, PS_Saidapet, PS_Perungudi (not operational)'],
  ['Pump / PortablePump', '2 + 3', 'FP_Velachery1, FP_Pallikaranai1; PP_01, PP_02, PP_03'],
  ['ReliefCamp', '4', 'RC_VelacheryHS, RC_PallikaranaiSchool, RC_SaidapetCommunity, RC_AnnaNagarHall'],
  ['Hospital', '2', 'HOS_VelacheryGH, HOS_AnnaNagarGH'],
  ['Road / Subway', '3 + 2', 'RD_VelacheryMainRd, RD_OMR, RD_GST; SW_SaidapetSubway, SW_KilpaukUnderpass'],
  ['Officer', '3', 'OFF_Ramesh, OFF_Priya, OFF_Karthik'],
  ['RescueBoat', '2', 'RB_01, RB_02'],
  ['RainfallAlertLevel', '4', 'AL_Green, AL_Yellow, AL_Orange, AL_Red (declared AllDifferent)'],
  ['HeavyRainfall / FloodEvent / EvacuationOrder', '2 + 2 + 1', 'HR_Event_A, HR_Event_B; FE_01, FE_02; EO_01'],
  ['**Total**', '**49**', ''],
], [2900, 900, 5838], { zebra: true, size: 18 }));
c.push(gap());
c.push(P('Modelling features beyond plain subclassing: disjointness axioms, an inverse pair (servesWard / isServedBy), a transitive property (flowsInto), functional properties, union domains and ranges, and three defined classes whose membership the reasoner infers (Task 10). The screenshot below is the output of `ontology/inspect_ontology.py`.'));
c.push(...img('ss_ontology_summary.png', 'Screenshot 1: ontology summary (classes with individual counts, properties, totals)', 560, 780));

// ---------------- Task 4
c.push(H1('Task 4. Semantic network (4 marks)'));
c.push(P('The network has **27 nodes** (19 ontology classes, 4 network-only event nodes, 2 aggregate nodes City and DrainageNetwork, and 2 individuals) and three relation types: **is-a** (solid grey, hollow arrow), **part-of** (dashed blue, diamond) and **causes** (bold red). The nodes WaterLogging, RiverOverflow, DrainBlockage and TrafficDisruption, and the aggregate nodes City and DrainageNetwork, exist only in the semantic network: they capture causal knowledge that the OWL ontology does not model.'));
c.push(...img('fig_semantic_network.png', 'Figure 1: semantic network of the flood-response domain', 640, 600));
c.push(P('**Causal chains shown:** HeavyRainfall causes FloodEvent directly and via RiverOverflow; FloodEvent causes WaterLogging, which causes TrafficDisruption; DrainBlockage also causes WaterLogging; FloodEvent causes EvacuationOrder. **Part-whole chains:** Pump is part of PumpStation, which is part of DrainageNetwork, which is part of City; Ward is part of City.'));

// ---------------- Task 5
c.push(H1('Task 5. Inheritance and property inheritance (3 marks)'));
c.push(...img('fig_inheritance.png', 'Figure 2: class inheritance and property inheritance examples', 520, 400));
c.push(P('**Example of inheritance (is-a):** PP_01 is-a PortablePump is-a Pump is-a Resource. Because of this chain, PP_01 is also a Pump and a Resource, so every rule or query about Pumps or Resources applies to it without restating anything. The same holds for Velachery is-a LowLyingWard is-a Ward is-a GeographicArea.'));
c.push(P('**Example of property inheritance:** the slot `hasPumpingCapacityLps` is declared once on **Pump**. PortablePump adds no slots of its own, yet PP_01 carries `hasPumpingCapacityLps = 500`: it inherited the slot from Pump and supplies a local value. Likewise `hasPopulation`, `hasElevationM` and `hasAlertLevel` are declared on **Ward** and used by the LowLyingWard individual Velachery (population 142000, elevation 2.5 m). The check below queries the ontology itself (subclass paths and property domains) to confirm this.'));
c.push(...img('ss_inheritance_check.png', 'Screenshot 2: inheritance check run against flood_ontology.ttl', 560, 300));

// ---------------- Task 6
c.push(H1('Task 6. Competency questions and SPARQL (4 marks)'));
c.push(P('Queries are in `sparql/cq1.rq`, `cq2.rq`, `cq3.rq`, and are executed by `sparql/run_queries.py` with rdflib against the Turtle file.'));
c.push(H2('CQ1. Which low-lying wards are served by a non-operational pump station and so need a portable pump?'));
c.push(...code(fs.readFileSync(path.join(__dirname, '..', 'sparql', 'cq1.rq'), 'utf8')));
c.push(...img('ss_sparql_cq1.png', 'Screenshot 3: CQ1 result', 480, 300));
c.push(P('**Answer:** Perungudi (87,000 residents, station PS_Perungudi is down).'));
c.push(H2('CQ2. Can each low-lying ward\'s designated relief camps hold its at-risk residents?'));
c.push(...code(fs.readFileSync(path.join(__dirname, '..', 'sparql', 'cq2.rq'), 'utf8')));
c.push(...img('ss_sparql_cq2.png', 'Screenshot 4: CQ2 result', 520, 340));
c.push(P('**Answer:** Pallikaranai (1,400 at risk vs 600 places) and Perungudi (900 vs 800) have a shortfall; Saidapet, Sholinganallur and Velachery are within capacity. **Caveat:** the query judges each ward against its own camps and ignores that camps are shared (RC_VelacheryHS serves Velachery and Perungudi; RC_AnnaNagarHall serves Velachery and Sholinganallur), so the true picture is worse. The rule run in Task 7 shows this.'));
c.push(H2('CQ3. Which hospitals are in flood-affected wards, and which officer must be called?'));
c.push(...code(fs.readFileSync(path.join(__dirname, '..', 'sparql', 'cq3.rq'), 'utf8')));
c.push(...img('ss_sparql_cq3.png', 'Screenshot 5: CQ3 result', 520, 300));
c.push(P('**Answer:** HOS_VelacheryGH, in Velachery (affected by FE_01); contact OFF_Ramesh on +91-44-2500-0101 (sample number).'));

// ---------------- Task 7
c.push(H1('Task 7. Twelve production rules (6 marks)'));
c.push(P('Rules are stored in `rules/flood_rules.txt` (plain text) and executed by `rules/flood_rules.py`. The engine loads ward, camp, pump and hospital facts **from the ontology** (via rdflib) and takes live sensor values (24-hour rainfall, river level, water depth) from a scenario dictionary. Priority is the salience used for conflict resolution (Task 8).'));
const R = [
  ['R01', 'Alert escalation', 'IF 24-h rainfall >= 204.5 mm AND ward alert < RED THEN set alert RED', '90'],
  ['R02', 'Alert escalation', 'IF 24-h rainfall >= 115.6 mm AND ward alert < ORANGE THEN set alert ORANGE', '80'],
  ['R03', 'Alert escalation', 'IF 24-h rainfall >= 64.5 mm AND ward alert < YELLOW THEN set alert YELLOW', '70'],
  ['R04', 'Alert escalation', 'IF alert is YELLOW or ORANGE AND the receiving river/canal level >= its danger level THEN raise the alert by one level (once)', '85'],
  ['R05', 'Evacuation', 'IF alert = RED AND ward is low-lying AND at-risk residents > 0 AND no evacuation ordered THEN order MANDATORY evacuation to the designated camps', '100'],
  ['R06', 'Evacuation', 'IF alert = ORANGE AND ward is low-lying AND at-risk residents > 0 AND no evacuation ordered THEN issue ADVISORY evacuation', '60'],
  ['R07', 'Evacuation', 'IF an evacuation is ordered AND residents remain unplaced because designated camps are full THEN open an overflow shelter and alert camp officers', '88'],
  ['R08', 'Pump deployment', 'IF alert >= ORANGE AND ward is low-lying AND its pump station is NOT operational AND a portable pump is free THEN deploy a portable pump to the ward', '95'],
  ['R09', 'Pump deployment', 'IF alert >= YELLOW AND ward is low-lying AND its station IS operational AND a portable pump is free THEN pre-position a pump on standby', '50'],
  ['R10', 'Road closure', 'IF water depth on a road >= 0.30 m THEN close the road and divert traffic', '75'],
  ['R11', 'Subway closure', 'IF water depth in a subway >= 0.15 m THEN close the subway and dispatch a dewatering pump', '78'],
  ['R12', 'Critical facility', 'IF alert = RED AND the ward contains a hospital THEN put the hospital on emergency footing, confirm a rescue boat and notify its officer', '92'],
];
c.push(table(['ID', 'Group', 'IF ... THEN ...', 'Priority'], R, [650, 1650, 6538, 800], { zebra: true, size: 18 }));
c.push(gap());
c.push(P('**Test scenario** (sample sensor data): ward rainfall Pallikaranai 218 mm, Velachery 132.4 mm, Perungudi 125 mm, Sholinganallur 118 mm, Saidapet 90 mm, others 60 - 70 mm; Adyar River at 5.4 m (danger mark 5.0 m); Velachery main road 0.45 m deep, Saidapet subway 0.60 m; two free portable pumps. The engine fired 24 rule instances; the screenshots show the full trace (each line shows the rule, its priority, the action, the size of the conflict set and the runner-up).'));
c.push(...img('ss_rules_trace1.png', 'Screenshot 6: rule engine trace, part 1', 600, 800));
c.push(...img('ss_rules_trace2.png', 'Screenshot 7: rule engine trace, part 2', 600, 800));
c.push(...img('ss_rules_final.png', 'Screenshot 8: final working-memory state', 560, 340));

// ---------------- Task 8
c.push(H1('Task 8. Rule ranking and conflict resolution (3 marks)'));
c.push(P('**Ranking principle:** protect life first, then critical facilities and resources, then classify and warn, then routine preparation. Priorities are salience values: the highest-salience eligible rule fires first.'));
c.push(table(['Rank', 'Rule', 'Priority', 'Why it ranks here'], [
  ['1', 'R05 Mandatory evacuation', '100', 'Direct threat to life'],
  ['2', 'R08 Deploy portable pump', '95', 'Failed station means no protection at all'],
  ['3', 'R12 Hospital protection', '92', 'Critical facility; loss of function endangers many'],
  ['4', 'R01 Red alert', '90', 'Triggers the life-safety rules'],
  ['5', 'R07 Camp overflow', '88', 'Prevents evacuees being left without shelter'],
  ['6', 'R04 River-level escalation', '85', 'Corrects rainfall-only alert when river is at danger mark'],
  ['7', 'R02 Orange alert', '80', 'Classification'],
  ['8', 'R11 Subway closure', '78', 'Immediate risk of drowning in underpasses'],
  ['9', 'R10 Road closure', '75', 'Traffic safety'],
  ['10', 'R03 Yellow alert', '70', 'Classification'],
  ['11', 'R06 Advisory evacuation', '60', 'Voluntary; must not pre-empt mandatory orders'],
  ['12', 'R09 Standby pump', '50', 'Preparation only; yields pumps to R08'],
], [700, 3000, 1000, 4938], { zebra: true, size: 18 }));
c.push(gap());
c.push(P('**Conflict-resolution strategy (as implemented and tested):**', { keepNext: true }));
c.push(N('**Salience first.** Of all eligible rule instances (the conflict set), the one with the highest priority fires.'));
c.push(N('**Specificity.** On equal priority, the rule with more conditions wins.'));
c.push(N('**Severity of the instance.** On a further tie, the ward with the higher alert level, then more at-risk residents, goes first (for roads and subways, the deeper water). I added this after my first run, where a Yellow-alert ward received the last standby pump before an Orange/Red ward because ties were broken arbitrarily.'));
c.push(N('**Refraction and guards.** A rule instance fires once. Guards such as `alert < ORANGE` and `no evacuation ordered` make the rules monotonic during an event: alerts and evacuation levels only go up, so R06 (advisory) cannot fire after R05 (mandatory) and R01/R02/R03 do not overwrite each other. De-escalation is deliberately **not** automatic; it needs a human decision.'));
c.push(N('**Priority is not execution order across dependencies.** R05 (100) cannot fire before R01 (90) because its condition needs the alert that R01 sets; the recognise-act cycle handles this because R05 only enters the conflict set after R01 fires (see cycles 01-02 in the trace).'));
c.push(N('**Safety first.** If two rules would recommend different actions of the same kind, the more protective one wins; this is why the evacuation rules rank above the pump and closure rules.'));
c.push(N('**Human override.** Every firing is logged with its conflict set so the duty officer can see what was suppressed and can retract or pin a decision.'));
c.push(P('**What the test run revealed (limits of priority-based resolution):**', { keepNext: true }));
c.push(B('**Pump contention worked as intended:** R08 gave PP_01 to Perungudi (failed station) before R09 standby could take it; R09 then gave PP_02 to Velachery (Red, 2,200 at risk) rather than a lower-severity ward. Pallikaranai and Saidapet received no standby pump because none were left.'));
c.push(B('**Shared camps were not resolved well.** Velachery (processed first, higher severity) filled RC_AnnaNagarHall (1,500) and 500 places at RC_VelacheryHS. Sholinganallur and Perungudi, whose only designated camps were these two, then had **0 places** and R07 flagged 1,200 and 900 residents as unplaced. Priority rules decide who goes first; they do not decide how to share a scarce resource across wards. This needs a global allocation step (an optimisation or an officer decision) on top of the rules.'));

// ---------------- Task 9
c.push(H1('Task 9. Three rules in a second formalism (3 marks)'));
c.push(P('Rules R05, R08 and R12 are re-expressed as **frames** (slots, fillers and an action procedure) and as **description-logic** (DL) definitions. The DL versions capture the *condition* only; a DL class says which individuals qualify, not what to do about them. They were added to a copy of the ontology in memory and classified by HermiT (`reasoner/verify_dl_rules.py`).'));
c.push(H2('Rule R05 Mandatory evacuation'));
c.push(...code(`FRAME MandatoryEvacuationRule
  is-a:        EvacuationRule
  priority:    100
  applies-to:  Ward
  if-needed:   alert-level = RED
               ward-type = LowLyingWard
               at-risk-residents > 0
               evacuation-status = none
  then:        issue EvacuationOrder(MANDATORY); assign designated camps (evacuatesTo)
  if-added:    when unplaced > 0 -> trigger CampOverflowRule

DL:  MandatoryEvacuationWard  EQUIV  LowLyingWard
        AND  EXISTS hasAlertLevel.{AL_Red}
        AND  EXISTS hasAtRiskPopulation.(xsd:integer[>= 1])`));
c.push(H2('Rule R08 Deploy portable pump'));
c.push(...code(`FRAME PortablePumpDeploymentRule
  is-a:        PumpRule
  priority:    95
  applies-to:  Ward
  if-needed:   alert-level >= ORANGE
               ward-type = LowLyingWard
               serving-station.isOperational = false
               free portable pump available
  then:        deployedIn(portable pump, ward); remove pump from free pool

DL:  PortablePumpNeededWard  EQUIV  LowLyingWard
        AND  EXISTS hasAlertLevel.{AL_Orange, AL_Red}
        AND  EXISTS isServedBy.(PumpStation AND EXISTS isOperational.{false})`));
c.push(H2('Rule R12 Hospital protection'));
c.push(...code(`FRAME HospitalProtectionRule
  is-a:        CriticalFacilityRule
  priority:    92
  applies-to:  Hospital
  if-needed:   locatedIn(hospital, ward) with ward.alert-level = RED
  then:        set emergency footing; confirm rescue boat in ward; notify managedBy officer

DL:  EmergencyHospital  EQUIV  Hospital
        AND  EXISTS locatedIn.(Ward AND EXISTS hasAlertLevel.{AL_Red})`));
c.push(...img('ss_dl_rules.png', 'Screenshot 9: HermiT classification of the three DL rule definitions', 620, 300));
c.push(P('**Reading the result:** on the alert snapshot stored in the ontology (Pallikaranai and Perungudi Red, Velachery and Sholinganallur Orange), HermiT classifies Pallikaranai and Perungudi as MandatoryEvacuationWard and Perungudi as PortablePumpNeededWard. EmergencyHospital has no members because no Red ward currently contains a hospital in that snapshot, which is the correct answer. Note that the DL cannot express "the alert is the *result* of rainfall >= 204.5 mm", which needs arithmetic; this is why the alert-assignment rules R01 - R04 were not chosen for this task.'));

// ---------------- Task 10
c.push(H1('Task 10. Reasoner testing (6 marks)'));
c.push(P('**Honest note on method:** the final ontology was consistent and had no unsatisfiable class on the first reasoner run, so there was no accidental error to repair. To show that the testing process works, I **deliberately seeded three faults** in copies of the ontology (`ontology/test_fault1.owl` to `test_fault3.owl`, produced by `build_ontology.py --fault N`), ran HermiT on each, diagnosed it, and applied the fix. The fixed ontology is `flood_ontology.owl`.'));
c.push(table(['Test', 'Seeded fault', 'HermiT result', 'Diagnosis and fix'], [
  ['1', 'Class AmphibiousRoad declared a subclass of both Road and WaterBody, which sit under disjoint branches (Infrastructure vs GeographicArea)', 'Consistent, but **AmphibiousRoad is unsatisfiable** (equivalent to owl:Nothing)', 'A class cannot be both. Fix: delete the class; if the idea is needed (a road crossing a canal), model it as a Road with a `crossesWaterBody` relation to a Canal'],
  ['2', 'Individual Velachery asserted as both LowLyingWard and HighGroundWard', '**Ontology inconsistent**', 'The two classes are disjoint. Elevation 2.5 m confirms low-lying, so remove the HighGroundWard assertion'],
  ['3', 'Saidapet given two different alert levels (Yellow and Red) for the functional property hasAlertLevel; the alert levels are declared AllDifferent', '**Ontology inconsistent**', 'A ward can have only one current alert. Fix: retract the stale value before asserting the new one; in operation use a validation step that blocks double assignment'],
  ['4', 'Final ontology after fixes', '**Consistent; no unsatisfiable classes**', 'Defined classes classify correctly (below)'],
], [550, 3000, 2400, 3688], { size: 17 }));
c.push(gap());
c.push(...img('ss_reasoner_faults.png', 'Screenshot 10: HermiT output on the three seeded-fault ontologies', 580, 400));
c.push(...img('ss_reasoner_fixed.png', 'Screenshot 11: HermiT output on the fixed ontology, with inferred knowledge', 580, 560));
c.push(P('**What the reasoner inferred on the fixed ontology (useful results, not just error checking):**', { keepNext: true }));
c.push(B('**ServedWard** = Velachery, Pallikaranai, Saidapet, Perungudi, found through the *inverse* property: only servesWard was asserted, and HermiT derived isServedBy.'));
c.push(B('**UnprotectedWard** = Perungudi, because its serving station has isOperational = false.'));
c.push(B('**OperationalPumpStation** = three of the four stations.'));
c.push(B('**Transitive flowsInto:** SWD_Saidapet and SWD_Velachery drain into AdyarRiver and, transitively, BuckinghamCanal.'));
c.push(P('**Limitation of this testing:** owlready2 reports *that* an ontology is inconsistent but not *which axioms* cause it. I located each fault from my knowledge of what I had seeded. For an unknown inconsistency, Protégé\'s "Explain inconsistent ontology" feature would be the tool to use. Also, because OWL uses the open-world assumption, the reasoner does **not** flag Sholinganallur (no pump station asserted) as a problem; it simply does not know. A SPARQL or SHACL check is needed for completeness rules like "every low-lying ward must have a pump station".'));

// ---------------- Task 11
NREF = 'num2';
c.push(H1('Task 11. Updating the knowledge base after each monsoon season (3 marks)'));
c.push(P('The northeast monsoon runs roughly October to December, so the update cycle is: **post-season review in January, release in February to April, freeze by mid-September**, with no changes during the season except emergency corrections.'));
c.push(H2('What is updated'));
c.push(B('**Facts:** pump station status and capacity, new drains and camps, ward population and at-risk pockets, camp capacities, officer contacts.'));
c.push(B('**Event records:** each flood event, depths observed per road and subway, pumps that failed, camp occupancy reached, response times.'));
c.push(B('**Rule parameters and rules:** alert thresholds and depth limits recalibrated from false alarms and missed events; rules added, retired or re-prioritised.'));
c.push(H2('Versioning'));
c.push(B('Semantic version numbers in `owl:versionIRI` and `owl:versionInfo`: patch (data corrections), minor (new individuals, thresholds), major (class or property changes that break queries or rules).'));
c.push(B('The ontology, rule file and SPARQL queries live in one Git repository; every release is tagged (for example `v2026.1`) with a changelog. Rules carry their own version and a "last reviewed" date.'));
c.push(B('Deprecate, do not delete: mark retired terms with `owl:deprecated true` and a replacement, so old event records stay interpretable. Keep the previous season\'s release archived read-only for audit.'));
c.push(H2('Validation before release (all must pass)'));
c.push(N('**Reasoner:** HermiT reports consistent and no unsatisfiable classes.'));
c.push(N('**Regression queries:** the competency questions (CQ1 to CQ3 and any new ones) return the expected answers on a fixed test dataset.'));
c.push(N('**Completeness checks (SHACL or SPARQL):** every ward has exactly one alert level, every low-lying ward has a station and at least one camp, every camp has a capacity and an officer, no camp is oversubscribed by its designated wards.'));
c.push(N('**Rule replay:** run the rule engine on recorded past events and compare with what officers actually did; investigate every disagreement.'));
c.push(N('**Expert review and sign-off:** the domain owners below approve a diff of what changed.'));
c.push(H2('Ownership'));
c.push(table(['Role', 'Responsibility'], [
  ['Knowledge owner (e.g., Superintending Engineer, Storm Water Drains)', 'Final approval of each release; accountable for the content'],
  ['Zone data stewards (one per zone)', 'Supply and correct ward-level facts: stations, camps, contacts, at-risk pockets'],
  ['Ontology engineer / data team', 'Maintain the ontology, rules and tests; run validation; manage releases'],
  ['Disaster-management cell and meteorology liaison', 'Review thresholds and rules after each season; approve alert policy changes'],
  ['Review board (owner, stewards, engineer, cell)', 'Meets in the post-season review; decides change requests'],
], [4200, 5438], { zebra: true, size: 18 }));
c.push(gap());
c.push(P('Changes arrive as change requests (who, what, why, evidence), are applied on a branch, validated, reviewed and then merged. Emergency corrections during the season are allowed only for facts (for example a pump failure) and are logged, never for rules.'));

// ---------------- Task 12
c.push(H1('Task 12. Critique: what the knowledge base cannot represent (6 marks)'));
c.push(P('This knowledge base is good at stable structure (what exists, where, how it is classified) and at crisp threshold rules. It is weak in the places where flood response is hardest.'));
c.push(P('**1. Time and dynamics.** Flooding is a process: water rises, peaks and recedes, and decisions depend on the trend. The ontology holds single snapshot values (a water level, an alert), and my rules react to a level, not to its rate of change. Without temporal modelling the system cannot say "the river will cross the danger mark in two hours".'));
c.push(P('**2. Uncertainty.** Rainfall forecasts are probabilistic and sensor readings are noisy. OWL and IF-THEN rules are crisp: 204.4 mm gives Orange and 204.5 mm gives Red. Real officers weigh confidence, and a Bayesian or fuzzy layer would be needed.'));
c.push(P('**3. Space and geometry.** Which streets drain where, which wards border each other, which road is the only access to a hospital, and where within a ward the low pockets are all depend on geography. I approximated this with a single `hasAtRiskPopulation` number and a one-step `flowsInto` chain. A GIS with elevation models and routing is the proper source; OWL can only hold the results.'));
c.push(P('**4. Numerical and optimisation reasoning.** OWL cannot add or compare quantities; I needed SPARQL aggregation and Python for camp capacity. The test run exposed the deeper problem: priority rules decide who goes first, but sharing a scarce resource fairly (two wards whose only camp is the same hall) is an allocation problem that rules solve badly. Velachery took the Anna Nagar hall and left Sholinganallur and Perungudi with nothing.'));
c.push(P('**5. Open-world assumption and missing data.** If a ward has no pump station recorded, the reasoner does not conclude that it has none. Absence of data (for example Sholinganallur) cannot be detected by OWL alone and needs closed-world checks.'));
c.push(P('**6. Two sources of truth.** The ontology stores a stored alert level per ward, while the rule engine computes alerts from rainfall. In my own data the stored snapshot says Velachery is Orange whereas the rule run derives Red once the river is above its danger mark. A real system must decide which one is authoritative and keep them synchronised; the OWL file and the rule file are only loosely coupled.'));
c.push(P('**7. Cascading and interdependent failures.** A power cut can stop several pump stations, a blocked drain can overload another, and a flooded road can cut a camp off. The model treats assets as independent, so it cannot reason about such chains.'));
c.push(P('**8. Human and institutional factors.** It does not represent whether residents will comply with an evacuation order, who is elderly or needs assistance, whether communication works, who has legal authority to order what, or how long a pump takes to arrive. Much of an experienced officer\'s judgment is tacit and context-dependent and was never written down as rules, so the 12 rules are a simplification that should support, not replace, a duty officer.'));
c.push(P('**9. Data quality and my own assumptions.** All numbers here are invented samples; thresholds and depth limits (0.30 m, 0.15 m) are plausible but unvalidated. Tidal effects from the Bay of Bengal, which strongly affect Chennai drainage, are absent. The knowledge base is only as good as the data and the review process of Task 11.'));

// ---------------- Appendix
c.push(H1('Appendix. Submitted files and how to reproduce'));
c.push(table(['File', 'Purpose'], [
  ['ontology/flood_ontology.owl, .ttl', 'The ontology (RDF/XML and Turtle) - Tasks 1 to 3'],
  ['build_ontology.py', 'Builds the ontology; with `--fault N` builds the seeded-fault test files'],
  ['ontology/test_fault1.owl ... test_fault3.owl', 'Seeded-fault ontologies used in Task 10'],
  ['ontology/inspect_ontology.py, inheritance_check.py', 'Summary and inheritance checks (Tasks 3 and 5)'],
  ['sparql/cq1.rq, cq2.rq, cq3.rq, run_queries.py', 'Competency questions and runner (Task 6)'],
  ['rules/flood_rules.txt, flood_rules.py', 'Twelve rules in plain text and the executable rule engine (Tasks 7, 8)'],
  ['reasoner/run_reasoner.py, verify_dl_rules.py', 'HermiT tests (Tasks 9, 10); outputs in reasoner_output.txt, dl_rules_output.txt'],
  ['diagrams/make_diagrams.py, make_screenshots.py', 'Regenerate figures and screenshots'],
  ['screenshots/*.png', 'All figures and screenshots used in this report'],
], [4200, 5438], { zebra: true, size: 18 }));
c.push(gap());
c.push(P('To reproduce: `pip install rdflib owlready2 graphviz pillow`, install Java and Graphviz, then run `python build_ontology.py`, `python sparql/run_queries.py`, `python rules/flood_rules.py`, `python reasoner/run_reasoner.py all`.'));

const doc = new Document({
  creator: 'KEDS Assignment 1', title: 'KEDS Assignment 1 - Flood-Response Knowledge Base',
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 30, bold: true, color: '1F3864' }, paragraph: { spacing: { before: 360, after: 140 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 25, bold: true, color: '2F5496' }, paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ] },
  numbering: { config: [
    { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '\u2022', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: 'num', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
    { reference: 'num2', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] },
  ] },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'KEDS Assignment 1 (CO1)  |  Page ', size: 18, font: FONT, color: '777777' }), new TextRun({ children: [PageNumber.CURRENT], size: 18, font: FONT, color: '777777' })] })] }) },
    children: c }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(path.join(__dirname, 'Assignment1_KEDS_Report.docx'), b); console.log('ok'); });
