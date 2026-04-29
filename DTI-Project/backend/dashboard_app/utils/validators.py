"""
Custom validators for DTI Fund Monitoring System
Implements required, numeric, letters-only, format, range, uniqueness, date, and security validations
"""

import re
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError

_STRING_LENGTH_VALIDATOR_CACHE = {}


# ============================================================================
# NUMERIC VALIDATORS
# ============================================================================


def validate_numeric_only(value):
    """Validates that a field contains only numeric characters"""
    if not str(value).isdigit():
        raise ValidationError(
            "Please enter only numeric characters (0-9). Special characters and letters are not allowed.",
            code="numeric_only",
        )


def validate_positive_number(value):
    """Validates that a value is a positive number"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Value must be a positive number. Negative values are not permitted.",
                code="positive_number",
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid numeric value.", code="invalid_number"
        )


def validate_non_negative_number(value):
    """Validates that a value is zero or positive"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Negative values are not allowed. Please enter a value of zero or greater.",
                code="non_negative",
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid numeric value.", code="invalid_number"
        )


# ============================================================================
# TEXT FORMAT VALIDATORS
# ============================================================================


def validate_letters_only(value):
    """Validates that a field contains only letters (including accented), spaces, hyphens, periods, and apostrophes"""
    value_str = str(value)

    # Check each character
    for char in value_str:
        # Allow: letters (including accented), spaces, hyphens, periods, apostrophes
        if not (char.isalpha() or char in " -.'" or ord(char) > 127):
            raise ValidationError(
                "Only letters (including accented characters), spaces, hyphens, periods, and apostrophes are allowed. Numbers and special characters cannot be used.",
                code="letters_only",
            )

    # Also reject if contains numbers
    if re.search(r"\d", value_str):
        raise ValidationError("Numbers are not allowed in names.", code="letters_only")


def validate_alphanumeric_with_spaces(value):
    """Validates alphanumeric characters with spaces"""
    if not re.match(r"^[a-zA-Z0-9\s\-\.]+$", str(value)):
        raise ValidationError(
            "Please use only letters, numbers, spaces, hyphens, and periods. Special characters are not permitted.",
            code="alphanumeric",
        )


def validate_tin_format(value):
    """
    Validates Philippine Tax Identification Number (TIN) format
    Format: ###-###-###-### (12 digits with hyphens)
    """
    value = str(value).strip()
    if not re.match(r"^\d{3}-\d{3}-\d{3}-\d{3}$", value):
        raise ValidationError(
            "Invalid TIN format. Please use the format: ###-###-###-### (12 digits with hyphens, e.g., 123-456-789-012)",
            code="invalid_tin",
        )


def validate_tin_numeric(value):
    """Validates that TIN contains only the required digits"""
    tin_digits = str(value).replace("-", "")
    if not tin_digits.isdigit():
        raise ValidationError(
            "TIN must contain only numeric digits (0-9) and hyphens. Letters or other characters are not allowed.",
            code="tin_numeric",
        )


def validate_phone_number(value):
    """
    Validates Philippine phone number format - MORE FLEXIBLE
    Accepts:
    - Mobile: 09XX-XXX-XXXX, 09XXXXXXXXXX, +63-9XX-XXX-XXXX
    - Landline: (02) XXXX-XXXX, 02-XXXX-XXXX, 4808394 (7-8 digits)
    - Multiple numbers separated by slash: 480-7481 / 480-7687
    - Dual mobile: 09061348372 / 09558044035
    """
    if not value or not str(value).strip():
        # Empty is allowed - field is optional
        return

    value_str = str(value).strip()

    # Handle dual phone numbers - extract first one if separated by /
    if "/" in value_str:
        value_str = value_str.split("/")[0].strip()

    # Remove all formatting characters
    cleaned = (
        value_str.replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    # Remove leading country code (63) or leading 0
    if cleaned.startswith("63"):
        cleaned = cleaned[2:]
    elif cleaned.startswith("0"):
        cleaned = cleaned[1:]

    # Check if remaining value is all digits
    if not cleaned.isdigit():
        raise ValidationError(
            "Invalid phone number format. Phone number must contain only digits, hyphens, spaces, and parentheses. "
            "Accepted formats: 09XX-XXX-XXXX (mobile), (02)XXXX-XXXX (landline), or 480-7481 (local).",
            code="invalid_phone",
        )

    # Accept 7+ digits (covers local area codes, landlines, and mobile)
    if len(cleaned) < 7:
        raise ValidationError(
            "Invalid phone number. Phone number must have at least 7 digits.",
            code="invalid_phone_length",
        )

    # Accept up to 11 digits (covers mobile with 0 prefix = 10 digits, or 11 with +63)
    if len(cleaned) > 11:
        raise ValidationError(
            "Invalid phone number. Phone number has too many digits (max 11).",
            code="invalid_phone_too_long",
        )


def validate_email_format(value):
    """Validates email format"""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, str(value)):
        raise ValidationError(
            "Invalid email format. Please enter a valid email address (e.g., name@example.com).",
            code="invalid_email",
        )


def validate_hex_color(value):
    """Validates hex color format (#RRGGBB)"""
    if not re.match(r"^#[0-9A-Fa-f]{6}$", str(value)):
        raise ValidationError(
            "Invalid color format. Please use hexadecimal format: #RRGGBB (e.g., #FF5733).",
            code="invalid_hex_color",
        )


# ============================================================================
# RANGE VALIDATORS
# ============================================================================


def validate_percentage(value):
    """Validates that a value is between 0 and 100"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0 or decimal_value > 100:
            raise ValidationError(
                "Percentage must be between 0 and 100. Please enter a valid percentage value.",
                code="percentage_range",
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid numeric percentage value.", code="invalid_number"
        )


def validate_budget_amount(value):
    """Validates budget amounts are reasonable (max 999,999,999.99)"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Budget amount cannot be negative. Please enter a positive value.",
                code="negative_amount",
            )
        if decimal_value > Decimal("999999999.99"):
            raise ValidationError(
                "Budget amount exceeds the maximum allowed limit of ₱999,999,999.99.",
                code="amount_too_large",
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid budget amount.", code="invalid_number"
        )


def validate_transaction_amount(value):
    """Validates transaction amounts"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Transaction amount cannot be negative. Please enter a positive value.",
                code="negative_amount",
            )
        if decimal_value > Decimal("9999999999.99"):
            raise ValidationError(
                "Transaction amount exceeds the maximum allowed limit of ₱9,999,999,999.99.",
                code="amount_too_large",
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid transaction amount.", code="invalid_number"
        )


def validate_string_length(min_length=0, max_length=None):
    """Factory function for string length validation.

    Skips validation if the value is blank/None; this allows fields that
    permit empty values (blank=True) to avoid raising errors when left
    empty, while still enforcing length constraints on non-empty input.

    The returned function is given a descriptive name so that migrations
    can correctly reference it instead of using the generic ``validator``
    name which would later cause import errors.
    """
    cache_key = (min_length, max_length)
    if cache_key in _STRING_LENGTH_VALIDATOR_CACHE:
        return _STRING_LENGTH_VALIDATOR_CACHE[cache_key]

    def validator(value):
        if value is None:
            return
        str_value = str(value).strip()
        # ignore empty strings to allow blank values through
        if str_value == "":
            return
        if len(str_value) < min_length:
            raise ValidationError(
                f"This field must be at least {min_length} characters long.",
                code="min_length",
            )
        if max_length and len(str_value) > max_length:
            raise ValidationError(
                f"This field must be at most {max_length} characters long.",
                code="max_length",
            )

    # assign explicit name to avoid collision during migration serialization
    validator.__name__ = f"validate_string_length_{min_length}_{max_length}"
    # ensure serializer sees this as a module-level function (not <locals>)
    validator.__qualname__ = validator.__name__
    # also register it in the module namespace so Django's serializer
    # can import it by name when writing migrations
    globals()[validator.__name__] = validator
    _STRING_LENGTH_VALIDATOR_CACHE[cache_key] = validator
    return validator


# compatibility shim for migrations
# some historical migrations serialized the inner function returned by
# `validate_string_length` and named it ``validator``. When those
# migrations are executed Django will try to import
# ``dashboard_app.utils.validators.validator``. Without a top-level symbol
# this import fails with the ValueError mentioned in the issue.
#
# The function below is never used by application logic; it simply
# exists so that the import succeeds. The real validator applied to
# fields is created by calling `validate_string_length(...)` during
# model initialization.
def validator(value):
    """Placeholder function for migration compatibility."""
    # no-op: migrations already contain the serialized validation code
    return


# ============================================================================
# DATE VALIDATORS
# ============================================================================


def validate_date_not_in_future(value):
    """Validates that a date is not in the future"""
    if value > date.today():
        raise ValidationError(
            "Date cannot be set in the future. Please enter today's date or an earlier date.",
            code="future_date",
        )


def validate_date_not_in_past(value):
    """Validates that a date is not in the past"""
    if value < date.today():
        raise ValidationError(
            "Date cannot be in the past. Please enter today's date or a future date.",
            code="past_date",
        )


def validate_cleared_date_after_transaction(instance_date, cleared_date):
    """Validates that cleared_date is after or equal to transaction date"""
    if cleared_date and cleared_date < instance_date:
        raise ValidationError(
            "Cleared date must be on or after the transaction date.",
            code="cleared_date_before_transaction",
        )


# ============================================================================
# SECURITY VALIDATORS
# ============================================================================


def sanitize_string_input(value):
    """
    Sanitizes string input to prevent injection attacks
    Removes potentially harmful characters
    """
    if not isinstance(value, str):
        return value

    # Remove null bytes
    value = value.replace("\x00", "")

    # Remove control characters except newlines and tabs
    value = "".join(char for char in value if ord(char) >= 32 or char in "\n\t")

    # Limit consecutive spaces
    value = re.sub(r"\s{2,}", " ", value)

    return value.strip()


def validate_no_script_content(value):
    """Prevents script injection in text fields"""
    dangerous_patterns = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
        r"eval\(",
        r'src\s*=\s*["\']?javascript:',
    ]

    value_lower = str(value).lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            raise ValidationError(
                "This field contains invalid or potentially dangerous content. Please remove any scripts or special tags and try again.",
                code="script_injection",
            )


def validate_no_sql_injection(value):
    """Basic SQL injection prevention in text fields"""
    dangerous_sql_patterns = [
        r"('\s*(OR|AND)\s*')",
        r"(UNION.*SELECT)",
        r"(DROP\s+TABLE)",
        r"(DELETE\s+FROM)",
        r"(INSERT\s+INTO)",
    ]

    value_upper = str(value).upper()
    for pattern in dangerous_sql_patterns:
        if re.search(pattern, value_upper):
            raise ValidationError(
                "This field contains invalid content.", code="sql_injection"
            )


# ============================================================================
# UNIQUENESS VALIDATORS
# ============================================================================


def validate_unique_tin(value, exclude_id=None):
    """
    Validates TIN is unique in Supplier table
    exclude_id: ID of current record to exclude from check (for updates)
    """
    from data_management_app.models import Supplier

    query = Supplier.objects.filter(tin=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)

    if query.exists():
        raise ValidationError(
            "This TIN is already registered in the system. Please use a different TIN or contact administrator if this is a duplicate entry.",
            code="duplicate_tin",
        )


def validate_unique_supplier_name(value, exclude_id=None):
    """Validates supplier name is unique"""
    from data_management_app.models import Supplier

    query = Supplier.objects.filter(supplier__iexact=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)

    if query.exists():
        raise ValidationError(
            "A supplier with this name is already registered. Please use a different name or verify if this is a new supplier.",
            code="duplicate_supplier",
        )


def validate_unique_division_name(value, exclude_id=None):
    """Validates division name is unique"""
    from data_management_app.models import Division

    query = Division.objects.filter(name__iexact=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)

    if query.exists():
        raise ValidationError(
            "A division with this name already exists in the system. Please choose a different name.",
            code="duplicate_division",
        )


def validate_unique_expense_code(value, exclude_id=None):
    """Validates expense object code is unique"""
    from data_management_app.models import ExpenseObject

    query = ExpenseObject.objects.filter(code=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)

    if query.exists():
        raise ValidationError(
            "This expense code is already in use. Please enter a unique code or contact administrator.",
            code="duplicate_code",
        )


def validate_unique_expense_category(value, exclude_id=None):
    """Validates expense category name is unique"""
    from data_management_app.models import ExpenseCategory

    query = ExpenseCategory.objects.filter(name__iexact=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)

    if query.exists():
        raise ValidationError(
            "An expense category with this name is already registered. Please use a different name.",
            code="duplicate_category",
        )


# ============================================================================
# FIELD-SPECIFIC VALIDATORS
# ============================================================================


def validate_nc_format(value):
    """Validates NC (Neighborhood Code) format"""
    valid_ncs = [
        "sto_domingo",
        "bacacay",
        "malilipot",
        "tabaco_city",
        "tiwi",
        "apo",
        "sedcen",
        "camalig",
        "daraga",
        "manito",
        "guinobatan",
        "ligao_city",
        "oas",
        "polangui",
        "piodoran",
    ]
    if str(value).lower() not in valid_ncs:
        raise ValidationError(
            "Invalid Neighborhood Code. Please select a valid NC from the provided dropdown list.",
            code="invalid_nc",
        )


def validate_dv_number_format(value):
    """Validates Disbursement Voucher number format"""
    if value and not re.match(r"^[A-Z0-9\-]+$", str(value)):
        raise ValidationError(
            "Invalid DV Number format. Please use only uppercase letters, numbers, and hyphens (e.g., DV-2024-001).",
            code="invalid_dv",
        )


def validate_check_number_format(value):
    """Validates check number format"""
    if value and not re.match(r"^[A-Z0-9\-]+$", str(value)):
        raise ValidationError(
            "Invalid check number format. Please use only uppercase letters, numbers, and hyphens.",
            code="invalid_check",
        )
