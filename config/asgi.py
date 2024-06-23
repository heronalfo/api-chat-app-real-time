"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path, include
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from a_rtchat import routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({


    'http': django_asgi_app,
    
    'websocket': AllowedHostsOriginValidator(
    
        AuthMiddlewareStack(
        
            URLRouter(
            
                path('ws/', include('a_rtchat.routing'))
            
            )
        
        
        ),
    
    )



})
