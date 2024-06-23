from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from asgiref.sync import async_to_sync
import json
from ..models import ChatGroup, GroupMessage
from ..managers import group_message_manager

class ChatroomConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope['user']
        
        # Verifica se o usuário é anônimo
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Obtém o nome da sala de chat e o objeto ChatGroup correspondente
        
        try:
            self.chatroom_name = self.scope['url_route']['kwargs']['chatroom']    
            self.chatroom = await database_sync_to_async(ChatGroup.objects.get)(name=self.chatroom_name)
            
        except ObjectDoesNotExist:
            await self.close()
            return
            
        self.manager = group_message_manager.ChatGroupManager
        # Adiciona o usuário ao grupo de canais
        await async_to_sync(layer.group_add)(
            self.chatroom_name,
            self.channel_name
        )
        
        # Adiciona o usuário às listas de users_online e members da sala de chat
        await self.add_or_remove_user_online(self.user, connect=True)
        await self.add_or_remove_member(self.user, connect=True)
        
        # Aceita a conexão WebSocket
        await self.accept()
        
        # Envia a contagem de usuários online após a conexão ser aceita
        await self.manager.get_messages()
        await self.manager.send_online_user_count()
    
    async def disconnect(self, close_code):
        await async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name,
            self.channel_name
        )
        
        # Remove o usuário das listas de users_online e members da sala de chat
        await self.add_or_remove_user_online(self.user, connect=False)
    
    async def receive(self, text_data):    
        data = json.loads(text_data)
        self.action = data.get('action')
        
        try:
            if self.action == 'list':
                await self.manager.get_messages()        
            elif self.action == 'create':          
                await self.manager.send_message(data)                
            elif self.action == 'file':
                await self.manager.send_message_file(data)                       
            elif self.action == 'destroy':       
                await self.manager.delete_message(data)                
            elif self.action == 'update':       
                await self.manager.edit_message(data)                
            elif self.action == 'online_user_count':        
                await self.manager.send_online_user_count()                
            
            else:
                await self.send(text_data=json.dumps({
                    'action': action,
                    'message': 'Method Not Allowed'
                }))
                                
        except ValidationError as e:
            await self.send(text_data=json.dumps({
                'action': self.action,
                'errors': e.messages
            }))
            
        except ObjectDoesNotExist as e:
            await self.send(text_data=json.dumps({
                'action': self.action,
                'errors': e.messages
            }))