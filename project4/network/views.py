from pyexpat.errors import messages
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Max,Count
import json
from django.shortcuts import get_object_or_404
from .models import *
from chat.models import *
from .forms import *
from django.contrib.auth.models import Group



def index(request):
    
    followings = []
    suggestions = []
    
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        user_posts = Post.objects.filter(creater=request.user).order_by('-date_created')  #zedtha
        public_posts = Post.objects.filter(privacy='public').order_by('-date_created')  #zedtha
        following_user = Follower.objects.filter(followers=request.user).values('user')  
        private_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')  #zedtha
        print(following_user)
        is_admin = request.user.groups.filter(name='administrateur').exists()

    # Concaténer les deux listes pour les afficher ensemble
        posts = public_posts | private_posts | user_posts #zedtha
       
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        all_suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")
    else: #zedtha
        all_posts = Post.objects.filter(privacy='public').order_by('-date_created')
        all_suggestions=[]
        is_admin = False
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,
        "all_suggestions": all_suggestions,
        "page": "all_posts",
        'profile': False,
        "is_admin":is_admin,
    })
from django.core.mail import send_mail
import random
import string
def verif_view(request):
    if request.method == "POST":
        code2 = request.POST.get("code")
        codee = request.session.get("verification_code")  # Récupérer le code de vérification stocké en session
        if codee and code2 == codee:  # Vérifier si les codes correspondent
            del request.session["verification_code"]  # Supprimer le code de vérification de la 
            username=request.session.get("user_username")
            password=request.session.get("user_password")
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/verif.html", {"error": "Code incorrect"})
    else:
        username = request.session.get("username")
        password = request.session.get("password")
        user_email=request.session.get("user_email")
        sujet = "2 step verification"
        caracteres = string.ascii_letters + string.digits
        code = ''.join(random.choice(caracteres) for _ in range(5))
        request.session["verification_code"] = code  # Stocker le code de vérification en session
        message = f"Votre code est {code}"
        send_mail(sujet, message, 'hallahmoha@gmail.com', [user_email])
        return render(request, "network/verif.html",{"mail":user_email})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
            username=user.username
            user = authenticate(request, username=username, password=password)

            if user is not None:
                request.session["user_username"] = username
                request.session["user_password"] = password
                if user.email:  # Vérifier si l'utilisateur a un e-mail
                    request.session["user_email"] = user.email  # Stocker l'e-mail dans la session
                return HttpResponseRedirect(reverse("verif"))
            else:
                return render(request, "network/login.html", {"message": "Nom d'utilisateur ou mot de passe invalide."})
        except User.DoesNotExist:
                return render(request, "network/login.html")
    else:
        return render(request, "network/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        print(f"--------------------------Profile: {profile}----------------------------")
        cover = request.FILES.get('cover')
        print(f"--------------------------Cover: {cover}----------------------------")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover           
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



def profile(request, username):
    user = User.objects.get(username=username)
    all_posts = Post.objects.filter(creater=user,privacy='public').order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        all_suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")
        public_posts = Post.objects.filter(privacy='public', creater=user).order_by('-date_created')
        
        is_admin = request.user.groups.filter(name='administrateur').exists()
        
        if request.user in Follower.objects.get(user=user).followers.all():
            # If the user is a follower, include private posts as well
            private_posts = Post.objects.filter(privacy='private', creater=user).order_by('-date_created')
            posts = public_posts | private_posts
            follower = True
    
    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    follower_user = list(Follower.objects.get(user=user).followers.all())
    following_user = list(Follower.objects.filter(followers=user).all())

    return render(request, 'network/profile.html', {
        "username": user,
        "posts": posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "all_suggestions": all_suggestions,########
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count,
        "follower_user": follower_user,
        "following_user": following_user,
        "is_admin":is_admin,
    })


def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
            
        is_admin = request.user.groups.filter(name='administrateur').exists()
        
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "following",
            "is_admin":is_admin,
        })
    else:
        return HttpResponseRedirect(reverse('login'))

def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by('-date_created')

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        is_admin = request.user.groups.filter(name='administrateur').exists()
        
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "saved",
            "is_admin":is_admin,
        })
    else:
        return HttpResponseRedirect(reverse('login'))
        


@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        privacy=request.POST.get('privacy') #zedtha
        try:
            post = Post.objects.create(creater=request.user, content_text=text, content_image=pic,privacy=privacy) #zedtha privacy
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")

@login_required
@csrf_exempt

#layout.js zedt f .popup <select> t3 privacy
def edit_post(request, post_id):
    if request.method == 'POST':
        priv = request.POST.get('priv') #zedtha
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        text = request.POST.get('text')
        print("++++++++++++++++++++++++++++++++")
        print(priv)
        # Vérifier l'existence du post
        post = get_object_or_404(Post, id=post_id)
        
        try:
            post.privacy=priv  #zedtha
            post.content_text = text
            
            # Vérifier si une nouvelle image est fournie
            if img_chg != 'false' and pic:
                post.content_image = pic
            
            post.save()
            
            post_text = post.content_text if post.content_text else False
            post_image = post.img_url() if post.content_image else False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
            # Utiliser logger.error pour enregistrer l'erreur dans les journaux
            print('-----------------------------------------------')
            print(e)
            print('-----------------------------------------------')
            return JsonResponse({
                "success": False
            })
    else:
        return JsonResponse({
            "success": False,
            "error": "Method must be 'POST'"
        })

@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Follower: {request.user}......................")
            try:
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Unfollower: {request.user}......................")
            try:
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            comment = data.get('comment_text')
            post = Post.objects.get(id=post_id)
            try:
                newcomment = Comment.objects.create(post=post,commenter=request.user,comment_content=comment)
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Exception as e:
                return HttpResponse(e)
    
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by('-comment_time').all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delet = post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

def admin_panel(request):
    is_admin = request.user.groups.filter(name='administrateur').exists()
    nbuser=User.objects.all().count()
    nbro=Room.objects.all().count()
    nbpos=Post.objects.all().count()
    nbcom=Comment.objects.all().count()
    return render(request,"network/admin.html",{"is_admin":is_admin,"nbuser":nbuser,"nbro":nbro,"nbcom":nbcom,"nbpos":nbpos})

def admin_user(request):
    users=User.objects.all()
    is_admin = request.user.groups.filter(name='administrateur').exists()
    contexe={
         'users':users,
        'is_admin':is_admin,
    }
    
    return render(request,"network/admin_panel/admin_user.html",contexe)


def delete_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.delete()
    except User.DoesNotExist:
        pass
    return redirect('admin_user')

from django.core.files.storage import default_storage
def add_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["first"]
        lname = request.POST["last"]
        password = request.POST["password"]
        confirmation = request.POST["confirm"]
        profile = request.FILES.get("profile")
        cover = request.FILES.get('cover')
        selected_groups = request.POST.getlist('groups')  # Get selected groups from the form

        if username and fname and lname and email and password:
            if password != confirmation:
                return render(request, "network/admin_panel/add_user.html", {
                    "message": "Passwords must match."
                })

            try:
                user = User.objects.create_user(username, email, password)
                user.first_name = fname
                user.last_name = lname

                # Vérifier et sauvegarder le fichier téléchargé pour le profil
                if profile:
                    profile_path = default_storage.save(profile.name, profile)
                    user.profile_pic = profile_path
                else:
                    user.profile_pic = "profile_pic/no_pic.png"

                # Assurez-vous de sauvegarder le fichier téléchargé pour la couverture
                if cover:
                    cover_path = default_storage.save(cover.name, cover)
                    user.cover = cover_path

                user.save()
                
                # Assign the user to selected groups
                user.groups.set(Group.objects.filter(pk__in=selected_groups))

                Follower.objects.create(user=user)
                return HttpResponseRedirect(reverse("admin_user"))
            except IntegrityError:
                return render(request, "network/admin_panel/add_user.html", {
                    "message": "Username already exists."
                })
        else:
            return render(request, "network/admin_panel/add_user.html", {
                "message": "Complete the form!"
            })

    # Pass all groups to the template context
    all_groups = Group.objects.all()
    return render(request, "network/admin_panel/add_user.html", {"all_groups": all_groups})


def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    available_groups = Group.objects.all()
    selected_groups = user.groups.all()
    message_err = ""

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first')
        last_name = request.POST.get('last')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        profile = request.FILES.get("profile")
        cover = request.FILES.get('cover')

        if username and first_name and last_name and email and password:
            if password == confirm:
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.set_password(password)

                if profile is not None:
                    user.profile_pic = default_storage.save(profile.name, profile)
                else:
                    user.profile_pic = "profile_pic/no_pic.png"

                if cover is not None:
                    user.cover = default_storage.save(cover.name, cover)
                else:
                    user.cover = None

                user.save()

                # Update user groups
                user.groups.set(Group.objects.filter(pk__in=request.POST.getlist('groups')))

               
                return HttpResponseRedirect(reverse("admin_user"))
            else:
                message_err = "Passwords must match."
        else:
            message_err = "Completez le formulaire !"

    return render(request, 'network/admin_panel/edit_user.html', {
        'form': user,
        'message_err': message_err,
        'available_groups': available_groups,
        'selected_groups': selected_groups
    })
def admin_post(request):
    posts=Post.objects.all()
    is_admin = request.user.groups.filter(name='administrateur').exists()
    contexe={
        
         'is_admin':is_admin,
        'posts':posts,
    }
    return render(request,"network/admin_panel/admin_post.html",contexe)

def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.creater = form.cleaned_data['creater']
            post.save()
            
            return redirect('admin_post') 
    else:
        form = PostForm()
    return render(request, 'network/admin_panel/add_post.html', {'form': form})


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('admin_post') 

    else:
        form = PostForm(instance=post)
    return render(request, 'network/admin_panel/edit_post.html', {'form': form, 'post': post})


def delete_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        post.delete()
    except User.DoesNotExist:
        pass
    return redirect('admin_post')

def admin_comment(request):
    comments=Comment.objects.all()
    is_admin = request.user.groups.filter(name='administrateur').exists()
    contexe={
         'is_admin':is_admin,
        'comments':comments,
    }
    return render(request,"network/admin_panel/admin_comment.html",contexe)

def add_comment(request):
    
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commenter =form.cleaned_data['commenter']
            comment.post.comment_count+=1
            comment.post.save()
            comment.save()
            return redirect('admin_comment')  # Adjust the redirection URL as needed
    else:
        form = CommentForm()
    
    return render(request, 'network/admin_panel/add_comment.html', {'form': form})

def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('admin_comment')  # Adjust the redirection URL as needed
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'network/admin_panel/edit_comment.html', {'form': form, 'comment': comment})

def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
        comment.post.comment_count-=1
        comment.post.save()
        comment.delete()
    except Comment.DoesNotExist:
        pass
    return redirect('admin_comment')

def admin_room(request):
    rooms=Room.objects.all()
    is_admin = request.user.groups.filter(name='administrateur').exists()
    contexe={
         'is_admin':is_admin,
        'rooms':rooms,
    }
    return render(request,"network/admin_panel/admin_room.html",contexe)

def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            return redirect('admin_room')
    else:
        form = RoomForm()
    return render(request, 'network/admin_panel/add_room.html', {'form': form})

def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('admin_room')

    else:
        form = RoomForm(instance=room)
    return render(request, 'network/admin_panel/edit_room.html', {'form': form, 'room': room})



def delete_room(request, room_id):
    try:
        room = Room.objects.get(pk=room_id)
        room.delete()
    except Room.DoesNotExist:
        pass
    return redirect('admin_room')

def admin_message(request):
    messages=Message.objects.all()
    is_admin = request.user.groups.filter(name='administrateur').exists()
    contexe={
         'is_admin':is_admin,
        'messages':messages,
    }
    return render(request,"network/admin_panel/admin_message.html",contexe)


def add_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save()
            return redirect('admin_message')
    else:
        form = MessageForm()
    return render(request, 'network/admin_panel/add_message.html', {'form': form})

def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('admin_message')

    else:
        form = MessageForm(instance=message)
    return render(request, 'network/admin_panel/edit_message.html', {'form': form, 'message': message})


def delete_message(request, message_id):
    try:
        message = Message.objects.get(pk=message_id)
        message.delete()
    except Message.DoesNotExist:
        pass
    return redirect('admin_message')

#-----------------------------------------------
def chatting(request):
    if request.user.is_authenticated:
        is_admin = request.user.groups.filter(name='administrateur').exists()
        allUsers = User.objects.exclude(username=request.user.username).order_by("username")
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
                        'last_message_id': last_message.id if last_message else None,
                        'isGroupChat' : False
                    }
            user_rooms_info.append(room_info)
        return render(request, "chat/partials/chat_page.html", {
            "allUsers": allUsers,
            'user_rooms_info': user_rooms_info,
            'is_admin':is_admin,
        })
    else:
        return HttpResponseRedirect(reverse('login'))
    
def showMessaging(request):
    return render(request,"chat/partials/messaging.html",{})

def search_users(request):
    if request.user.is_authenticated:
        query = request.GET.get('query', '')
        print("im here")
        users = User.objects.exclude(username=request.user.username).filter(username__startswith=query)
        user_list = [{'username': user.username,
                      'profile_pic' : user.profile_pic.url,
                      'first_name' : user.first_name,
                      'last_name' : user.last_name
                      } 
                      for user in users]
        return JsonResponse(user_list, safe=False)
    else : 
        return HttpResponseRedirect(reverse('login'))
    
#----------------------------------------------------------------------