from __future__ import annotations

from backend.app.services.hashing import canonical_json, config_hash, input_hash, result_hash, sha256_hex


def test_canonical_sorted_keys():
    a = canonical_json({"b": 1, "a": 2})
    b = canonical_json({"a": 2, "b": 1})
    assert a == b


def test_canonical_float_format():
    assert canonical_json({"x": 0.1}) == canonical_json({"x": 0.1000000000000000055511151231257827})


def test_canonical_no_whitespace():
    assert " " not in canonical_json({"a": [1, 2], "b": {"c": 3}})
    assert "\n" not in canonical_json({"a": 1})


def test_canonical_deterministic():
    assert canonical_json({"x": 1.5, "y": [1, 2, 3]}) == canonical_json({"x": 1.5, "y": [1, 2, 3]})


def test_sha256_known_vector():
    import hashlib

    assert sha256_hex("abc") == hashlib.sha256(b"abc").hexdigest()


def test_config_hash_changes_with_block():
    h1 = config_hash({"a": 1}, {}, {}, {}, {}, {}, "digest")
    h2 = config_hash({"a": 2}, {}, {}, {}, {}, {}, "digest")
    assert h1 != h2


def test_result_hash_deterministic():
    out = {"qnet": 0.0631, "apd90": 291.4}
    assert result_hash("c", "i", out) == result_hash("c", "i", out)


def test_result_hash_sensitive_to_outputs():
    out1 = {"qnet": 0.0631}
    out2 = {"qnet": 0.0632}
    assert result_hash("c", "i", out1) != result_hash("c", "i", out2)


def test_input_hash_stable():
    a = input_hash({"drugs": [{"drug_id": "d", "exposure_multiplier": 1.0}], "k_o_mM": 4.0})
    b = input_hash({"k_o_mM": 4.0, "drugs": [{"exposure_multiplier": 1.0, "drug_id": "d"}]})
    assert a == b
