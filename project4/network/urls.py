
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("",include('chat.urls')),
    path("n/login", views.login_view, name="login"),
    path("n/verif", views.verif_view, name="verif"),
    path("n/logout", views.logout_view, name="logout"),
    path("n/register", views.register, name="register"),
    path("<str:username>", views.profile, name='profile'),
    path("n/following", views.following, name='following'),
    path("n/saved", views.saved, name="saved"),
    path("n/createpost", views.create_post, name="createpost"),
    path("n/post/<int:id>/like", views.like_post, name="likepost"),
    path("n/post/<int:id>/unlike", views.unlike_post, name="unlikepost"),
    path("n/post/<int:id>/save", views.save_post, name="savepost"),
    path("n/post/<int:id>/unsave", views.unsave_post, name="unsavepost"),
    path("n/post/<int:post_id>/comments", views.comment, name="comments"),
    path("n/post/<int:post_id>/write_comment",views.comment, name="writecomment"),
    path("n/post/<int:post_id>/delete", views.delete_post, name="deletepost"),
    path("<str:username>/follow", views.follow, name="followuser"),
    path("<str:username>/unfollow", views.unfollow, name="unfollowuser"),
    path("n/post/<int:post_id>/edit", views.edit_post, name="editpost"),
    path("n/chatting", views.chatting, name="chatting"),
    path('search_users/', views.search_users, name='search_users'),
    path("n/admin/", views.admin_panel, name="admin_panel"),
    path("n/admin/user", views.admin_user, name="admin_user"),
    path('n/admin/delete/user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('n/add/user/', views.add_user, name='add_user'),
    path('n/admin/edit/user/<int:user_id>/', views.edit_user, name='edit_user'),
    path("n/admin/post", views.admin_post, name="admin_post"),
    path('n/admin/delete/post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('n/add/post/', views.add_post, name='add_post'),
    path('n/admin/edit/post/<int:post_id>/', views.edit_post, name='edit_post'),
    path("n/admin/comment", views.admin_comment, name="admin_comment"),
    path('n/admin/delete/comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('n/add/comment/', views.add_comment, name='add_comment'),
    path('n/admin/edit/comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
     path("n/admin/room", views.admin_room, name="admin_room"),
    path('n/admin/delete/room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('n/add/room/', views.add_room, name='add_room'),
    path('n/admin/edit/room/<int:room_id>/', views.edit_room, name='edit_room'),
    path("n/admin/message", views.admin_message, name="admin_message"),
    path('n/admin/delete/message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('n/add/message/', views.add_message, name='add_message'),
    path('n/admin/edit/message/<int:message_id>/', views.edit_message, name='edit_message'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

