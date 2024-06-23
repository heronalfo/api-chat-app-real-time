# Generated by Django 5.0.1 on 2024-06-17 17:34

import shortuuid.main
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_rtchat', '0003_chatgroup_is_private'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='admins', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='group_name',
            field=models.CharField(default='Group message', max_length=30),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='members_edit_group',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chatgroup',
            name='name',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, max_length=128, unique=True),
        ),
    ]