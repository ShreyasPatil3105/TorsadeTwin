# Unit constants and conversion guards (§2.2 L3, services/units).

# qNet is stored in SI (C/F) and displayed in uC/uF (numerically identical).
C_PER_F_TO_UC_PER_UF = 1.0e6  # 1 C/F == 1e6 uC/uF (numerically identical to uC/uF scale)

# Free concentration units: nM throughout. Hill exponents dimensionless.
NANOMOLAR = "nM"

# Stimulus amplitude A/F, durations ms.
AMP_A_PER_F = -80.0


def c_per_f_to_uc_per_uf(value: float) -> float:
    """Convert C/F to uC/uF for display (numerically identical values)."""
    return value * C_PER_F_TO_UC_PER_UF


def assert_finite(*values: float) -> None:
    """Raise ValueError if any value is NaN or infinite."""
    import math

    for v in values:
        if v is not None and (math.isnan(v) or math.isinf(v)):
            raise ValueError("non-finite numeric value")
