import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .models import ChatGroup, GroupMessages


class ChatroomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.chatroom_name = self.scope["url_route"]["kwargs"]["chatroom_name"]
        self.chatroomobj = await database_sync_to_async(get_object_or_404)(
            ChatGroup, group_name=self.chatroom_name
        )

        await self.channel_layer.group_add(
            self.chatroom_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.chatroom_name,
            self.channel_name,
        )

    async def receive(self, text_data):
        text_data = json.loads(s=text_data)
        text_data_msg = text_data.get("content")
        message = await database_sync_to_async(GroupMessages.objects.create)(
            group=self.chatroomobj,
            author=self.user,
            content=text_data_msg,
        )

        event = {
            "type": "message_handler",
            "message_id": message.id,
        }

        await self.channel_layer.group_send(
            self.chatroom_name,
            event,
        )

    async def message_handler(self, event):

        message_id = event["message_id"]

        message = await database_sync_to_async(
            GroupMessages.objects.prefetch_related("author__profile").get
        )(id=message_id)

        context = {
            "message": message,
            "user": self.user,
        }
        html = render_to_string(
            template_name="chats/partials/chat_message_p.html", context=context
        )

        await self.send(text_data=html)
