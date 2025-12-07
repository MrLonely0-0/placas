import re
from dataclasses import dataclass
from typing import List, Optional


# Define regex patterns for plate formats
OLD_PLATE_PATTERN = re.compile(r"^[A-Z]{3}-[0-9]{4}$")
OLD_PLATE_COMPACT_PATTERN = re.compile(r"^[A-Z]{3}[0-9]{4}$")
MERCOSUL_PLATE_PATTERN = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")


@dataclass
class PlateValidationResult:
    valid: bool
    plate_type: Optional[str]
    normalized: str
    errors: List[str]


def normalize_plate(raw: str) -> str:
    """Trim spaces and uppercase the plate text."""
    return raw.strip().upper()


def validate_plate(raw: str) -> PlateValidationResult:
    """Validate a Brazilian car plate against old and Mercosul formats."""
    normalized = normalize_plate(raw)
    errors: List[str] = []

    if not normalized:
        errors.append("Placa obrigatoria")
        return PlateValidationResult(False, None, normalized, errors)

    # Reject internal spaces
    if " " in normalized:
        errors.append("Nao use espacos internos")

    # Decide format
    if OLD_PLATE_PATTERN.fullmatch(normalized):
        return PlateValidationResult(True, "ANTIGA", normalized, errors)

    if OLD_PLATE_COMPACT_PATTERN.fullmatch(normalized):
        # Normalize to include hyphen for consistency
        normalized_hyphen = f"{normalized[:3]}-{normalized[3:]}"
        return PlateValidationResult(True, "ANTIGA", normalized_hyphen, errors)

    if MERCOSUL_PLATE_PATTERN.fullmatch(normalized):
        return PlateValidationResult(True, "MERCOSUL", normalized, errors)

    # If reached here, formats mismatched
    if not errors:
        errors.append("Formato invalido: use AAA-0000 ou AAA0A00")

    return PlateValidationResult(False, None, normalized, errors)


def is_valid_plate(raw: str) -> bool:
    """Convenience boolean check."""
    return validate_plate(raw).valid
