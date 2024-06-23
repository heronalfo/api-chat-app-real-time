from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.models import User
from ..managers import ChatGroupManager
from ..models import ChatGroup, GroupMessage

class MessageManager(ChatGroupManager):
    def __init__(self, user_id: int, group_id: int):
        super().__init__(user_id, group_id)
        
    @database_sync_to_async
    def get_messages(self) -> GroupMessage:
        return GroupMessage.objects.all().filter(chat_group=group_id, is_deleted=False)

    @database_sync_to_async
    def send_message(self, data: dict) -> str:
        """
        Handles sending new messages to the group.
        
        Parameters:
        data (dict): Dictionary with message data (content)
        
        Returns:
        str: Success message
        """
        content = data.get('content')
        
        if not content:
            raise ValidationError('This field ["content"] is required')
        
        if len(content) > 2000:
            raise ValidationError('This field ["content"] cannot receive more than 2000 characters')

        chat_group = self.get_chat_group()

        GroupMessage.objects.create(content=content, sender_id=self.user_id, chat_group=chat_group)
        return 'Message sent successfully'
    
    @database_sync_to_async
    def send_special_message(self, type: int) -> str:
        """
        Handles sending new messages to the group.
        
        Parameters:
        type (int): Type of message
        
        Returns:
        str: Success message
        """
        
        chat_group = self.get_chat_group()
        user = User.objects.get(id=self.user_id)
        
        if type == 1:
            content = f'{user.username} joined the group'
            
        elif type == 2:
            content = f'{user.username} left the group'

        GroupMessage.objects.create(content=content, sender_id=self.user_id, chat_group=chat_group, type=type)
        return 'Message sent successfully'
        
    @database_sync_to_async
    def send_message_file(self, file):
        chat_group = self.get_chat_group()
        GroupMessage.objects.create(sender=self.user_id, file=file, chat_group=chat_group)
        
        return 'File uploaded successfully'
    
    @database_sync_to_async
    def delete_message(self, data: dict) -> str:
        """
        Handles deleting a message in the group.
        
        Parameters:
        data (dict): Dictionary with message ID
        
        Returns:
        str: Success message
        """
        message_id = data.get('id')
        
        if not message_id:
            raise ValidationError('This field ["id"] is required')
        
        try:
            message = GroupMessage.objects.get(id=message_id)
        except ObjectDoesNotExist:
            raise ValidationError('The message does not exist')
        
        if message.sender_id != self.user_id and not self.chat_group.admins.filter(id=self.user_id).exists():
            raise PermissionDenied('You do not have permission to delete this message')
        
        message.is_deleted = True
        message.save()
        return 'Message deleted successfully'
    
    @database_sync_to_async
    def edit_message(self, data: dict) -> str:
        """
        Handles editing a message in the group.
        
        Parameters:
        data (dict): Dictionary with message ID and new content
        
        Returns:
        str: Success message
        """
        message_id = data.get('id')
        content = data.get('content')
        
        if not message_id:
            raise ValidationError('This field ["id"] is required')
        
        if not content:
            raise ValidationError('This field ["content"] is required')
        
        if len(content) > 2000:
            raise ValidationError('This field ["content"] cannot receive more than 2000 characters')
        
        try:
            message = GroupMessage.objects.get(id=message_id)
        except ObjectDoesNotExist:
            raise ValidationError('The message does not exist')
        
        if message.sender_id != self.user_id and not self.chat_group.admins.filter(id=self.user_id).exists():
            raise PermissionDenied('You do not have permission to edit this message')
        
        message.content = content
        message.is_edited = True
        message.save()
        return 'Message edited successfully'
    
    @database_sync_to_async
    def add_or_remove_user_online(self, user, connect: bool):
        """
        Adds or removes a user from the online users list.
        
        Parameters:
        user: The user to add or remove.
        connect (bool): True to add, False to remove.
        """
        chat_group = self.get_chat_group()
        
        if connect:
            chat_group.users_online.add(user)
        else:
            chat_group.users_online.remove(user)
    
    @database_sync_to_async
    def get_count_users_online(self) -> int:
        """
        Gets the count of online users in the group.
        
        Returns:
        int: The count of online users.
        """
        chat_group = self.get_chat_group()
        return chat_group.users_online.count()