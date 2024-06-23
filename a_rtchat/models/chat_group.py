from django.db import models
from django.contrib.auth.models import User
import shortuuid

class ChatGroup(models.Model):

    name = models.CharField(max_length=128, unique=True, default=shortuuid.uuid)
    group_name = models.CharField(max_length=30, default='Group message')
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='members_in_group', blank=True)
    admins = models.ManyToManyField(User, related_name='admins', blank=True)
    members_edit_group = models.BooleanField(default=False)  
    is_private = models.BooleanField(default=False)   
    
    def __str__(self):    
        return self.group_name    