from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('', views.home, name='home'),
    path('room/<str:pk>', views.room, name='room'),
    path('profile/<str:pk>', views.userProfile, name='user-profile'),
    path('update-profile/<str:pk>', views.updateProfile, name='update-profile'),
    path('update-room/<str:pk>', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>', views.deleteRoom, name='delete-room'),
    path('delete-message/<str:pk>', views.deleteMessage, name='delete-message'),
    path('delete-message-in-home/<str:pk>', views.deleteMessageInHome, name='delete-message-in-home'),
    path('create-room/', views.createRoom, name='create-room'),
    path('topics', views.topicsPage, name='topics')
]
