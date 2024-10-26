from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('api/create-room/<str:room_id>/', views.create_room, name='create-room'),
    path('api/updateGroupDetails/', views.updateGroupDetails, name='updateGroupDetails'),
    path('get-current-user/', views.get_current_user, name='get_current_user'),
    path('n/chatting/<str:room_id>/', views.room, name='room'),
]
