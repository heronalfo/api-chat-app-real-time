from django.contrib import admin
from ..models import *

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    ...