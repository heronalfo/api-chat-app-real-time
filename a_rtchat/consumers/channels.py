from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from ..models import ChatGroup
from ..managers import chat_group_manager
from django.core.exceptions import ValidationError, PermissionDenied

class ChannelsConsumer(AsyncWebsocketConsumer):

    async def connect(self):   
        self.user = self.scope['user']
                    
        if self.user.is_anonymous:
            await self.close()
            return
            
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom']
        
        try:
            self.chatroom = await sync_to_async(ChatGroup.objects.get)(name=self.chatroom_name)
        except ChatGroup.DoesNotExist:
            await self.close()
            return
        
        await self.accept()
        
    async def disconnect(self, close_code):
        pass
        
    async def receive(self, text_data):
        self.data = json.loads(text_data)
        self.action = self.data.get('action')
        self.manager = chat_group_manager.GroupManager(user_id=self.user.id, group_id=self.data.get('group_id'))

        try:
            if self.action == 'list':
                message = await self.get_chat_group()   
            elif self.action == 'create':
                message = await self.manager.create_group(self.data)
            elif self.action == 'delete':
                message = await self.manager.delete_group()
            elif self.action == 'edit':
                message = await self.manager.edit_group(self.data)
            elif self.action == 'remove_member':
                message = await self.manager.remove_member(self.data['member_id'])
            elif self.action == 'add_admin':
                message = await self.manager.add_admin(self.data['member_id'])
            elif self.action == 'remove_admin':
                message = await self.manager.remove_admin(self.data['admin_id'])
            else:
                message = 'Invalid action'

            await self.send(text_data=json.dumps({
                'action': self.action,
                'message': message
            }))
        except ValidationError as e:
            await self.send(text_data=json.dumps({
                'action': self.action,
                'errors': e.messages
            }))
        except PermissionDenied as e:
            await self.send(text_data=json.dumps({
                'action': self.action,
                'errors': str(e)
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'action': self.action,
                'errors': 'An error occurred'
            }))