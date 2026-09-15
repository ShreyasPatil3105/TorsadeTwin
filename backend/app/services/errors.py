# Error codes -> HTTP mapping (§19.4).
# Every error body: {error_code, message, detail, remediation, disclaimers}.
# No stack traces to the client; full traces to logs/backend.log.

class TorsadeTwinError(Exception):
    """Base error with the frozen error-code vocabulary."""

    def __init__(self, code: str, message: str, detail: str = "", remediation: str = "",
                 http_status: int = 400, disclaimers: list[str] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail
        self.remediation = remediation
        self.http_status = http_status
        self.disclaimers = disclaimers or ["DISC_GLOBAL"]

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "message": self.message,
            "detail": self.detail,
            "remediation": self.remediation,
            "disclaimers": self.disclaimers,
        }


# Frozen error table (§19.4)
ERROR_TABLE = {
    "E_SCHEMA": (422, "Request schema validation failed."),
    "E_UNKNOWN_DRUG": (400, "Unknown drug id."),
    "E_DOMAIN_K": (400, "Extracellular K+ out of the declared domain."),
    "E_DOMAIN_EXPOSURE": (400, "Exposure multiplier out of the declared domain."),
    "E_DOMAIN_CL": (400, "Pacing cycle length out of the declared domain."),
    "E_PROVENANCE_INCOMPLETE": (503, "Data provenance incomplete; refusing to serve."),
    "E_MODEL_HASH_MISMATCH": (503, "Model artefact hash mismatch; refusing to start."),
    "E_MODEL_BINDING": (503, "Required model label binding missing; refusing to start."),
    "E_MODEL_UNAVAILABLE": (503, "Model artefact unavailable; refusing to serve."),
    "E_SOLVER": (500, "ODE solver failure."),
    "E_NO_STEADY_STATE": (422, "Steady state not reached."),
    "E_NUMERICAL_INSTABILITY": (422, "Numerical instability detected."),
    "E_ACTION_SET_TOO_LARGE": (500, "Declared action set exceeds the permitted size (config error)."),
    "E_NO_UPSTROKE": (422, "No upstroke detected in the analysis beat."),
    "E_BUDGET": (200, "Budget exceeded; partial result returned with degraded credibility."),
    "E_UNITS": (503, "Data unit check failed; refusing to start."),
}


def error_status(code: str) -> int:
    return ERROR_TABLE.get(code, (400, ""))[0]


def error_message(code: str) -> str:
    return ERROR_TABLE.get(code, (400, "Unknown error."))[1]
