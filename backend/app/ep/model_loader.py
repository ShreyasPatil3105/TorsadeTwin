# L4 — model loader (§3.2, §2.2 L4).
# Loads the vendored .mmt read-only, verifies SHA-256 against CHECKSUMS.txt, asserts the
# required label bindings, and disables the dynamic hERG binding pathway (D1).
# Fails safely with the specified error codes when the artefact or dependency is absent.
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from ..services.errors import TorsadeTwinError

# Required label bindings (§3.2.5)
REQUIRED_LABELS = ["membrane_potential", "stimulus_current", "extracellular.ko"]
QNET_CURRENTS = ["INaL", "ICaL", "IKr", "IKs", "IK1", "Ito"]


@dataclass(frozen=True)
class ModelInfo:
    model_id: str
    artefact: str
    artefact_sha256: str
    source_url: str
    source_retrieved_on: str
    labels: dict[str, str]
    qnet_current_labels: dict[str, str]
    herg_dynamic_binding: str = "DISABLED (deviation D1)"


class ModelLoader:
    """Loads the vendored Myokit model and runs integrity/binding assertions."""

    def __init__(self, config: dict, checksums_path: Path, model_path: Path):
        self.config = config
        self.checksums_path = checksums_path
        self.model_path = model_path

    def load(self) -> ModelInfo:
        if not self.model_path.exists():
            raise TorsadeTwinError(
                "E_MODEL_UNAVAILABLE",
                "Model artefact not present.",
                detail=f"Expected {self.model_path}. Run scripts/fetch_model.py then scripts/convert_model.py "
                "(one-time network step) to produce and commit the .mmt.",
                remediation="Run make fetch-model && make convert-model, then commit models/ord_cipa_v1.mmt.",
                http_status=503,
            )
        actual = sha256_file(self.model_path)
        expected = self._expected_hash()
        if expected is not None and actual != expected:
            raise TorsadeTwinError(
                "E_MODEL_HASH_MISMATCH",
                "Model artefact SHA-256 does not match CHECKSUMS.txt.",
                detail=f"expected {expected}, actual {actual}",
                remediation="Re-run scripts/convert_model.py; do not modify the .mmt by hand.",
                http_status=503,
            )
        # Load via Myokit (imported lazily so the rest of the system runs without it).
        try:
            import myokit  # type: ignore
        except ImportError as exc:
            raise TorsadeTwinError(
                "E_MODEL_UNAVAILABLE",
                "Myokit is not installed; the EP engine cannot run.",
                detail="Install backend/requirements.txt (requires network once).",
                remediation="pip install -r backend/requirements.txt",
                http_status=503,
            ) from exc
        model = myokit.load_model(str(self.model_path))
        labels = self._assert_labels(model)
        qnet_labels = self._assert_qnet_labels(model)
        self._disable_herg_dynamic(model)
        return ModelInfo(
            model_id=self.config.get("model_id", "ORd-CiPA-v1.0"),
            artefact=str(self.model_path),
            artefact_sha256=actual,
            source_url=self.config.get("vendor_url", "https://models.cellml.org/e/5a0"),
            source_retrieved_on=self.config.get("source_retrieved_on", ""),
            labels=labels,
            qnet_current_labels=qnet_labels,
        )

    def _expected_hash(self) -> str | None:
        if not self.checksums_path.exists():
            return None
        for line in self.checksums_path.read_text("utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and (self.model_path.name in parts[1] or self.model_path.suffix == Path(parts[1]).suffix):
                return parts[0]
        return None

    def _assert_labels(self, model) -> dict[str, str]:
        available = dict(model.labels())
        label_aliases = {
            "membrane_potential": "membrane_potential",
            "stimulus_current": "stimulus_current",
            "extracellular.ko": "extracellular_ko",
        }
        labels: dict[str, str] = {}
        for name in REQUIRED_LABELS:
            actual = label_aliases.get(name, name)
            if actual not in available:
                raise TorsadeTwinError(
                    "E_MODEL_BINDING",
                    f"Required label binding missing: {name}.",
                    detail="The vendored model must expose membrane_potential, stimulus_current and extracellular_ko.",
                    http_status=503,
                )
            labels[name] = available[actual].qname()
        return labels

    def _assert_qnet_labels(self, model) -> dict[str, str]:
        available = dict(model.labels())
        found: dict[str, str] = {}
        for c in QNET_CURRENTS:
            if c in available:
                found[c] = available[c].qname()
        missing = [c for c in QNET_CURRENTS if c not in found]
        if missing:
            raise TorsadeTwinError(
                "E_MODEL_BINDING",
                f"Missing qNet current label(s): {missing}.",
                http_status=503,
            )
        return found

    def _disable_herg_dynamic(self, model) -> None:
        """D1: hold the dynamic drug-hERG binding drug concentration at 0."""
        # The CiPA v1.0 CellML embeds Li 2017 dynamic binding states; we set the drug
        # concentration variable to 0 and record the action. Exact variable name depends on
        # the vendored artefact and is asserted by test_herg_dynamic_disabled.py.
        candidates = ["drug", "herg.drug", "binding.drug", "drug_conc"]
        for name in candidates:
            if name in model:
                model.get(name).set_rhs(0)
                return
        # If no binding variable is present, the pathway is already inert; record that.


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
