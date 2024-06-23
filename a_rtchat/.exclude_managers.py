from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from typing import Union, List
from .models import ChatGroup

class ChatGroupManager:

    def __init__(self, user_id: int, group_id: int = None):
        self.user_id = user_id
        self.group_id = group_id

    def get_chat_group(self) -> ChatGroup:
        try:
            chat_group = ChatGroup.objects.get(id=self.group_id)
            return chat_group
        except ObjectDoesNotExist:
            raise ValidationError('The group does not exist')

    def check_admin_permissions(self, chat_group: ChatGroup):
        if not chat_group.admins.filter(id=self.user_id).exists():
            raise PermissionDenied("You do not have permission to perform this action")

    @database_sync_to_async
    def create_group(self, data: dict) -> str:
        """
        Creates a chat group if validation passes.

        Parameters:
        data (dict): Data containing group_name and optionally description.

        Returns:
        str: Success message.
        """
        errors = []

        group_name = data.get('group_name')

        if not group_name:
            raise ValidationError('This field ["group_name"] is required')

        if len(group_name) > 30:
            errors.append('This field ["group_name"] cannot receive more than 30 characters')

        if errors:
            raise ValidationError(errors)

        chat_group = ChatGroup.objects.create(
            group_name=group_name,
            description=data.get('description', '')
        )

        # Add the creator as an admin and a member
        chat_group.admins.add(self.user_id)
        chat_group.members.add(self.user_id)

        return 'Group created successfully'

    @database_sync_to_async
    def delete_group(self) -> str:
        """
        Deletes a chat group if it exists and the user has admin permissions.

        Returns:
        str: Success message.
        """
        chat_group = self.get_chat_group()
        self.check_admin_permissions(chat_group)
        chat_group.delete()
        return 'Group removed successfully'

    @database_sync_to_async
    def edit_group(self, data: dict) -> str:
        """
        Edits a chat group if it exists and the user has admin permissions.

        Parameters:
        data (dict): Data containing the ID of the group to edit and new values.

        Returns:
        str: Success message.
        """
        chat_group = self.get_chat_group()
        self.check_admin_permissions(chat_group)

        errors = []

        if 'group_name' in data:
            group_name = data['group_name']
            if len(group_name) > 30:
                errors.append('This field ["group_name"] cannot receive more than 30 characters')
            else:
                chat_group.group_name = group_name

        if 'description' in data:
            chat_group.description = data['description']

        if errors:
            raise ValidationError(errors)

        chat_group.save()
        return 'Group updated successfully'

    @database_sync_to_async
    def remove_member(self, member_id: int) -> str:
        """
        Remove a member from a chat group.

        Parameters:
        member_id (int): ID of the member to be removed.

        Returns:
        str: Success message if the member is removed.
        """
        chat_group = self.get_chat_group()
        if member_id not in chat_group.members.all():
            return ValidationError('It is not possible to remove this admin because he is not a member')
            
        self.check_admin_permissions(chat_group)
        chat_group.members.remove(member_id)
        return 'Member removed successfully'

    @database_sync_to_async
    def add_admin(self, member_id: int) -> str:
        """
        Add an admin to a chat group.

        Parameters:
        member_id (int): ID of the member to be added as an admin.

        Returns:
        str: Success message if the admin is added.
        """
        chat_group = self.get_chat_group()
        
        if member_id not in chat_group.members.all():
            return ValidationError('It is not possible to add this admin because he is not a member')
            
        self.check_admin_permissions(chat_group)
        chat_group.admins.add(member_id)
        return 'Admin added successfully'

    @database_sync_to_async
    def remove_admin(self, admin_id: int) -> str:
        """
        Remove an admin from a chat group.

        Parameters:
        admin_id (int): ID of the admin to be removed.

        Returns:
        str: Success message if the admin is removed.
        """
        chat_group = self.get_chat_group()
        self.check_admin_permissions(chat_group)
        chat_group.admins.remove(admin_id)
        return 'Admin removed successfully'