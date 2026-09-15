# Provenance record assembly (§18.2, §18.4).
# Refuses to emit (E_PROVENANCE_INCOMPLETE) if any link in the chain is missing.
from __future__ import annotations

import datetime
import platform

from ..copy.disclaimers import DISCLAIMERS
from .errors import TorsadeTwinError


class ProvenanceBuilder:
    def __init__(self, software: dict, model: dict, solver: dict, protocol: dict,
                 config_hash: str, assumptions: list[str], boundary: dict):
        self.software = software
        self.model = model
        self.solver = solver
        self.protocol = protocol
        self.config_hash = config_hash
        self.assumptions = assumptions
        self.boundary = boundary

    def build(self, parameters: list[dict], result_hash: str, credibility: dict,
              disclaimers: list[str] | None = None) -> dict:
        # Traceability chain: every used parameter must carry DOI + VERIFIED status.
        for p in parameters:
            if not p.get("source_doi"):
                raise TorsadeTwinError(
                    "E_PROVENANCE_INCOMPLETE",
                    "A used parameter lacks source_doi; refusing to emit a report.",
                    http_status=503,
                )
            if p.get("verification_status") != "VERIFIED":
                raise TorsadeTwinError(
                    "E_PROVENANCE_INCOMPLETE",
                    f"A used parameter is not VERIFIED ({p.get('verification_status')}); refusing to emit a report.",
                    http_status=503,
                )
        if not self.model.get("artefact_sha256"):
            raise TorsadeTwinError("E_PROVENANCE_INCOMPLETE", "Model artefact hash missing.", http_status=503)
        return {
            "software": self.software,
            "model": self.model,
            "solver": self.solver,
            "protocol": self.protocol,
            "parameters": parameters,
            "assumptions": self.assumptions,
            "boundary": self.boundary,
            "config_hash": self.config_hash,
            "result_hash": result_hash,
            "credibility": credibility,
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "disclaimers": disclaimers or ["DISC_GLOBAL"],
        }


def default_software() -> dict:
    return {
        "name": "TorsadeTwin",
        "version": "0.1.0",
        "git_commit": "<sha>",
        "built_on": "<iso>",
    }


def default_solver() -> dict:
    import numpy

    return {
        "engine": "myokit.Simulation/CVODES",
        "myokit_version": "<v>",
        "sundials_version": "<v>",
        "profile": "standard",
        "rtol": 1e-8,
        "atol": 1e-10,
        "max_step_ms": 1.0,
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "scipy": "<v>",
        "platform": f"{platform.system()}/{platform.machine()}",
    }
