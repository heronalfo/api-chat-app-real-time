from django.test import TestCase
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from ..consumers import ChatroomConsumer
from django.contrib.auth.models import User
from ..models import *

class AsyncChatConsumersTest(TestCase):

    def setUp(self):
    
        # Criando uma sala para testes
        self.chatroom = ChatGroup.objects.create(name='ChatroomTests', description='Chatroom for Tests')
        
        # Criando um usuário para testes
        self.user = User.objects.create_user(username='user-tests', password='_Abc123456')
        
        # Comunicator principal para a conexão Websocket
        self.communicator = WebsocketCommunicator(ChatroomConsumer, f'chatroom/{self.chatroom.name}/')
                
        # Conexão Aberta
        self.connect, self._ = communicator.connect()
        
    @database_sync_to_async
    def create_message(self, content: str):
        message = GroupMessage.objects.create(chat_group=self.chatroom, sender=self.user, content=content)
        
        return message
        
    async def test_websocket_connection_open_is_true(self):
    
        self.assertEqual(self.connect, True)
    
    async def test_chat_consumer_receive_message(self):
                                    
        await self.communicator.send_json_to({'action': 'create', 'content': 'Hello, world!'})        
        response = await self.communicator.receive_json_from()
        
        self.assertEqual(response, 0)
        
    async def test_chat_consumer_edit_message(self):
    
        message = await self.create_message(content='Hell, word!')
        
        await self.communicator.send_json_to({'action': 'update', 'id': message.id, 'content': 'Hello, world!'})
        response = await self.communicator.receive_json_from()
        
        self.assertEqual(message.is_edited, 1)
        self.assertEqual(response, 0)
      
    async def test_chat_consumer_delete_message(self):
    
        message = await self.create_message(content='Hello, world!')
        await self.communicator.send_json_to({'action': 'delete', 'id': message.id})
        response = await self.communicator.receive_json_from()
        
        self.assertEqual(message.is_deleted, 1)
        self.assertEqual(response, 0)
        
    async def test_chat_consumer_online_users(self):
    
        await self.communicator.send_json_to({'action': 'online_user_count'})
        response = await self.communicator.receive_json_from()
        self.assertEqual(response, 0)
        
    async def test_chat_consumer_action_not_allowed(self):
    
        await self.communicator.send_json_to({'action': 'method_not_allowed'})
        response = await self.communicator.receive_json_from()
        self.assertIn(response['message'], 'Action Not Allowed')
      
    
         