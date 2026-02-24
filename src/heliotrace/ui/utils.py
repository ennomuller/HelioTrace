"""
Shared UI utility helpers used across Streamlit pages and components.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional


def format_diff(sim_time: Optional[datetime], ref_time: Optional[datetime]) -> Optional[str]:
    """
    Format the signed difference between a simulated arrival and a reference time.

    :param sim_time: Simulated arrival datetime, or ``None``.
    :param ref_time: Reference (observed/expected) datetime, or ``None``.
    :return: Signed string like ``"+2.35 h"`` or ``"-1.10 h"``,
             or ``None`` if either input is missing.
    """
    if sim_time is None or ref_time is None:
        return None
    diff_h = (sim_time - ref_time).total_seconds() / 3600.0
    return f"{diff_h:+.2f} h"
