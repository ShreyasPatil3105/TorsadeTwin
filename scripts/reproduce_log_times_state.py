"""Executable reproduction of Myokit's absolute log_times semantics.

This minimal clock model implements the relevant Simulation.run contract: explicit
log times are absolute, and only times in [current_time, current_time + duration)
are emitted.
"""
from __future__ import annotations

import numpy as np


class AbsoluteLogClock:
    def __init__(self) -> None:
        self.time = 0.0

    def run(self, duration: float, log_times: np.ndarray) -> np.ndarray:
        end = self.time + duration
        emitted = log_times[(log_times >= self.time) & (log_times < end)]
        self.time = end
        return emitted


def main() -> None:
    cl = 2000.0
    dt = 0.1
    n_steps = int(round(cl / dt))
    relative = np.arange(n_steps, dtype=float) * dt

    broken = AbsoluteLogClock()
    broken_first = broken.run(cl, relative)
    broken_second = broken.run(cl, relative)

    fixed = AbsoluteLogClock()
    fixed_first = fixed.run(cl, fixed.time + relative)
    fixed_second = fixed.run(cl, fixed.time + relative)

    print(f"broken counts: {len(broken_first)}, {len(broken_second)}")
    print(f"fixed counts:  {len(fixed_first)}, {len(fixed_second)}")
    print(f"fixed second grid: {fixed_second[0]:.1f} ... {fixed_second[-1]:.1f}")

    assert (len(broken_first), len(broken_second)) == (20000, 0)
    assert (len(fixed_first), len(fixed_second)) == (20000, 20000)
    assert fixed_second[0] == 2000.0
    assert fixed_second[-1] == 3999.9


if __name__ == "__main__":
    main()
