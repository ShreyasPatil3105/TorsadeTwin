# Hill pore-block + combination rules (§5.4, §5.5). Prior art, cited everywhere it appears.
# block fraction  b = 1/(1+(IC50/C)^h); unblocked fraction f = 1/(1+(C/IC50)^h).
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class BlockResult:
    block: dict[str, float]          # channel -> fraction blocked (0..1)
    unblocked: dict[str, float]      # channel -> fraction unblocked F_c (0..1]
    partial_panel: list[str]         # channels with NA data (zero block)
    combo_rule: str


def hill_unblocked_fraction(c_free_nM: float, ic50_nM: float, hill: float) -> float:
    """f = 1/(1+(C/IC50)^h); f in (0,1]; b = 0.5 at C = IC50 for h = 1."""
    if c_free_nM <= 0:
        return 1.0
    if ic50_nM <= 0:
        return 1.0
    ratio = c_free_nM / ic50_nM
    return 1.0 / (1.0 + ratio**hill)


def hill_block_fraction(c_free_nM: float, ic50_nM: float, hill: float) -> float:
    return 1.0 - hill_unblocked_fraction(c_free_nM, ic50_nM, hill)


def combine_indep_mult(unblocked_by_drug: list[dict[str, float]]) -> dict[str, float]:
    """F_c = PRODUCT over drugs of f_{d,c} (COMBO_RULE_INDEP_MULT_v1)."""
    channels: set[str] = set()
    for d in unblocked_by_drug:
        channels.update(d.keys())
    out: dict[str, float] = {}
    for c in channels:
        prod = 1.0
        for d in unblocked_by_drug:
            prod *= d.get(c, 1.0)
        out[c] = prod
    return out


def combine_additive_occ(block_by_drug: list[dict[str, float]]) -> dict[str, float]:
    """b_c = min(1, sum_d b_{d,c}) (COMBO_RULE_ADDITIVE_OCC_v1, sensitivity variant only)."""
    channels: set[str] = set()
    for d in block_by_drug:
        channels.update(d.keys())
    out: dict[str, float] = {}
    for c in channels:
        total = sum(d.get(c, 0.0) for d in block_by_drug)
        out[c] = 1.0 - min(1.0, total)
    return out


def compute_block(registry, drugs: list[tuple[str, float]]) -> BlockResult:
    """Compute per-channel block for the declared drug exposures.

    drugs: list of (drug_id, c_free_nM).
    """
    unblocked_by_drug: list[dict[str, float]] = []
    block_by_drug: list[dict[str, float]] = []
    partial: set[str] = set()
    for drug_id, c_free in drugs:
        rec = registry.get(drug_id)
        unblocked: dict[str, float] = {}
        block: dict[str, float] = {}
        for ch in rec.channels:
            if ch.runtime_excluded:
                partial.add(ch.channel)
                unblocked[ch.channel] = 1.0
                block[ch.channel] = 0.0
                continue
            f = hill_unblocked_fraction(c_free, ch.ic50_nM, ch.hill)
            unblocked[ch.channel] = f
            block[ch.channel] = 1.0 - f
        unblocked_by_drug.append(unblocked)
        block_by_drug.append(block)
    if not unblocked_by_drug:
        return BlockResult(block={}, unblocked={}, partial_panel=[], combo_rule="indep_mult")
    F = combine_indep_mult(unblocked_by_drug)
    B = {c: 1.0 - F[c] for c in F}
    return BlockResult(block=B, unblocked=F, partial_panel=sorted(partial), combo_rule="indep_mult")


def compute_block_alt(registry, drugs: list[tuple[str, float]]) -> dict[str, float]:
    """Additive-occupancy variant for the audit panel (§5.5)."""
    block_by_drug: list[dict[str, float]] = []
    for drug_id, c_free in drugs:
        rec = registry.get(drug_id)
        block: dict[str, float] = {}
        for ch in rec.channels:
            if ch.runtime_excluded:
                block[ch.channel] = 0.0
            else:
                block[ch.channel] = hill_block_fraction(c_free, ch.ic50_nM, ch.hill)
        block_by_drug.append(block)
    return combine_additive_occ(block_by_drug)
