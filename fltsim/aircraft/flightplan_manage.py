from __future__ import annotations
from .acft_data import FPLPhase


def dispatch_next_fpl(fpl_data, now: int) -> bool:
    if fpl_data.curFPL or fpl_data.curFPLPhase != FPLPhase.Schedule or fpl_data.scheduledFPL is None:
        return False

    nextFPL = fpl_data.scheduledFPL
    if nextFPL.startTime > now:
        return False

    fpl_data.scheduledFPL = None
    fpl_data.curFPL = nextFPL
    fpl_data.curFPLPhase = FPLPhase.EnRoute
    return True


# KannSei
def update_fplphase(fpl_data, profile):
    if not fpl_data.curFPL:
        return
    if not profile.target:
        fpl_data.curFPL = None
        fpl_data.curFPLPhase = FPLPhase.Finished
