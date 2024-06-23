from django.urls import path
from .consumers import * 
from .views import *

urlpatterns = [

    path('chatroom/<str:chatroom>/', ChatroomConsumer.as_asgi()),
    path('chatroom/<str:chatroom>/edit/', ChannelsConsumer.as_asgi()),
    path('invite/<str:username>/', InviteView.as_view()),
    path('chat/<str:chatroom>/', ChatroomConsumer.as_asgi()),


]