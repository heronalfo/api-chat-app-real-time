from django.contrib import admin
from ..models import *

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    ...