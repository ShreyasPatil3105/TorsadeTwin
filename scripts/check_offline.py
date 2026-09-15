#!/usr/bin/env python3
"""Assert no outbound socket is created during the test suite (§19.5).
Monkeypatches socket.socket and runs the CI-gate tests.
"""
from __future__ import annotations

import socket
import sys


class _BlockedSocket:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("outbound socket creation attempted (offline violation)")

    def __getattr__(self, name):
        raise RuntimeError("outbound socket creation attempted (offline violation)")


def main() -> int:
    original = socket.socket
    socket.socket = _BlockedSocket  # type: ignore
    try:
        import pytest
    except ImportError:
        print("pytest not installed; offline check requires the dev environment.")
        return 1
    code = pytest.main(["tests/unit", "tests/api", "tests/failure", "tests/repro", "tests/contract", "-q"])
    socket.socket = original  # type: ignore
    return int(code != 0)


if __name__ == "__main__":
    sys.exit(main())
