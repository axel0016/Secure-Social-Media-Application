from django.db import models

from network.models import User

class Room(models.Model):
    room_id = models.CharField(max_length=255)
    participants = models.ManyToManyField(User,related_name='rooms')
    room_name = models.CharField(max_length=255,blank=True,null=True)
    room_picture = models.ImageField(upload_to='profile_pic/',blank=True)
    isGroupChat = models.BooleanField(default=False)
    url = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta : 
        ordering = ('-created_at',)
        
    def __str__(self):
        return f'{self.room_id}'

class Message(models.Model):
    chat_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    body = models.TextField()
    created_by = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta : 
        ordering = ('created_at',)
    
    def __str__(self):
        return f'Sender : {self.created_by}, Message : {self.body}'
    