from django import template

register = template.Library()


@register.filter
def get_action_badge(action):
    """
    Return Bootstrap badge color class based on action type
    """
    badge_colors = {
        "CREATE": "success",
        "UPDATE": "info",
        "DELETE": "danger",
        "VIEW": "secondary",
        "DOWNLOAD": "warning",
        "IMPORT": "primary",
        "LOGIN": "success",
        "LOGOUT": "secondary",
        "PASSWORD_CHANGE": "warning",
        "SETTINGS_CHANGE": "info",
        "BULK_DELETE": "danger",
        "STATUS_CHANGE": "info",
    }
    return badge_colors.get(action, "secondary")
