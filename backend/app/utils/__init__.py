"""
工具函数
"""
from .hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)
from .ai_interface import (
    call_ai_classification,
    verify_ai_connection,
    AIClassificationError,
    AIConnectionError,
    AIResponseError,
    AIRateLimitError,
)

__all__ = [
    "apply_hospital_filter",
    "get_current_hospital_id_or_raise",
    "validate_hospital_access",
    "set_hospital_id_for_create",
    "call_ai_classification",
    "verify_ai_connection",
    "AIClassificationError",
    "AIConnectionError",
    "AIResponseError",
    "AIRateLimitError",
]
