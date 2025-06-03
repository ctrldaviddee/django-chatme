# Description: WebSocket consumers for handling real-time chat.
# --------------------------------------------------------------------------
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Group, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when websocket is trying to connect
        """
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"User {self.user.username} connected to room {self.room_name}")

        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": f"You are now connected to room {self.room_name}",
                }
            )
        )

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
            print(f"User {self.user.username} disconnected from room {self.room_name}")

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.
        """

        if not self.user.is_authenticated:
            return

        text_data_json = json.loads(text_data)
        message_content = text_data_json.get("message")

        if not message_content:
            return

        print(
            f"Received message from {self.user.username} in {self.room_name}: {message_content}"
        )

        new_message = await self.save_message(
            self.user, self.room_name, message_content
        )

        if new_message is not None:

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",  # This will call the chat_message method
                    "message": message_content,
                    "username": self.user.username,
                    "timestamp": new_message.timestamp.isoformat(),
                },
            )

    # Receive message from room group
    async def chat_message(self, event):
        """
        Called when a message is received from the group
        Sends the message to the WebSocket
        """

        message = event["message"]
        username = event["username"]
        timestamp = event.get("timestamp", "")  # Get timestamp if available

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username,
                    "timestamp": timestamp,
                }
            )
        )

    @database_sync_to_async
    def save_message(self, user, room_name, content):
        """
        Saves a message to the database.
        This needs to be an async helper because Django ORM operations are synchronous.
        """
        try:
            group, created = Group.objects.get_or_create(name=room_name)
            # TODO: handle group creation/joining more explicitly
            return Message.objects.create(group=group, author=user, content=content)
        except Exception as e:
            print(f"Error saving message: {e}")
            # TODO: Handle error appropriately, maybe send an error message back to the user
            return None
