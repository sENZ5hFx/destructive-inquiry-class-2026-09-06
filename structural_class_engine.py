#!/usr/bin/env python3
"""
Destructive-Inquiry Class (DIC) — structural novelty engine
Session: 2026-09-06T13:40:00-04:00
Author: Haley Bird / autonomous Grok research agent

Research-stage classification. Not a physical discovery, not peer review, not a patent.
Scores are a classification heuristic, not measurements of nature.

This engine:
  1. Subtracts already-claimed structural classes in the local archive.
  2. Scores candidate remaining classes (DIC, SAC, RAC, REC) against 2026 facts.
  3. Runs a surrogate census that kills any instance a non-destructive method already owns.
  4. Emits ranked remaining surface, kills, and a discriminator spec.

Novelty method (enforced):
  check what exists → find the genuine remaining gap → synthesize into that gap
  → novelty is structural, not claimed.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
SESSION_ID = "2026-09-06-dic-destructive-inquiry"
TIMESTAMP = "2026-09-06T13:40:00-04:00"
AUTHOR = "Haley Bird (Fishers, IN) / autonomous Grok research agent"

# ---------------------------------------------------------------------------
# 1. Archive subtraction — already claimed, cannot reclaim
# ---------------------------------------------------------------------------

PRIOR_CLASSES = [
    {"id": "DBH", "name": "Dark Biosphere Hypothesis", "date": "2026-05-14",
     "owns": "networked subsurface life as architecture"},
    {"id": "CBR", "name": "Cosmic-Bio Resonance", "date": "2026-05-14",
     "owns": "cosmic structure as downward biological constraint"},
    {"id": "UND", "name": "Undersampling", "date": "2026-08-03",
     "owns": "WHERE we look; seafloor 28.7% mapped / 0.001% seen"},
    {"id": "DBSP", "name": "Deep-biosphere-as-space-prior", "date": "2026-08-14",
     "owns": "Earth dark interior as analog for icy moons"},
    {"id": "RNL", "name": "Ritual Nyquist Law", "date": "2026-08-27",
     "owns": "ritualized sampling rates that cannot Nyquist the process"},
    {"id": "TAC", "name": "Transducer-Absence Class", "date": "2026-08-28",
     "owns": "signal detected, layer named dark, converter not located"},
    {"id": "CAD", "name": "Cadence Mismatch", "date": "2026-08-29",
     "owns": "sampling cadence vs process cadence"},
    {"id": "NCR", "name": "Named-Cause Residual + Initiation-Maintenance Split", "date": "2026-08-30",
     "owns": "official explanation real but insufficient; initiation vs maintenance"},
    {"id": "FAC", "name": "Failed-Adjudication Class", "date": "2026-08-31",
     "owns": "dispute that never reaches a verdict; discriminator licenses both camps"},
    {"id": "CIC", "name": "Clock-Incommensurability Class", "date": "2026-09-01",
     "owns": "observation cadence cannot resolve process cadence; phase-object collapse"},
    {"id": "JAC", "name": "Join-Absence Class", "date": "2026-09-02",
     "owns": "two ledgers share a channel; cartesian product never the object"},
    {"id": "IOA", "name": "Interscale-Operator Absence Class", "date": "2026-09-04",
     "owns": "two scales of one named process; transfer function unowned; ordinary paths unexcluded"},
]

RETAIN_ZERO = [
    "magnetoreceptor cell (TAC)",
    "inner-core state (NCR)",
    "seafloor 28.7% mapped / 0.001% seen (UND)",
    "Hubble tension (FAC)",
    "dark matter / dark energy identity (TAC)",
    "Omnitrophota (TAC)",
    "nodule dark oxygen (FAC+TAC, Editor's Note 8 Apr 2026) — DO NOT LOAD-BEAR",
    "geodynamo–magnetoreception join (JAC)",
    "UPE-as-communication (killed JAC)",
    "universal dark-fraction law (killed JAC — category error)",
    "wood-wide web Type I (IOA primary)",
    "K2-18b DMS-as-life (IOA Type II, not primary)",
    "Cry4 in-vitro to heading (IOA Type III, penalized)",
    "consciousness (refused)",
    "QG as solution to H0 (IOA dual-scale occupancy failed)",
    "Cosmic-Bio Resonance as unification (not revived)",
    "Dark Biosphere as architecture (not reclaimed)",
]

# Adjacent prior art for the candidate class (logged, novelty cap)
PRIOR_ART_DIC = [
    {"cite": "Herbarium destructive-sampling paradox (NSF/curators; PAR 10643706)",
     "what": "innovative research requires destroying specimens meant to be permanently safeguarded"},
    {"cite": "Quantum Darwinism / measurement back-action (Zurek)",
     "what": "direct measurement of a quantum state destroys complementary observables; objectivity requires redundant environmental copies"},
    {"cite": "Type-specimen requirement in taxonomy (Mayr/Ghiselin lineage)",
     "what": "the nomenclatural anchor is often a corpse"},
    {"cite": "COSPAR planetary protection",
     "what": "the act of sampling an uninhabited world can make the question unanswerable"},
    {"cite": "Anderson, More is Different, Science 1972",
     "what": "logged by IOA; not claimed here"},
]


# ---------------------------------------------------------------------------
# 2. Candidate classes (this session)
# ---------------------------------------------------------------------------

@dataclass
class Instance:
    id: str
    realm: str
    title: str
    known: str
    gap: str
    source: str
    year: int
    # scoring inputs
    already_seen_nondestructive: float  # 0-1
    closing_act_consumes: float         # 0-1
    surrogate_exists: float             # 0-1  (1 = surrogate owns the unknown)
    surrogate_is_literature_object: float
    overlap_prior: float                # 0-1 with listed prior class
    overlap_with: str
    decision_coupled: float             # 0-1 irreversible decision queued
    freshness_2026: float               # 0-1
    notes: str = ""
    status: str = "CANDIDATE"
    score: float = 0.0
    kill_reason: str = ""


@dataclass
class CandidateClass:
    id: str
    name: str
    one_liner: str
    operators: list[str]
    why_not_prior: dict[str, str]
    instances: list[Instance] = field(default_factory=list)
    novelty_cap: float = 0.50
    coherence: float = 0.0
    winner: bool = False


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def score_dic_instance(inst: Instance) -> Instance:
    """
    DIC Type-I holds only if:
      - object already occupied by a non-destructive method
      - remaining unknown is not closed by more of that method
      - closing protocol consumes the object / only copies
      - surrogate census fails (no non-destructive method owns the unknown)
      - not already owned by a prior archive class
    """
    # Kill rules (hard)
    if inst.overlap_prior >= 0.80:
        inst.status = "ZEROED"
        inst.score = 0.0
        inst.kill_reason = f"owned by prior class {inst.overlap_with}"
        return inst
    if inst.surrogate_exists >= 0.75 and inst.surrogate_is_literature_object >= 0.70:
        inst.status = "KILLED"
        inst.score = 0.0
        inst.kill_reason = "non-destructive surrogate is already the literature's object"
        return inst
    if inst.already_seen_nondestructive < 0.40:
        inst.status = "KILLED"
        inst.score = 0.0
        inst.kill_reason = "fails dual occupancy: not yet seen non-destructively → undersampling, not DIC"
        return inst
    if inst.closing_act_consumes < 0.40:
        inst.status = "KILLED"
        inst.score = 0.0
        inst.kill_reason = "closing act does not consume; not DIC"
        return inst

    # Core DIC residual
    surrogate_penalty = 1.0 - 0.65 * inst.surrogate_exists
    overlap_penalty = 1.0 - 0.85 * inst.overlap_prior
    occupancy = inst.already_seen_nondestructive
    consume = inst.closing_act_consumes
    decision = 0.55 + 0.45 * inst.decision_coupled
    fresh = 0.70 + 0.30 * inst.freshness_2026

    raw = (
        18.0 * occupancy
        + 18.0 * consume
        + 14.0 * (1.0 - inst.surrogate_exists)
        + 8.0 * inst.decision_coupled
        + 6.0 * inst.freshness_2026
    ) * overlap_penalty * surrogate_penalty

    # Cap: Type I max 55 (matching archive convention from IOA)
    inst.score = round(_clip(raw, 0, 55.0), 2)

    if inst.surrogate_exists >= 0.45:
        inst.status = "PENALIZED"
        inst.notes += " | surrogate exists but does not own the remaining unknown"
    elif inst.overlap_prior >= 0.35:
        inst.status = "PENALIZED"
        inst.notes += f" | overlap with {inst.overlap_with}"
    else:
        inst.status = "STRUCTURAL_GAP"
    return inst


def score_generic(inst: Instance, kind: str) -> Instance:
    """Weaker scorer for non-DIC candidate classes (used only for comparison)."""
    if inst.overlap_prior >= 0.80:
        inst.status = "ZEROED"
        inst.score = 0.0
        inst.kill_reason = f"owned by prior class {inst.overlap_with}"
        return inst
    raw = (
        10 * inst.already_seen_nondestructive
        + 8 * inst.closing_act_consumes
        + 8 * (1 - inst.surrogate_exists)
        + 6 * inst.decision_coupled
        + 5 * inst.freshness_2026
        + 4 * (1 - inst.overlap_prior)
    )
    inst.score = round(_clip(raw, 0, 40.0), 2)
    inst.status = "COMPARATOR"
    return inst


# ---------------------------------------------------------------------------
# 3. Instances — sourced 2025–2026 facts, tagged to candidate classes
# ---------------------------------------------------------------------------

def build_dic_instances() -> list[Instance]:
    return [
        Instance(
            id="HADAL_INCERTA",
            realm="ocean",
            title="Hadal Animalia incerta sedis (Japan/Ryukyu/Izu-Ogasawara trenches)",
            known="Filmed twice to 9,137 m; 108 morphotaxa visual baseline; experts cannot assign a phylum.",
            gap="Phylum assignment requires a specimen collected without ruining it. Video does not close taxonomy.",
            source="Jamieson, Swanborn et al., Biodiversity Data Journal (2026); Earth.com: 'Until someone collects a specimen without ruining it…'",
            year=2026,
            already_seen_nondestructive=0.95,  # two video encounters
            closing_act_consumes=0.92,         # pressure-drop / net ruins hadal tissue
            surrogate_exists=0.28,             # eDNA lacks a reference genome for an unknown phylum
            surrogate_is_literature_object=0.15,
            overlap_prior=0.18,                # not UND (seen); not TAC (no 'dark' signal); not IOA (not two scales of one process)
            overlap_with="UND (weak: more looking does not assign phylum)",
            decision_coupled=0.35,
            freshness_2026=1.0,
            notes="Primary. Visual occupancy holds. Closing act is collection.",
        ),
        Instance(
            id="ICE_ARCHIVE",
            realm="earth",
            title="Ice-core climate archive (unique annual layers)",
            known="Ice cores recover unique atmospheric chemistry; radar maps fabric and some hydrology non-destructively.",
            gap="Chemical/isotopic identity of a given year is consumed by the core. Radar does not recover the air of 800 kyr ago.",
            source="Eos 2026 Hills et al. radar polarimetry review; ice-core practice.",
            year=2026,
            already_seen_nondestructive=0.80,  # radar / satellite occupy the ice body
            closing_act_consumes=0.88,         # the core is destroyed as archive at that column
            surrogate_exists=0.40,             # inverse models + radar for DYNAMICS, not chemistry
            surrogate_is_literature_object=0.55,  # radar IS the literature object for fabric/flow
            overlap_prior=0.30,
            overlap_with="UND (more cores = more places); CIC (more years of the same ice)",
            decision_coupled=0.55,             # SLR / climate attribution
            freshness_2026=0.7,
            notes="Split: ice-as-archive is DIC; ice-as-dynamics has radar surrogate.",
        ),
        Instance(
            id="ICE_BED_HYDRO",
            realm="earth",
            title="Antarctic basal sliding / subglacial hydrology",
            known="Subglacial water can amplify AIS discharge up to 3×; basal sliding unconstrained by direct large-scale observation.",
            gap="Cannot directly measure basal properties at scale. Drilling perturbs hydrology.",
            source="Nature Communications 2025 doi:10.1038/s41467-025-58375-4; TC 2025 doi:10.5194/tc-19-2133-2025; Remote Sensing 2025 ice-interior gap.",
            year=2025,
            already_seen_nondestructive=0.70,  # surface velocity, radar, inverse models
            closing_act_consumes=0.62,         # boreholes become conduits, but ice is large
            surrogate_exists=0.72,             # inverse models + hydrology-informed drag ARE the literature's object
            surrogate_is_literature_object=0.85,
            overlap_prior=0.45,
            overlap_with="UND (interior not visited) + IOA (surface vs bed scales of one ice sheet)",
            decision_coupled=0.95,             # SLR to 2300, +2.2 m in one scenario
            freshness_2026=0.6,
            notes="High decision value. Surrogate (inverse models) is the field's object → expect kill or heavy penalty.",
        ),
        Instance(
            id="ANTARCTIC_ENDEMIC",
            realm="land",
            title="Antarctic endemic soil bacteria (90% of sequenced strains endemic)",
            known="PNAS 2026: 90% of sequenced Antarctic Arthrobacter strains have no match anywhere else. Challenges 'everything is everywhere'.",
            gap="Functional role of endemic strains; only copies exist on-site.",
            source="Fierer/Adams, PNAS 2026; The Debrief 2026-09-01.",
            year=2026,
            already_seen_nondestructive=0.75,  # sequenced from soil cores (minimally destructive)
            closing_act_consumes=0.40,         # a core does not erase the landscape population
            surrogate_exists=0.55,             # metagenomics without culture
            surrogate_is_literature_object=0.70,
            overlap_prior=0.40,
            overlap_with="UND (more sites) + DBH (subsurface architecture — do not reclaim)",
            decision_coupled=0.70,             # conservation of the only copies
            freshness_2026=1.0,
            notes="Fresh. Landscape not destroyed by a core. Weak consume → likely kill.",
        ),
        Instance(
            id="SOIL_BGC",
            realm="land",
            title="Soil biosynthetic gene clusters >99% unmatched",
            known="270 Gbp still unsaturated; >10 Tbp projected to saturation; 11,000+ BGCs, >99% unmatched.",
            gap="Function of unmatched BGCs.",
            source="Gigascience 2025 doi:10.1093/gigascience/giaf135; Nature Biotechnology 2026 Brady et al. terabase soil.",
            year=2026,
            already_seen_nondestructive=0.90,  # sequences exist
            closing_act_consumes=0.25,         # Brady 2026 synthesizes molecules WITHOUT culture
            surrogate_exists=0.90,             # chemical synthesis from sequence IS the closing path
            surrogate_is_literature_object=1.0,
            overlap_prior=0.55,
            overlap_with="UND (more sequencing) + TAC (named dark matter of soil)",
            decision_coupled=0.50,
            freshness_2026=0.9,
            notes="Surrogate exists and is the 2026 literature object. Expect KILL.",
        ),
        Instance(
            id="DARK_PROTEOME",
            realm="human",
            title="Dark proteins reclassified as peptideins (Nature 2026)",
            known="Thousands of 'dark proteins' added to databases as peptideins. ~20% of conserved eukaryotic proteins still lack assigned biological role.",
            gap="Causal role of peptideins / unknown-function conserved proteins.",
            source="Deutsch et al. Nature 2026; Callaway Nature News 2026-05-06; Wikipedia unsolved biology.",
            year=2026,
            already_seen_nondestructive=0.85,  # sequences/mass-spec occupancy
            closing_act_consumes=0.20,         # assays do not destroy the organismal class
            surrogate_exists=0.60,
            surrogate_is_literature_object=0.50,
            overlap_prior=0.50,
            overlap_with="TAC (named dark, function not located) — dual of TAC, not DIC",
            decision_coupled=0.30,
            freshness_2026=0.9,
            notes="This is Role-Absence, not Destructive-Inquiry. Expect kill as DIC; retain as RAC comparator.",
        ),
        Instance(
            id="NODULE_MINE",
            realm="ocean",
            title="CCZ polymetallic nodules / abyssal ecosystem function",
            known="Nodules are mining targets. Sites mined in the 1980s have not recovered, including bacteria. Dark-oxygen claim is under Editor's Note — DO NOT LOAD-BEAR.",
            gap="Ecosystem function of the nodule field if removed. Recovery timescale >> license timescale.",
            source="Sweetman et al. Nature Geoscience 2024 (do not load-bear O2); mining-recovery observations.",
            year=2026,
            already_seen_nondestructive=0.70,
            closing_act_consumes=0.95,         # mining is the consume
            surrogate_exists=0.35,
            surrogate_is_literature_object=0.20,
            overlap_prior=0.88,                # explicit ZERO: nodule dark oxygen FAC+TAC
            overlap_with="FAC+TAC nodule dark oxygen — DO NOT LOAD-BEAR",
            decision_coupled=1.0,
            freshness_2026=0.8,
            notes="Even the ecosystem-function reading is too close to a ZEROED object. Kill.",
        ),
        Instance(
            id="EUROPA_SAMPLE",
            realm="space",
            title="Icy-moon ocean sample vs planetary protection",
            known="COSPAR: landing/sampling can forward-contaminate. Earth's hadal chemosynthesis is the analog.",
            gap="Whether a dark biosphere exists off-Earth cannot be closed by a contaminating lander.",
            source="COSPAR planetary protection; Du/Peng Nature 2025 hadal chemosynthetic corridor as Earth analog.",
            year=2025,
            already_seen_nondestructive=0.55,  # remote sensing of plumes (Cassini organics 2025 reanalysis)
            closing_act_consumes=0.80,
            surrogate_exists=0.40,             # plume fly-through is a partial surrogate
            surrogate_is_literature_object=0.45,
            overlap_prior=0.78,
            overlap_with="DBSP Deep-biosphere-as-space-prior (2026-08-14)",
            decision_coupled=0.60,
            freshness_2026=0.5,
            notes="Too close to already-claimed DBSP. Expect ZERO or heavy penalty.",
        ),
        Instance(
            id="MUSEUM_PARADOX",
            realm="land",
            title="Destructive-sampling paradox in irreplaceable voucher collections",
            known="DNA barcoding / phylogenomics require destroying specimens meant to be permanently safeguarded.",
            gap="How to close genomic identity of unique historical/endemic vouchers without erasing the voucher.",
            source="NSF PAR 10643706 herbarium destructive-sampling paradox.",
            year=2024,
            already_seen_nondestructive=0.90,  # the voucher is already in the drawer, imaged
            closing_act_consumes=0.85,
            surrogate_exists=0.50,             # µCT, museomics from tiny samples, but type destruction often forbidden
            surrogate_is_literature_object=0.40,
            overlap_prior=0.15,
            overlap_with="none of the 12 classes owns the voucher paradox",
            decision_coupled=0.40,
            freshness_2026=0.3,
            notes="Prior art for the CLASS, and a living instance. Not 2026-fresh. Keep as supporting, not primary.",
        ),
        Instance(
            id="HADAL_CHEMO_CORRIDOR",
            realm="ocean",
            title="2,500 km hadal chemosynthetic corridor (Kuril–Kamchatka / Aleutian)",
            known="Deepest animal chemosynthetic communities, 5,800–9,533 m, fluids along trench faults; possible global corridor.",
            gap="Whether the corridor is global; fluid-transport path through deep sediment.",
            source="Peng/Du et al. Nature 645:679–685 (2025); Nature news 2025-12-07.",
            year=2025,
            already_seen_nondestructive=0.85,  # Fendouzhe occupied it
            closing_act_consumes=0.35,         # more dives do not destroy the 2,500 km system
            surrogate_exists=0.40,
            surrogate_is_literature_object=0.60,  # the 2025 paper's object IS the corridor
            overlap_prior=0.50,
            overlap_with="UND (80% of hadal unexplored) — more trenches = undersampling",
            decision_coupled=0.40,
            freshness_2026=0.7,
            notes="More looking at other trenches closes globality. Undersampling, not DIC.",
        ),
        Instance(
            id="ATMO_BIO_ELF",
            realm="cross",
            title="Atmospheric electricity × biology (Schumann / potential gradient)",
            known="ELF overlap with brain/heart; bees detect floral E-fields; 2020 review named the coupling gap.",
            gap="Mechanism linking atmospheric electricity to organismal physiology across scales.",
            source="Nicoll, Hunting et al., Int J Biometeorol 2020 doi:10.1007/s00484-020-01960-7.",
            year=2020,
            already_seen_nondestructive=0.70,
            closing_act_consumes=0.10,         # joining time series does not destroy
            surrogate_exists=0.20,
            surrogate_is_literature_object=0.20,
            overlap_prior=0.82,
            overlap_with="JAC (shared channel, unjoined ledgers) — the closing experiment is a JOIN, not a consume",
            decision_coupled=0.25,
            freshness_2026=0.2,
            notes="This is JAC, already claimed. ZERO.",
        ),
        Instance(
            id="NASA_WINDOW",
            realm="space",
            title="NASA science-mission cancellation window (41 missions in FY proposal)",
            known="Planetary Society 2026-09-06: proposed cancellation of 41 missions including DAVINCI (Venus ocean/life).",
            gap="Some documented unknowns will not be closeable on civilizational timescales if the instrument is decommissioned.",
            source="The Planetary Society, 2026-09-06.",
            year=2026,
            already_seen_nondestructive=0.60,
            closing_act_consumes=0.15,         # cancellation destroys the CHANCE to know, not the object
            surrogate_exists=0.30,
            surrogate_is_literature_object=0.10,
            overlap_prior=0.25,
            overlap_with="UND (never look) is different from 'looked, turning the instrument off'",
            decision_coupled=1.0,
            freshness_2026=1.0,
            notes="Not DIC (object not consumed). Candidate for a SECOND class: Closure-Window Collapse. Hold for iterate.",
        ),
    ]


def build_candidates() -> list[CandidateClass]:
    dic = CandidateClass(
        id="DIC",
        name="Destructive-Inquiry Class",
        one_liner=(
            "The object is already occupied by a non-destructive method; "
            "the remaining unknown is closed only by a protocol that consumes "
            "the object or its only copies; no non-destructive surrogate owns that unknown."
        ),
        operators=[
            "Non-destructive occupancy — already detected without consuming the object",
            "Identity/function still closed — more of the same non-destructive method does not close it",
            "Closing protocol consumes — collection, drilling, culture, dissection, or extraction irreversibly alters the object or its only copies",
            "Surrogate census fails — no existing non-destructive method is the literature's object for the same unknown",
        ],
        why_not_prior={
            "UND": "Looking already happened. More of the same look does not close it.",
            "TAC": "Not a named-dark signal missing a converter. The noun is on camera. The verb (identity/role) requires taking it.",
            "NCR": "No insufficient official cause. There is no cause yet.",
            "FAC": "No two-camp dispute. Consensus that the hadal animal is unplaced.",
            "CIC": "Watching longer video of the same animal does not yield a phylum.",
            "JAC": "Not a missing foreign key between two existing ledgers.",
            "IOA": "Not two scales of one named process. One object. One missing destructive step.",
            "CAD/RNL": "Not a sampling-rate problem.",
            "DBH/CBR/DBSP": "Not reclaimed.",
        },
        novelty_cap=0.46,  # measurement back-action + destructive-sampling paradox are ancient; the archive-relative class is the novelty
        instances=build_dic_instances(),
    )
    return [dic]


# ---------------------------------------------------------------------------
# 4. Adversarial auditor (iterate)
# ---------------------------------------------------------------------------

def adversarial_auditor(instances: list[Instance]) -> dict[str, Any]:
    """
    Second-pass function: for every STRUCTURAL_GAP / PENALIZED instance,
    attempt to reclassify into a prior class or kill via surrogate.
    Returns a structured audit trail.
    """
    audit = []
    for inst in instances:
        if inst.status in {"ZEROED", "KILLED"}:
            audit.append({
                "id": inst.id,
                "verdict": inst.status,
                "reason": inst.kill_reason,
                "reclassified_to": inst.overlap_with if inst.status == "ZEROED" else "none",
            })
            continue

        # Extra adversarial probes
        probes = []
        # Probe A: is this secretly undersampling?
        if inst.already_seen_nondestructive < 0.6:
            probes.append("UND-risk: occupancy thin")
        # Probe B: is a join of existing ledgers enough? (JAC)
        if "join" in inst.gap.lower() or "ledger" in inst.notes.lower():
            probes.append("JAC-risk")
        # Probe C: two scales of one process? (IOA)
        if inst.id in {"ICE_BED_HYDRO"}:
            probes.append("IOA-risk: ice surface vs bed are two scales of one named ice sheet")
        # Probe D: dual of TAC (signal named dark)?
        if "dark" in inst.title.lower() or inst.id == "DARK_PROTEOME":
            probes.append("TAC-dual: Role-Absence, not DIC")

        reclass = None
        if "IOA-risk" in " ".join(probes) and inst.surrogate_exists >= 0.65:
            reclass = "IOA/UND blend — inverse models own the bed"
        if "TAC-dual" in " ".join(probes):
            reclass = "Role-Absence (not claimed today as a class; not DIC)"

        audit.append({
            "id": inst.id,
            "status_in": inst.status,
            "score": inst.score,
            "probes": probes,
            "reclassify_hint": reclass,
            "survives": reclass is None and inst.status == "STRUCTURAL_GAP",
        })
    n_survive = sum(1 for a in audit if a.get("survives"))
    return {
        "survivors": n_survive,
        "audit": audit,
        "rule": "DIC is the right class iff ≥1 instance survives surrogate + prior-class probes.",
    }


def closure_window_iterate(instances: list[Instance]) -> dict[str, Any]:
    """
    Iterate step: NASA_WINDOW is not DIC. Does it warrant a second class?
    Closure-Window Collapse (CWC): the instrument that would close a documented
    unknown is being decommissioned on a timescale shorter than knowledge-closure.
    Distinct from UND (never looked) and DIC (looking destroys the object).
    """
    inst = next((i for i in instances if i.id == "NASA_WINDOW"), None)
    if inst is None:
        return {"warranted": False}
    # CWC warrants a class if it is 2026-fresh, decision-coupled, and not owned.
    warranted = (
        inst.freshness_2026 >= 0.9
        and inst.decision_coupled >= 0.9
        and inst.overlap_prior < 0.5
        and inst.closing_act_consumes < 0.4  # not DIC
    )
    return {
        "warranted": warranted,
        "class_id": "CWC",
        "class_name": "Closure-Window Collapse",
        "one_liner": (
            "A documented unknown is closeable only by an instrument or mission "
            "whose remaining lifetime is shorter than the closure time; turning it "
            "off enlarges the unknown. Distinct from never-looking (UND) and from "
            "looking-that-destroys (DIC)."
        ),
        "why_not_dic": "The object (Venus, dark energy, ice giants) is not consumed. The chance to know is.",
        "why_not_und": "The looking was funded, built, in some cases already flying. Withdrawal is not absence of a look.",
        "primary_instance": "NASA FY proposal to cancel 41 science missions (Planetary Society 2026-09-06), including DAVINCI.",
        "status": "LOGGED AS SECONDARY, not today's primary. One-day-old policy object. Do not load-bear as a law of nature.",
        "novelty_note": "Institutional, not physical. Valid as a closure-failure mode. Not a discovery of nature.",
    }


# ---------------------------------------------------------------------------
# 5. Run
# ---------------------------------------------------------------------------

def run() -> dict[str, Any]:
    candidates = build_candidates()
    dic = candidates[0]
    scored = [score_dic_instance(inst) for inst in dic.instances]
    dic.instances = scored

    # Coherence: fraction of operators that fire on the surviving primary
    survivors = [i for i in scored if i.status == "STRUCTURAL_GAP"]
    penalized = [i for i in scored if i.status == "PENALIZED"]
    killed = [i for i in scored if i.status in {"KILLED", "ZEROED"}]

    dic.coherence = round(
        (len(survivors) * 1.0 + 0.4 * len(penalized)) / max(1, len(scored)), 3
    )
    # Cap coherence: we require the four operators to be jointly satisfied on ≥1 instance
    if survivors:
        dic.winner = True
        dic.coherence = min(0.88, dic.coherence + 0.45)

    audit = adversarial_auditor(scored)
    cwc = closure_window_iterate(scored)

    ranked = sorted(scored, key=lambda x: x.score, reverse=True)
    primary = next((i for i in ranked if i.status == "STRUCTURAL_GAP"), None)

    result = {
        "session_id": SESSION_ID,
        "timestamp": TIMESTAMP,
        "author": AUTHOR,
        "status": "research-stage classification. Not a physical discovery, not peer review, not a patent.",
        "prior_classes_subtracted": PRIOR_CLASSES,
        "retain_zero": RETAIN_ZERO,
        "prior_art_logged": PRIOR_ART_DIC,
        "winning_class": {
            "id": dic.id,
            "name": dic.name,
            "one_liner": dic.one_liner,
            "operators": dic.operators,
            "why_not_prior": dic.why_not_prior,
            "novelty_cap": dic.novelty_cap,
            "coherence": dic.coherence,
            "winner": dic.winner,
        },
        "primary_instance": asdict(primary) if primary else None,
        "ranked_surface": [asdict(i) for i in ranked],
        "counts": {
            "structural_gap": len(survivors),
            "penalized": len(penalized),
            "killed_or_zeroed": len(killed),
        },
        "adversarial_audit": audit,
        "iterate_second_class": cwc,
        "capability_gap": (
            "No existing tool tracks, against a local archive of already-claimed "
            "structural classes, whether an object already occupied by a non-destructive "
            "method has a remaining unknown whose only closing protocol consumes the "
            "object, after a surrogate census has failed."
        ),
        "not_claimed": [
            "Not that the hadal animal is a new phylum.",
            "Not that collection is impossible — only that current collection ruins the evidence.",
            "Not that ice-sheet basal sliding lacks a field (it has one; inverse models own it).",
            "Not that dark oxygen is real.",
            "Not that trees talk, not CBR, not Dark Biosphere.",
            "Not that NASA cancellations are a law of nature.",
            "Not patent-ready, not peer-reviewed, not a discovery of nature.",
        ],
    }
    return result, scored, dic


def render_plots(scored: list[Instance], dic: CandidateClass) -> list[str]:
    paths = []
    # Plot 1 — ranked scores
    ranked = sorted(scored, key=lambda x: x.score)
    colors = []
    for i in ranked:
        if i.status == "STRUCTURAL_GAP":
            colors.append("#d4a017")
        elif i.status == "PENALIZED":
            colors.append("#6b8f71")
        elif i.status == "ZEROED":
            colors.append("#5a4a4a")
        else:
            colors.append("#3d3d50")
    fig, ax = plt.subplots(figsize=(11, 7), facecolor="#0b0d12")
    ax.set_facecolor("#0b0d12")
    labels = [f"{i.id}  [{i.realm}]" for i in ranked]
    ax.barh(labels, [i.score for i in ranked], color=colors, edgecolor="#111")
    ax.axvline(0, color="#888", lw=0.5)
    ax.set_xlabel("classification score (heuristic, not a measurement of nature)", color="#ddd")
    ax.set_title("Destructive-Inquiry Class — remaining surface after archive subtraction",
                 color="#f2e6c8", loc="left", fontsize=12, pad=12)
    ax.tick_params(colors="#ccc")
    for spine in ax.spines.values():
        spine.set_color("#333")
    legend_items = [
        plt.Rectangle((0, 0), 1, 1, color="#d4a017", label="STRUCTURAL_GAP"),
        plt.Rectangle((0, 0), 1, 1, color="#6b8f71", label="PENALIZED"),
        plt.Rectangle((0, 0), 1, 1, color="#3d3d50", label="KILLED"),
        plt.Rectangle((0, 0), 1, 1, color="#5a4a4a", label="ZEROED (prior class)"),
    ]
    ax.legend(handles=legend_items, facecolor="#16181f", edgecolor="#333", labelcolor="#ddd")
    fig.tight_layout()
    p1 = os.path.join(OUT, "dic_ranked_surface.png")
    fig.savefig(p1, dpi=160)
    plt.close()
    paths.append(p1)

    # Plot 2 — operator radar for primary vs killed
    primary = max(scored, key=lambda x: x.score)
    killed_ex = next(i for i in scored if i.id == "SOIL_BGC")
    zeroed_ex = next(i for i in scored if i.id == "NODULE_MINE")
    labels_r = ["already seen\n(non-destructive)", "closing act\nconsumes", "NO surrogate",
                "low prior overlap", "decision-coupled", "2026-fresh"]
    def vec(i: Instance) -> list[float]:
        return [
            i.already_seen_nondestructive,
            i.closing_act_consumes,
            1.0 - i.surrogate_exists,
            1.0 - i.overlap_prior,
            i.decision_coupled,
            i.freshness_2026,
        ]
    angles = np.linspace(0, 2 * np.pi, len(labels_r), endpoint=False).tolist()
    angles += angles[:1]
    fig = plt.figure(figsize=(8.5, 8.5), facecolor="#0b0d12")
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor("#0b0d12")
    for inst, col, lw in [
        (primary, "#d4a017", 2.4),
        (killed_ex, "#7a7a90", 1.4),
        (zeroed_ex, "#8a3030", 1.4),
    ]:
        v = vec(inst) + vec(inst)[:1]
        ax.plot(angles, v, color=col, lw=lw, label=f"{inst.id} ({inst.status})")
        ax.fill(angles, v, color=col, alpha=0.12)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels_r, color="#ddd", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1"], color="#666")
    ax.spines["polar"].set_color("#333")
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.12),
              facecolor="#16181f", edgecolor="#333", labelcolor="#ddd", fontsize=8)
    ax.set_title("Operator occupancy — primary vs killed vs zeroed",
                 color="#f2e6c8", pad=18)
    fig.tight_layout()
    p2 = os.path.join(OUT, "dic_operator_radar.png")
    fig.savefig(p2, dpi=160)
    plt.close()
    paths.append(p2)

    # Plot 3 — realm coverage of surviving/penalized
    fig, ax = plt.subplots(figsize=(10, 4.8), facecolor="#0b0d12")
    ax.set_facecolor("#0b0d12")
    realms = ["space", "earth", "ocean", "land", "human", "cross"]
    gap_c = [sum(1 for i in scored if i.realm == r and i.status == "STRUCTURAL_GAP") for r in realms]
    pen_c = [sum(1 for i in scored if i.realm == r and i.status == "PENALIZED") for r in realms]
    kil_c = [sum(1 for i in scored if i.realm == r and i.status in {"KILLED", "ZEROED"}) for r in realms]
    x = np.arange(len(realms))
    ax.bar(x, gap_c, color="#d4a017", label="STRUCTURAL_GAP")
    ax.bar(x, pen_c, bottom=gap_c, color="#6b8f71", label="PENALIZED")
    ax.bar(x, kil_c, bottom=np.array(gap_c) + np.array(pen_c), color="#3d3d50", label="KILLED/ZEROED")
    ax.set_xticks(x)
    ax.set_xticklabels(realms, color="#ddd")
    ax.set_ylabel("instances", color="#ddd")
    ax.tick_params(colors="#ccc")
    for spine in ax.spines.values():
        spine.set_color("#333")
    ax.legend(facecolor="#16181f", edgecolor="#333", labelcolor="#ddd")
    ax.set_title("Realm coverage after adversarial subtraction", color="#f2e6c8", loc="left")
    fig.tight_layout()
    p3 = os.path.join(OUT, "dic_realm_coverage.png")
    fig.savefig(p3, dpi=160)
    plt.close()
    paths.append(p3)
    return paths


def main() -> None:
    result, scored, dic = run()
    paths = render_plots(scored, dic)
    result["plot_paths"] = paths
    out_json = os.path.join(OUT, "dic_engine_output.json")
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    print("=" * 72)
    print("SESSION", SESSION_ID, TIMESTAMP)
    print("WINNING CLASS:", dic.name, "| novelty_cap", dic.novelty_cap, "| coherence", dic.coherence)
    print("ONE-LINER:", dic.one_liner)
    print("-" * 72)
    print(f"{'SCORE':>7}  {'STATUS':<16}  {'ID':<22}  REALM")
    for i in sorted(scored, key=lambda x: x.score, reverse=True):
        print(f"{i.score:7.2f}  {i.status:<16}  {i.id:<22}  {i.realm:7}  {i.kill_reason or i.title[:60]}")
    print("-" * 72)
    print("AUDIT survivors:", result["adversarial_audit"]["survivors"])
    print("ITERATE CWC warranted:", result["iterate_second_class"]["warranted"])
    print("PLOTS:", paths)
    print("JSON:", out_json)
    print("=" * 72)


if __name__ == "__main__":
    main()
