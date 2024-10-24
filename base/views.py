from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.urls import is_valid_path
from urllib.parse import urlparse

# Create your views here.
def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')    

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')


    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user_info = form.save()
            messages.info(request, 'Thanks you for registering, you are now logged in!!!')            
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
            
            return redirect('home')
        else:
            messages.error(request, 'An error  occured during registration')

    return render(request, 'base/login_register.html', {'form': form})

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
                                )
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
        )
    # print(Message.objects.get(room))    

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
      
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_message,
        'topics': topics,

    }
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateProfile(request, pk):
    user = request.user
    form = UserForm(instance=user)
    context = {
        'form': form
    }

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/edit-user.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        Room.objects.create(
            name=name, topic=topic, description=description, host=request.user
        )

        return redirect('home')
    context = {'form': form, 'topics': Topic.objects.all()}
    return render(request, 'base/create-room.html', context)
    
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!!')  
    
    if request.method == 'POST':
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        topic_name = request.POST.get('topic')
        name = request.POST.get('name')
        description = request.POST.get('description')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST)

        room.name = name
        room.topic=topic
        room.description=description
        room.host = request.user
        room.save()

        # Room.objects.create(
        #     host=request.user,
        #     name=name,
        #     topic=topic,
        #     description=description,
        # )
        
        return redirect('home')
    
    context = {'form': form, 'topics': Topic.objects.all(), 'topic':room.topic.name}
    return render(request, 'base/room_form.html', context) 

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    room_url = f'/room/{message.room.id}'
    if request.user != message.user:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        message.delete()
        return HttpResponseRedirect(room_url)
    return render(request, 'base/delete.html', {'obj': message, 'room_url': room_url})

@login_required(login_url='login')
def deleteMessageInHome(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


