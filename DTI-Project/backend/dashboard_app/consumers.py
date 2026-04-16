import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


class RealtimeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = await self._resolve_user()
        if (
            not self.user
            or isinstance(self.user, AnonymousUser)
            or not self.user.is_authenticated
        ):
            await self.close(code=4401)
            return

        self.groups_to_join = [f"user.{self.user.id}"]
        if self.user.is_staff:
            self.groups_to_join.append("role.staff")
        if self.user.is_superuser:
            self.groups_to_join.append("role.superuser")

        for group_name in self.groups_to_join:
            await self.channel_layer.group_add(group_name, self.channel_name)

        await self.accept()
        await self.send_json(
            {
                "type": "connection.ready",
                "payload": {
                    "user_id": self.user.id,
                    "groups": self.groups_to_join,
                },
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, "groups_to_join"):
            for group_name in self.groups_to_join:
                await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Keep heartbeat support to allow frontend ping if needed.
        if text_data:
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                return

            if data.get("type") == "ping":
                await self.send_json({"type": "pong", "payload": {"ok": True}})

    async def realtime_event(self, event):
        await self.send_json(
            {
                "type": event.get("event_type", "unknown"),
                "payload": event.get("payload", {}),
            }
        )

    async def send_json(self, payload):
        await self.send(text_data=json.dumps(payload))

    async def _resolve_user(self):
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        params = parse_qs(query_string)
        token = (params.get("token") or [""])[0]
        if not token:
            return AnonymousUser()

        try:
            access_token = AccessToken(token)
            user_id = access_token.get("user_id")
            if not user_id:
                return AnonymousUser()
            return await self._get_user_by_id(user_id)
        except (InvalidToken, TokenError, ValueError):
            return AnonymousUser()

    @database_sync_to_async
    def _get_user_by_id(self, user_id):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return AnonymousUser()
