"""
Custom template filters for number formatting with thousands separators.
"""

from django import template

register = template.Library()


@register.filter(name="intcomma_format")
def intcomma_format(value, use_l10n=None):
    """
    Converts an integer or float to a string containing commas every three digits.
    Preserves decimal places for floats.

    Usage in template:
        {{ value|intcomma_format }}
        {{ 1234567.89|intcomma_format }}
    """
    if value is None:
        return ""

    # Convert to string to handle both int and float
    str_value = str(value)

    # Handle negative numbers
    is_negative = str_value.startswith("-")
    if is_negative:
        str_value = str_value[1:]

    # Split on decimal point if it exists
    if "." in str_value:
        integer_part, decimal_part = str_value.split(".")
    else:
        integer_part = str_value
        decimal_part = None

    # Non-numeric values should pass through unchanged.
    try:
        integer_with_commas = "{:,}".format(int(integer_part))
    except (ValueError, TypeError):
        return str(value)

    # Reconstruct the number
    result = integer_with_commas
    if decimal_part is not None:
        result += "." + decimal_part

    if is_negative:
        result = "-" + result

    return result


@register.filter(name="currency")
def currency(value, decimal_places=2):
    """
    Formats a number as currency with thousands separators and decimal places.

    Usage in template:
        ₱{{ value|currency }}
        ₱{{ value|currency:0 }}  (no decimals)
        ₱{{ value|currency:2 }}  (2 decimals)
    """
    if value is None:
        return ""

    try:
        # Format with specified decimal places
        if decimal_places == 0:
            formatted = "{:,.0f}".format(float(value))
        else:
            formatted = "{:,.{}f}".format(float(value), decimal_places)
        return formatted
    except (ValueError, TypeError):
        return str(value)


@register.filter(name="dict_key")
def dict_key(dictionary, key):
    """
    Gets a value from a dictionary using a key.
    Allows accessing dictionary keys that contain special characters (e.g., "4.1A").

    Usage in template:
        {{ budget_data|dict_key:"4.1A" }}
        {{ budget_data|dict_key:code_variable }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
