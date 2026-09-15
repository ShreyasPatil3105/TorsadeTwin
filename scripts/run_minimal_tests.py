#!/usr/bin/env python3
"""Minimal pytest-compatible runner for constrained sandboxes where pytest is unavailable.

The same test files run under real pytest in the target environment (make test). This
harness injects a small pytest shim (raises/mark/skip/approx/importorskip) and executes
every test_* function in tests/, reporting pass/fail/skip/error counts. It is used ONLY
for verification in this offline sandbox; it is not a replacement for the real suite.
"""
from __future__ import annotations

import contextlib
import importlib
import importlib.util
import re
import sys
import types
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))


class _Skip(Exception):
    pass


class _Raises(contextlib.AbstractContextManager):
    def __init__(self, exc_type, match=None):
        self.exc_type = exc_type
        self.match = match
        self.value = None

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is None:
            raise AssertionError(f"DID NOT RAISE {self.exc_type}")
        if not issubclass(et, self.exc_type):
            raise AssertionError(f"raised {et} instead of {self.exc_type}")
        if self.match is not None and re.search(self.match, str(ev)) is None:
            raise AssertionError(f"exception message {ev!r} does not match {self.match!r}")
        self.value = ev
        return True


class _Approx:
    def __init__(self, value, rel=None, abs=None):
        self.value = value
        self.rel = rel if rel is not None else 1e-6
        self.abs = abs if abs is not None else 1e-12

    def __eq__(self, other):
        if isinstance(other, _Approx):
            other = other.value
        return abs(self.value - other) <= max(self.rel * max(abs(self.value), abs(other)), self.abs)

    def __repr__(self):
        return f"approx({self.value})"


def _make_mark():
    class _Mark:
        def __getattr__(self, name):
            def deco(*args, **kwargs):
                if name == "skipif":
                    cond = args[0] if args else False
                    reason = kwargs.get("reason", "skipped")
                    if cond:
                        def wrapper(fn):
                            def wrapped(*a, **k):
                                raise _Skip(reason)
                            return wrapped
                        return wrapper
                return lambda fn: fn
            return deco
    return _Mark()


def _make_pytest_shim():
    mod = types.ModuleType("pytest")
    mod.raises = _Raises
    mod.mark = _make_mark()
    mod.skip = lambda reason="": (_ for _ in ()).throw(_Skip(reason))
    mod.skipif = lambda cond, reason="": (lambda fn: fn)
    mod.fixture = lambda *a, **k: (lambda fn: fn)
    mod.approx = _Approx
    mod.param = lambda *a, **k: (a[0] if a else None)
    mod.importorskip = lambda name, *a, **k: (_ for _ in ()).throw(_Skip(f"missing {name}"))
    mod.mark.skipif = lambda cond, reason="": (
        (lambda fn: (lambda *a, **k: (_ for _ in ()).throw(_Skip(reason))) if cond else (lambda fn: fn))(None)
    )
    return mod


def _load_module(path: Path):
    rel = path.relative_to(ROOT)
    dotted = ".".join(rel.with_suffix("").parts)
    return importlib.import_module(dotted)


def main() -> int:
    sys.modules["pytest"] = _make_pytest_shim()
    results = {"pass": 0, "fail": 0, "skip": 0, "error": 0}
    failures = []
    files = sorted(ROOT.joinpath("tests").rglob("test_*.py"))
    for path in files:
        rel = path.relative_to(ROOT)
        try:
            mod = _load_module(path)
        except Exception as exc:
            results["error"] += 1
            failures.append((str(rel), "<import>", f"{type(exc).__name__}: {exc}"))
            continue
        for name, fn in sorted(vars(mod).items()):
            if not name.startswith("test_") or not callable(fn):
                continue
            if getattr(fn, "__module__", None) != mod.__name__:
                continue
            try:
                fn()
                results["pass"] += 1
            except _Skip:
                results["skip"] += 1
            except AssertionError as exc:
                results["fail"] += 1
                failures.append((str(rel), name, f"AssertionError: {exc}"))
            except Exception as exc:
                results["error"] += 1
                failures.append((str(rel), name, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-600:]}"))
    print(f"\n=== MINIMAL TEST RUN ===\npass={results['pass']} fail={results['fail']} skip={results['skip']} error={results['error']}")
    for rel, name, msg in failures:
        print(f"\nFAIL {rel}::{name}\n  {msg}")
    return 1 if (results["fail"] or results["error"]) else 0


if __name__ == "__main__":
    sys.exit(main())
