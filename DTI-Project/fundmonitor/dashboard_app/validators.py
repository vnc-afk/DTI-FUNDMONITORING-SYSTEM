"""
Custom validators for DTI Fund Monitoring System
Implements required, numeric, letters-only, format, range, uniqueness, date, and security validations
"""

import re
from decimal import Decimal
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models import Q


# ============================================================================
# NUMERIC VALIDATORS
# ============================================================================

def validate_numeric_only(value):
    """Validates that a field contains only numeric characters"""
    if not str(value).isdigit():
        raise ValidationError(
            "Please enter only numeric characters (0-9). Special characters and letters are not allowed.",
            code="numeric_only"
        )


def validate_positive_number(value):
    """Validates that a value is a positive number"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Value must be a positive number. Negative values are not permitted.",
                code="positive_number"
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid numeric value.",
            code="invalid_number"
        )


def validate_non_negative_number(value):
    """Validates that a value is zero or positive"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Negative values are not allowed. Please enter a value of zero or greater.",
                code="non_negative"
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid numeric value.",
            code="invalid_number"
        )


# ============================================================================
# TEXT FORMAT VALIDATORS
# ============================================================================

def validate_letters_only(value):
    """Validates that a field contains only letters and spaces"""
    if not re.match(r'^[a-zA-Z\s\-\.\']+$', str(value)):
        raise ValidationError(
            "Only letters, spaces, hyphens, periods, and apostrophes are allowed. Numbers and special characters cannot be used.",
            code="letters_only"
        )


def validate_alphanumeric_with_spaces(value):
    """Validates alphanumeric characters with spaces"""
    if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', str(value)):
        raise ValidationError(
            "Please use only letters, numbers, spaces, hyphens, and periods. Special characters are not permitted.",
            code="alphanumeric"
        )


def validate_tin_format(value):
    """
    Validates Philippine Tax Identification Number (TIN) format
    Format: ###-###-###-### (12 digits with hyphens)
    """
    value = str(value).strip()
    if not re.match(r'^\d{3}-\d{3}-\d{3}-\d{3}$', value):
        raise ValidationError(
            "Invalid TIN format. Please use the format: ###-###-###-### (12 digits with hyphens, e.g., 123-456-789-012)",
            code="invalid_tin"
        )


def validate_tin_numeric(value):
    """Validates that TIN contains only the required digits"""
    tin_digits = str(value).replace('-', '')
    if not tin_digits.isdigit():
        raise ValidationError(
            "TIN must contain only numeric digits (0-9) and hyphens. Letters or other characters are not allowed.",
            code="tin_numeric"
        )


def validate_phone_number(value):
    """
    Validates Philippine phone number format
    Accepts: 09XX-XXX-XXXX, 09XXXXXXXXXX, +63-9XX-XXX-XXXX, (02) XXXX-XXXX
    """
    value = str(value).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Remove leading +63 or 0 for validation
    if value.startswith('+63'):
        value = value[3:]
    elif value.startswith('0'):
        value = value[1:]
    
    if not (value.isdigit() and len(value) == 10):
        raise ValidationError(
            "Invalid phone number format. Please enter a valid Philippine number with 10 digits (e.g., 09XX-XXX-XXXX).",
            code="invalid_phone"
        )


def validate_email_format(value):
    """Validates email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, str(value)):
        raise ValidationError(
            "Invalid email format. Please enter a valid email address (e.g., name@example.com).",
            code="invalid_email"
        )


def validate_hex_color(value):
    """Validates hex color format (#RRGGBB)"""
    if not re.match(r'^#[0-9A-Fa-f]{6}$', str(value)):
        raise ValidationError(
            "Invalid color format. Please use hexadecimal format: #RRGGBB (e.g., #FF5733).",
            code="invalid_hex_color"
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
                code="percentage_range"
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid numeric percentage value.",
            code="invalid_number"
        )


def validate_budget_amount(value):
    """Validates budget amounts are reasonable (max 999,999,999.99)"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Budget amount cannot be negative. Please enter a positive value.",
                code="negative_amount"
            )
        if decimal_value > Decimal('999999999.99'):
            raise ValidationError(
                "Budget amount exceeds the maximum allowed limit of ₱999,999,999.99.",
                code="amount_too_large"
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid budget amount.",
            code="invalid_number"
        )


def validate_transaction_amount(value):
    """Validates transaction amounts"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValidationError(
                "Transaction amount cannot be negative. Please enter a positive value.",
                code="negative_amount"
            )
        if decimal_value > Decimal('99999999.99'):
            raise ValidationError(
                "Transaction amount exceeds the maximum allowed limit of ₱99,999,999.99.",
                code="amount_too_large"
            )
    except (ValueError, TypeError):
        raise ValidationError(
            "Please enter a valid transaction amount.",
            code="invalid_number"
        )


def validate_string_length(min_length=0, max_length=None):
    """Factory function for string length validation"""
    def validator(value):
        str_value = str(value).strip()
        if len(str_value) < min_length:
            raise ValidationError(
                f"This field must be at least {min_length} characters long.",
                code="min_length"
            )
        if max_length and len(str_value) > max_length:
            raise ValidationError(
                f"This field must be at most {max_length} characters long.",
                code="max_length"
            )
    return validator


# ============================================================================
# DATE VALIDATORS
# ============================================================================

def validate_date_not_in_future(value):
    """Validates that a date is not in the future"""
    if value > date.today():
        raise ValidationError(
            "Date cannot be set in the future. Please enter today's date or an earlier date.",
            code="future_date"
        )


def validate_date_not_in_past(value):
    """Validates that a date is not in the past"""
    if value < date.today():
        raise ValidationError(
            "Date cannot be in the past. Please enter today's date or a future date.",
            code="past_date"
        )


def validate_cleared_date_after_transaction(instance_date, cleared_date):
    """Validates that cleared_date is after or equal to transaction date"""
    if cleared_date and cleared_date < instance_date:
        raise ValidationError(
            "Cleared date must be on or after the transaction date.",
            code="cleared_date_before_transaction"
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
    value = value.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\t')
    
    # Limit consecutive spaces
    value = re.sub(r'\s{2,}', ' ', value)
    
    return value.strip()


def validate_no_script_content(value):
    """Prevents script injection in text fields"""
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
        r'eval\(',
        r'src\s*=\s*["\']?javascript:',
    ]
    
    value_lower = str(value).lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            raise ValidationError(
                "This field contains invalid or potentially dangerous content. Please remove any scripts or special tags and try again.",
                code="script_injection"
            )


def validate_no_sql_injection(value):
    """Basic SQL injection prevention in text fields"""
    dangerous_sql_patterns = [
        r"('\s*(OR|AND)\s*')",
        r'(UNION.*SELECT)',
        r'(DROP\s+TABLE)',
        r'(DELETE\s+FROM)',
        r'(INSERT\s+INTO)',
    ]
    
    value_upper = str(value).upper()
    for pattern in dangerous_sql_patterns:
        if re.search(pattern, value_upper):
            raise ValidationError(
                "This field contains invalid content.",
                code="sql_injection"
            )


# ============================================================================
# UNIQUENESS VALIDATORS
# ============================================================================

def validate_unique_tin(value, exclude_id=None):
    """
    Validates TIN is unique in Supplier table
    exclude_id: ID of current record to exclude from check (for updates)
    """
    from dashboard_app.models import Supplier
    
    query = Supplier.objects.filter(tin=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    if query.exists():
        raise ValidationError(
            "This TIN is already registered in the system. Please use a different TIN or contact administrator if this is a duplicate entry.",
            code="duplicate_tin"
        )


def validate_unique_supplier_name(value, exclude_id=None):
    """Validates supplier name is unique"""
    from dashboard_app.models import Supplier
    
    query = Supplier.objects.filter(supplier__iexact=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    if query.exists():
        raise ValidationError(
            "A supplier with this name is already registered. Please use a different name or verify if this is a new supplier.",
            code="duplicate_supplier"
        )


def validate_unique_division_name(value, exclude_id=None):
    """Validates division name is unique"""
    from dashboard_app.models import Division
    
    query = Division.objects.filter(name__iexact=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    if query.exists():
        raise ValidationError(
            "A division with this name already exists in the system. Please choose a different name.",
            code="duplicate_division"
        )


def validate_unique_expense_code(value, exclude_id=None):
    """Validates expense object code is unique"""
    from dashboard_app.models import ExpenseObject
    
    query = ExpenseObject.objects.filter(code=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    if query.exists():
        raise ValidationError(
            "This expense code is already in use. Please enter a unique code or contact administrator.",
            code="duplicate_code"
        )


def validate_unique_expense_category(value, exclude_id=None):
    """Validates expense category name is unique"""
    from dashboard_app.models import ExpenseCategory
    
    query = ExpenseCategory.objects.filter(name__iexact=value)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    if query.exists():
        raise ValidationError(
            "An expense category with this name is already registered. Please use a different name.",
            code="duplicate_category"
        )


# ============================================================================
# FIELD-SPECIFIC VALIDATORS
# ============================================================================

def validate_mooe_format(value):
    """Validates MOOE category format"""
    if not re.match(r'^[A-Z0-9\-\.]+$', str(value)):
        raise ValidationError(
            "MOOE code must contain only uppercase letters (A-Z), numbers (0-9), hyphens, and periods. Lowercase letters are not allowed.",
            code="invalid_mooe"
        )


def validate_nc_format(value):
    """Validates NC (Neighborhood Code) format"""
    valid_ncs = [
        'sto_domingo', 'bacacay', 'malilipot', 'tabaco_city', 'tiwi',
        'apo', 'sedcen', 'camalig', 'daraga', 'manito',
        'guinobatan', 'ligao_city', 'oas', 'polangui', 'piodoran'
    ]
    if str(value).lower() not in valid_ncs:
        raise ValidationError(
            "Invalid Neighborhood Code. Please select a valid NC from the provided dropdown list.",
            code="invalid_nc"
        )


def validate_dv_number_format(value):
    """Validates Disbursement Voucher number format"""
    if value and not re.match(r'^[A-Z0-9\-]+$', str(value)):
        raise ValidationError(
            "Invalid DV Number format. Please use only uppercase letters, numbers, and hyphens (e.g., DV-2024-001).",
            code="invalid_dv"
        )


def validate_check_number_format(value):
    """Validates check number format"""
    if value and not re.match(r'^[A-Z0-9\-]+$', str(value)):
        raise ValidationError(
            "Invalid check number format. Please use only uppercase letters, numbers, and hyphens.",
            code="invalid_check"
        )
