import asyncio

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def _resolve_group_names_for_user(user):
    groups = [f"user.{user.id}"]
    if user.is_superuser:
        groups.append("role.superuser")
    if user.is_staff:
        groups.append("role.staff")
    return groups


def broadcast_to_user(user, event_type, payload):
    channel_layer = get_channel_layer()
    if not channel_layer or not user:
        return

    event = {
        "type": "realtime.event",
        "event_type": event_type,
        "payload": payload,
    }

    for group_name in _resolve_group_names_for_user(user):
        async_to_sync(channel_layer.group_send)(group_name, event)


def broadcast_to_roles(event_type, payload, role_groups=None):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    target_groups = role_groups or ["role.staff", "role.superuser"]
    event = {
        "type": "realtime.event",
        "event_type": event_type,
        "payload": payload,
    }

    for group_name in target_groups:
        async_to_sync(channel_layer.group_send)(group_name, event)


async def broadcast_to_roles_async(event_type, payload, role_groups=None):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    target_groups = role_groups or ["role.staff", "role.superuser"]
    event = {
        "type": "realtime.event",
        "event_type": event_type,
        "payload": payload,
    }

    await asyncio.gather(
        *(channel_layer.group_send(group_name, event) for group_name in target_groups),
        return_exceptions=True,
    )
