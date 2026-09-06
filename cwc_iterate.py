#!/usr/bin/env python3
"""
Iterate function: Closure-Window Collapse (CWC)

Triggered because NASA_WINDOW failed DIC (the object is not consumed;
the chance to know is). CWC is logged as SECONDARY — institutional,
not a law of nature. One-day-old policy object (2026-09-06).
"""

from __future__ import annotations

import json
import os
from datetime import datetime

OUT = os.path.dirname(os.path.abspath(__file__))


def closure_window_collapse(
    unknown: str,
    instrument: str,
    instrument_status: str,
    closure_years: float,
    remaining_window_years: float,
    object_consumed: bool,
    already_looked: bool,
    source: str,
) -> dict:
    """
    Classify whether a documented unknown is in Closure-Window Collapse.

    Inputs
    ------
    unknown : documented unknown (not a vibes-unknown)
    instrument : named mission/instrument that would close it
    instrument_status : flying | built | funded | proposed_cancel | cancelled
    closure_years : estimated years to close if the instrument runs
    remaining_window_years : years of instrument life remaining if not cancelled
    object_consumed : if True, this is DIC not CWC
    already_looked : if False and never funded, this is Undersampling not CWC
    source : citation

    Output
    ------
    verdict dict with class, holds (bool), why_not_prior, and a caution flag.
    """
    if not unknown or not instrument:
        raise ValueError("unknown and instrument are required")
    if object_consumed:
        return {
            "holds": False,
            "class": None,
            "reason": "object_consumed=True → Destructive-Inquiry Class, not CWC",
        }
    if not already_looked and instrument_status in {"proposed", "unfunded", "none"}:
        return {
            "holds": False,
            "class": None,
            "reason": "never looked and never funded → Undersampling, not CWC",
        }
    if remaining_window_years >= closure_years:
        return {
            "holds": False,
            "class": "CWC",
            "reason": "window still longer than closure time; CWC not yet",
        }
    status_ok = instrument_status in {"flying", "built", "funded", "proposed_cancel", "cancelled"}
    if not status_ok:
        return {"holds": False, "class": None, "reason": f"instrument_status={instrument_status} not a window"}

    ratio = remaining_window_years / max(closure_years, 1e-6)
    return {
        "holds": True,
        "class": "CWC",
        "class_name": "Closure-Window Collapse",
        "unknown": unknown,
        "instrument": instrument,
        "instrument_status": instrument_status,
        "closure_years": closure_years,
        "remaining_window_years": remaining_window_years,
        "window_to_closure_ratio": round(ratio, 3),
        "source": source,
        "why_not_UND": "The look was funded/built/flying. Withdrawal is not absence of a look.",
        "why_not_DIC": "The planetary/physical object is not consumed. The chance to know is.",
        "why_not_CIC": "Not a clock mismatch of observation vs process. The clock of the INSTITUTION is collapsing.",
        "caution": (
            "Institutional, not physical. One-day-old policy object. "
            "Do not load-bear as a law of nature. Logged as secondary."
        ),
        "status": "SECONDARY — not today's primary",
    }


def invoke_with_session_data() -> dict:
    cases = [
        closure_window_collapse(
            unknown="Whether Venus once had an ocean / could host microbial life in the atmosphere",
            instrument="DAVINCI",
            instrument_status="proposed_cancel",
            closure_years=8.0,
            remaining_window_years=0.0,
            object_consumed=False,
            already_looked=True,
            source="Planetary Society 2026-09-06; DAVINCI would be first Venus-cloud probe in ~50 years",
        ),
        closure_window_collapse(
            unknown="Dark-energy identity / Hubble-tension adjudication via wide-field imaging",
            instrument="Nancy Grace Roman Space Telescope",
            instrument_status="proposed_cancel",
            closure_years=6.0,
            remaining_window_years=0.0,
            object_consumed=False,
            already_looked=True,
            source="Planetary Society 2026-09-06; Hubble tension remains FAC in this archive — CWC is the WINDOW, not the tension",
        ),
        closure_window_collapse(
            unknown="Hadal Animalia incerta sedis phylum assignment",
            instrument="pressure-retaining hadal sampler (not yet standard)",
            instrument_status="unfunded",
            closure_years=3.0,
            remaining_window_years=10.0,
            object_consumed=True,
            already_looked=True,
            source="Jamieson 2026 — this must classify as DIC, not CWC",
        ),
    ]
    return {
        "function": "closure_window_collapse",
        "times_invoked": len(cases),
        "cases": cases,
        "n_holds": sum(1 for c in cases if c.get("holds")),
        "primary_today": "DIC, not CWC",
        "note": "CWC is the iterate gap. Logged. Not load-bearing.",
    }


if __name__ == "__main__":
    out = invoke_with_session_data()
    path = os.path.join(OUT, "cwc_iterate_output.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    print("WROTE", path)
