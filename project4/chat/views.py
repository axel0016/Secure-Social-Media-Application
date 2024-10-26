from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max,Count
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import Room,User,Message

@login_required
@require_POST
def create_room(request, room_id):
    current_user = request.user
    url = request.POST.get('url','')
    #Getting All the participants in the room
    receiver = request.POST.get('receiver','')
    receiverList = receiver.split(',')
    userList = [current_user]
    for userReceiver in receiverList:
        userList.append(User.objects.get(username=userReceiver))
    #Checking if a room with those participants Exists
    rooms_with_specific_participants = Room.objects.filter(participants__in=userList)\
                                               .annotate(num_participants=Count('participants'))\
                                               .filter(num_participants=len(userList))
    
    rooms_with_specific_participants = rooms_with_specific_participants.filter(num_participants=len(userList))

    if rooms_with_specific_participants.exists():
        room_id_to_render = rooms_with_specific_participants.first().room_id
        return JsonResponse({
            'message':'room created',
            'room_id':room_id_to_render,
            })
    else:
        if len(userList) == 2:
            new_room = Room.objects.create(room_id=room_id,url=url)
        else : 
            new_room = Room.objects.create(room_id=room_id,url=url,isGroupChat=True)
        for myusers in userList:
            new_room.participants.add(myusers)
        room_id_to_render = new_room.room_id
        return JsonResponse({
            'message':'room created',
            'room_id':room_id_to_render,
            })


@login_required
@require_POST
def updateGroupDetails(request):
    room_id = request.POST.get('room_id')
    room = Room.objects.get(room_id=room_id)
    if request.FILES and request.POST.get('groupName'):
        room.room_picture = request.FILES['myfile']
        room.room_name = request.POST.get('groupName')
        room.save()
        return JsonResponse({
            'message':'Saved Both GroupName and Group Image',
        })
    else :
        if request.FILES : 
            room.room_picture = request.FILES['myfile']
            room.save()
            return JsonResponse({
            'message':'Saved Group Image',
            })
        else :
            room.room_name = request.POST.get('groupName')
            room.save()
            return JsonResponse({
            'message':'Saved Group Name',
            })


def get_current_user(request):
    if request.user.is_authenticated:
        # Get details of the logged-in user
        user_details = {
            'username': request.user.username,
        }
        return JsonResponse(user_details)
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)


@login_required
def room(request,room_id):
    #to return the current room
    try:
        current_room = Room.objects.get(room_id=room_id)
    except Room.DoesNotExist:
        return HttpResponseRedirect(reverse('chatting'))
    #to return all the mssages of a room
    if (current_room.participants.filter(username=request.user.username).exists()):
        room = Room.objects.get(room_id=room_id)
        room_messages = Message.objects.filter(chat_room=room.pk).order_by('created_at')
        #To return the list of users, so i can do a new room
        allUsers = User.objects.exclude(username=request.user.username).order_by("username")
        #To show all the rooms a user got
        userLogged = request.user.id
        user_rooms_info = []
        user_rooms = Room.objects.filter(participants=userLogged).annotate(last_message_created_at=Max('messages__created_at')).order_by('-last_message_created_at')
        for room in user_rooms:
            if (room.isGroupChat):
                participants_excluding_me = room.participants.exclude(username = request.user.username)
                participants_last_names = ', '.join(participant.last_name for participant in participants_excluding_me)
                groupImage = '/media/profile_pic/groupchat.png'
                last_message = room.messages.last()
                room_info = {
                    'room_id': room.room_id,
                    'participants_last_names' : room.room_name if room.room_name else participants_last_names,
                    'group_pfp' : room.room_picture.url if room.room_picture else groupImage,
                    'last_message_body': last_message.body if last_message else None,
                    'last_message_created_at': last_message.created_at if last_message else None,
                    'last_message_created_by': last_message.created_by if last_message else None,
                    'last_message_id': last_message.id if last_message else None,
                    'isGroupChat' : True
                }

            else: 
                second_participant = room.participants.exclude(id=userLogged).first()
                if second_participant:
                    last_message = room.messages.last()
                    room_info = {
                        'room_id': room.room_id,
                        'second_participant_username': second_participant.username,
                        'second_participant_first_name': second_participant.first_name,
                        'second_participant_profile_pic': second_participant.profile_pic.url,
                        'second_participant_last_name': second_participant.last_name,
                        'last_message_body': last_message.body if last_message else None,
                        'last_message_created_at': last_message.created_at if last_message else None,
                        'last_message_created_by': last_message.created_by if last_message else None,
                        'last_message_id': last_message.id if last_message else None,
                        'isGroupChat' : False
                    }
            user_rooms_info.append(room_info)
        #to retrieve infos about the second room member
        if current_room.isGroupChat:
            participants_inRoom = current_room.participants.exclude(username = request.user.username)
            participants_inRoom_last_names = ', '.join(participant.last_name for participant in participants_inRoom)
            groupImagepfp = '/media/profile_pic/groupchat.png'
            return render(request,'chat/partials/messaging.html',{
                'room': current_room,
                'room_messages':room_messages,
                'allUsers': allUsers,
                'user_rooms_info': user_rooms_info,
                'participants_inRoom_last_names':current_room.room_name if current_room.room_name else participants_inRoom_last_names,
                'groupImagepfp' : current_room.room_picture.url if current_room.room_picture else groupImagepfp,
            })
        else:
            second_user = current_room.participants.exclude(id=userLogged).first()
            return render(request,'chat/partials/messaging.html',{
                'room': current_room,
                'room_messages':room_messages,
                'allUsers': allUsers,
                'user_rooms_info': user_rooms_info,
                'second_user': second_user
            })
    else:
        return HttpResponseRedirect(reverse('chatting'))