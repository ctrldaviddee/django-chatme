from channels.generic.websocket import AsyncWebsocketConsumer


class ChatroomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
