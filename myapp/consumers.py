import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
            
        # URL route: ws/chat/<vendor_id>/
        # 'vendor_id' here acts as the other user's ID
        self.other_user_id = self.scope['url_route']['kwargs']['vendor_id']
        
        try:
            self.other_user_id = int(self.other_user_id)
        except ValueError:
            await self.close()
            return
            
        # Ensure a consistent room name regardless of who initiates
        user_ids = sorted([self.user.id, self.other_user_id])
        self.room_group_name = f'chat_{user_ids[0]}_{user_ids[1]}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message', '')
        
        if not message_content:
            return
            
        # Save message to database
        saved_message = await self.save_message(self.user.id, self.other_user_id, message_content)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': saved_message.content,
                'sender_id': self.user.id,
                'sender_name': self.user.get_full_name() or self.user.username,
                'time': saved_message.created_at.strftime("%I:%M %p").lstrip('0')
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event.get('sender_name', ''),
            'time': event.get('time', '')
        }))
        
    @sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)
            return Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content
            )
        except User.DoesNotExist:
            return None
