import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BroadcastConsumer(AsyncWebsocketConsumer):
    """Note two types of consumers here:
    - broadcast_html_update() sends a block of HTML to all clients at once
    - unicast_refresh() just sends a notice to clients that they should refresh
        from source - they will make their own request to get new content.
        We have settled on this approach throughout for consistency and to
        ensure that each request.user is handled correctly in each view.
    """

    async def connect(self):
        self.space_name = self.scope["url_route"]["kwargs"]["space_name"]
        self.room_group_name = f"broadcast_{self.space_name}"

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
        """Broadcast pre-rendered HTML to all users of the space.
        Essentially deprecated but leaving in place in case useful."""
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

    async def unicast_refresh(self, event):
        """Single handler for all unicast refresh triggers.
        Event should contain 'target_id' to specify which element to refresh.
        """
        # Send trigger-only update to WebSocket
        await self.send(
            text_data=json.dumps({"type": "unicast_refresh", "target_id": event["target_id"]})
        )
