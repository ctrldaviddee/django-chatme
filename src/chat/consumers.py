# Description: WebSocket consumers for handling real-time chat.
# --------------------------------------------------------------------------
import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.contrib.auth.models import User

from .models import Group, Message

logger = logging.getLogger(__name__)


def get_redis_client_from_settings():
    redis_client = getattr(settings, "REDIS_CLIENT", None)
    if redis_client is None:
        logger.error(
            "REDIS_CLIENT not configured in Django settings or connection failed."
        )
        raise RuntimeError("Redis client presence for presence is not available")
    return redis_client


class ChatConsumer(AsyncWebsocketConsumer):

    def get_redis_presence_key(self, room_name: str):
        return f"presence:chat:{room_name}"

    async def connect(self):
        self.room_name_url = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name_url}"
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            logger.warning(
                f"Unauthenticated connection attempt to room {self.room_name_url} rejected."
            )
            await self.close()
            return

        try:
            self.db_group, created = await database_sync_to_async(
                Group.objects.get_or_create
            )(name=self.room_name_url)
            self.redis_client = get_redis_client_from_settings()
        except Exception as e:
            logger.error(f"Error during connect for room {self.room_name_url}: {e}")
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        redis_key = self.get_redis_presence_key(self.room_name_url)
        try:
            await database_sync_to_async(self.redis_client.sadd)(
                redis_key, self.user.username
            )
            logger.info(
                f"User {self.user.username} connected to room {self.room_name_url} and added to presence."
            )
            await self.broadcast_presence()
        except Exception as e:
            logger.error(
                f"Redis error adding user {self.user.username} to presence for room {self.room_name_url}: {e}"
            )

    async def disconnect(self, close_code):
        if hasattr(self, "user") and self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
            if hasattr(self, "redis_client") and self.redis_client:
                redis_key = self.get_redis_presence_key(self.room_name_url)
                try:
                    await database_sync_to_async(self.redis_client.srem)(
                        redis_key, self.user.username
                    )
                    logger.info(
                        f"User {self.user.username} disconnected from room {self.room_name_url} and removed from presence."
                    )
                    await self.broadcast_presence()
                except Exception as e:
                    logger.error(
                        f"Redis error removing user {self.user.username} from presence for room {self.room_name_url}: {e}"
                    )
            else:
                logger.warning(
                    f"User {self.user.username} disconnected but Redis client was not available for presence removal."
                )
        else:
            logger.info(
                f"Unauthenticated or partially initialized user disconnected from {getattr(self, 'room_name_url', 'unknown room')}."
            )

    # Handler for presence updates
    async def presence_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "presence_update",  # Client-side type
                    "users": event["users"],
                    "added": event.get("added"),  # Optional: who was added
                    "removed": event.get("removed"),  # Optional: who was removed
                }
            )
        )

    async def receive(self, text_data):
        if not self.user or not self.user.is_authenticated:
            logger.warning(
                "Received message from unauthenticated/uninitialized user. Ignoring."
            )
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            logger.warning(
                f"Could not decode JSON from user {self.user.username}: {text_data}"
            )
            return
        message_content = text_data_json.get("message")
        message_type = text_data_json.get("type", "chat_message")
        if message_type == "chat_message":
            if (
                not message_content
                or not isinstance(message_content, str)
                or not message_content.strip()
            ):
                logger.info(
                    f"Empty or invalid chat message from {self.user.username}. Ignoring."
                )
                return
            if not hasattr(self, "db_group"):
                logger.error(
                    f"db_group not initialized for user {self.user.username} in room {self.room_name_url}. Cannot save message."
                )
                return
            new_message = await self.save_message(
                self.user, self.db_group, message_content.strip()
            )
            if new_message:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.message",
                        "message": new_message.content,
                        "username": self.user.username,
                        "timestamp": new_message.timestamp.isoformat(),
                    },
                )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_message",
                    "message": event["message"],
                    "username": event["username"],
                    "timestamp": event.get("timestamp", ""),
                }
            )
        )

    async def broadcast_presence(self):
        if not hasattr(self, "redis_client") or not self.redis_client:
            logger.error(
                f"Cannot broadcast presence for room {self.room_name_url}, Redis client not available."
            )
            return
        redis_key = self.get_redis_presence_key(self.room_name_url)
        try:
            online_usernames_set = await database_sync_to_async(
                self.redis_client.smembers
            )(redis_key)
            online_usernames = sorted(list(online_usernames_set))
            logger.debug(
                f"Broadcasting presence for room {self.room_name_url}: {online_usernames}"
            )
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "presence.update", "users": online_usernames},
            )
        except Exception as e:
            logger.error(
                f"Error broadcasting presence for room {self.room_name_url}: {e}"
            )

    @database_sync_to_async
    def save_message(self, user_instance: User, group_instance: Group, content: str):
        try:
            message = Message.objects.create(
                group=group_instance, author=user_instance, content=content
            )
            logger.info(
                f"Message saved from {user_instance.username} in group {group_instance.name}"
            )
            return message
        except Exception as e:
            logger.error(
                f"Error saving message from {user_instance.username} in group {group_instance.name}: {e}"
            )
            return None
