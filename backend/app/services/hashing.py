# Hashing rules (§18.3). canonical_json, config_hash, input_hash, result_hash.
# Determinism is a build-blocking requirement: no timestamps inside hashed payloads,
# sorted keys, floats formatted %.12e, no whitespace.
from __future__ import annotations

import hashlib
import json
from typing import Any


def _format_float(v: float) -> str:
    return format(float(v), ".12e")


def canonical_json(obj: Any) -> str:
    """Serialize an object to canonical JSON: UTF-8, sorted keys, floats as %.12e."""
    return json.dumps(_canon(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _canon(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _canon(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_canon(v) for v in obj]
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float)):
        if isinstance(obj, bool):
            return obj
        return _format_float(float(obj))
    if obj is None:
        return None
    return str(obj)


def sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def config_hash(model_block: dict, solver_block: dict, protocol_block: dict,
                thresholds_block: dict, margin_block: dict, rescue_block: dict,
                drug_parameter_digest: str) -> str:
    """config_hash = sha256(canonical_json(...)) per §18.3."""
    payload = {
        "model": model_block,
        "solver": solver_block,
        "protocol": protocol_block,
        "thresholds": thresholds_block,
        "margin": margin_block,
        "rescue": rescue_block,
        "drug_parameter_digest": drug_parameter_digest,
    }
    return sha256_hex(canonical_json(payload))


def input_hash(state: Any) -> str:
    """input_hash = sha256(canonical_json(StateSpec))."""
    return sha256_hex(canonical_json(state))


def result_hash(config_hash_: str, input_hash_: str, numeric_outputs: dict) -> str:
    """result_hash = sha256(config_hash + input_hash + canonical_json(numeric outputs, %.12e))."""
    payload = config_hash_ + input_hash_ + canonical_json(numeric_outputs)
    return sha256_hex(payload)
