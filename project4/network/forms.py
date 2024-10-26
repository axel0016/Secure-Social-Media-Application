# forms.py
from django import forms
from .models import *
from chat.models import *

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['creater','content_text', 'content_image', 'privacy']
        widgets = {
            'content_image': forms.FileInput(attrs={'id': 'formFile', 'class': 'form_control'}),
           
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['post', 'commenter','comment_content']
        
        
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_id', 'participants', 'url']  # Add or remove fields as needed


class MessageForm(forms.ModelForm):
    created_by = forms.ModelChoiceField(queryset=User.objects.all())  # Adjust queryset as needed

    class Meta:
        model = Message
        fields = ['chat_room', 'body', 'created_by']


