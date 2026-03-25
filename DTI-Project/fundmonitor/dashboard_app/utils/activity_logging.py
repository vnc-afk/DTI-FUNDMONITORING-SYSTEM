from django.utils.timezone import now
from dashboard_app.models import ActivityLog


def log_activity(user, action, model_name, object_id=None, object_repr=None, 
                description=None, changed_fields=None, ip_address=None, 
                user_agent=None, is_sensitive=False):
    """
    Log an activity to the ActivityLog model
    
    Args:
        user: User object who performed the action
        action: Action type (CREATE, UPDATE, DELETE, etc.)
        model_name: Name of the model affected
        object_id: ID of the object affected
        object_repr: String representation of the object
        description: Description of what happened
        changed_fields: Dict of changed fields {field: {old: value, new: value}}
        ip_address: IP address of the user
        user_agent: User agent string
        is_sensitive: Whether this is a sensitive operation
    """
    try:
        activity = ActivityLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr or str(object_id),
            description=description or '',
            changed_fields=changed_fields or {},
            ip_address=ip_address,
            user_agent=user_agent,
            is_sensitive=is_sensitive,
        )
        return activity
    except Exception as e:
        print(f"Error logging activity: {e}")
        return None


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_user_agent(request):
    """
    Get client user agent from request
    """
    return request.META.get('HTTP_USER_AGENT', '')


def track_model_changes(old_instance, new_instance, fields_to_track=None):
    """
    Track changes between old and new instance
    
    Args:
        old_instance: Previous version of the object
        new_instance: Current version of the object
        fields_to_track: List of field names to track (if None, tracks all fields)
    
    Returns:
        Dict of changed fields
    """
    changed_fields = {}
    
    if old_instance is None:
        return changed_fields
    
    # Get all fields if not specified
    if fields_to_track is None:
        fields_to_track = [f.name for f in new_instance._meta.get_fields() 
                          if f.name not in ['id', 'created_at', 'updated_at']]
    
    for field_name in fields_to_track:
        try:
            old_value = getattr(old_instance, field_name, None)
            new_value = getattr(new_instance, field_name, None)
            
            # Convert to string for comparison and storage
            old_str = str(old_value) if old_value is not None else None
            new_str = str(new_value) if new_value is not None else None
            
            if old_str != new_str:
                changed_fields[field_name] = {
                    'old': old_str,
                    'new': new_str
                }
        except Exception as e:
            print(f"Error tracking field {field_name}: {e}")
    
    return changed_fields


def log_create(request, instance, model_name):
    """
    Log object creation
    """
    ip = get_client_ip(request) if request else None
    user_agent = get_client_user_agent(request) if request else None
    
    return log_activity(
        user=request.user if request else None,
        action='CREATE',
        model_name=model_name,
        object_id=instance.pk,
        object_repr=str(instance),
        description=f"Created new {model_name}: {instance}",
        ip_address=ip,
        user_agent=user_agent,
        is_sensitive=False
    )


def log_update(request, old_instance, new_instance, model_name, fields_to_track=None):
    """
    Log object update
    """
    changed_fields = track_model_changes(old_instance, new_instance, fields_to_track)
    ip = get_client_ip(request) if request else None
    user_agent = get_client_user_agent(request) if request else None
    
    return log_activity(
        user=request.user if request else None,
        action='UPDATE',
        model_name=model_name,
        object_id=new_instance.pk,
        object_repr=str(new_instance),
        description=f"Updated {model_name}: {new_instance}",
        changed_fields=changed_fields,
        ip_address=ip,
        user_agent=user_agent,
        is_sensitive=bool(changed_fields)
    )


def log_delete(request, instance, model_name):
    """
    Log object deletion
    """
    ip = get_client_ip(request) if request else None
    user_agent = get_client_user_agent(request) if request else None
    
    return log_activity(
        user=request.user if request else None,
        action='DELETE',
        model_name=model_name,
        object_id=instance.pk,
        object_repr=str(instance),
        description=f"Deleted {model_name}: {instance}",
        ip_address=ip,
        user_agent=user_agent,
        is_sensitive=True
    )


def log_custom_action(request, action, model_name, object_id=None, 
                     object_repr=None, description=None, is_sensitive=False):
    """
    Log custom action
    """
    ip = get_client_ip(request) if request else None
    user_agent = get_client_user_agent(request) if request else None
    
    return log_activity(
        user=request.user if request else None,
        action=action,
        model_name=model_name,
        object_id=object_id,
        object_repr=object_repr,
        description=description,
        ip_address=ip,
        user_agent=user_agent,
        is_sensitive=is_sensitive
    )
