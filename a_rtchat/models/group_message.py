from django.db import models
from django.contrib.auth.models import User
from .chat_group import ChatGroup
    
class GroupMessage(models.Model):

    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=2000, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(default=0) #0 Normal, 1 Entered , 2 Exit
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    
    class Index:    
        fields = ['sent_at', 'content',]
    
    class Meta:   
        ordering = ['-sent_at',]
        
    def __str__(self):        
        return self.content if self.content else str(self.file)
