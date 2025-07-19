import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BroadcastConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"broadcast_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from room group (for demo purpose unless we )
    async def broadcast_message(self, event):
        """Simple text message"""
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def broadcast_html_update(self, event):
        """Output of HTMX-generating view that designates what part of page to render to."""
        html_content = event["html_content"]
        target_element = event["target_element"]

        # Send HTML update to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "html_update",
                    "html_content": html_content,
                    "target_element": target_element,
                }
            )
        )
