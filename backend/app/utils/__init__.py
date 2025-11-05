"""
工具函数
"""
from .hospital_filter import (
    apply_hospital_filter,
    get_current_hospital_id_or_raise,
    validate_hospital_access,
    set_hospital_id_for_create,
)

__all__ = [
    "apply_hospital_filter",
    "get_current_hospital_id_or_raise",
    "validate_hospital_access",
    "set_hospital_id_for_create",
]
