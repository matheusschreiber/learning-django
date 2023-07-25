from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse

# rooms = [
#   {'id': 1, 'name': 'lets learn python!'},
#   {'id': 2, 'name': 'lets learn python2!'},
#   {'id': 3, 'name': 'lets learn python3!'},
# ]

def loginPage(request):
   page = "login"
   
   if request.user.is_authenticated:
     return redirect('home')
   
   if request.method=='POST':
      username = request.POST.get('username').lower()
      password = request.POST.get('password')

      try:
        user = User.objects.get(username=username)
      except:
        messages.error(request, 'User does not exist')
      
      user = authenticate(request, username=username, password=password)        

      if user is not None:
        login(request, user)
        return redirect('home')
      else:
        messages.error(request, 'Username or password does not match')
   
   context = {'page':page}
   return render(request, 'base/login_register.html', context)

def logoutUser(request):
  logout(request)
  return redirect('home')

def registerPage(request):
  form = UserCreationForm()

  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.username = user.username.lower()
      user.save()
      login(request, user)
      return redirect('home')
    else:
      messages.error(request, 'An error has occurred during registration')

  return render(request, 'base/login_register.html', {'form': form})
   

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    # this property 'topic__name' is builtin to get the field name of topic
    # rooms = Room.objects.filter(topic__name=q)

    # icontains is case sensitive
    # contains is insensitive

    rooms = Room.objects.filter(
       Q(topic__name__icontains=q) |
       Q(name__icontains=q) |
       Q(description__icontains=q)
    )

    topics = Topic.objects.all()
    room_count = rooms.count()

    room_messages = Message.objects.filter(
      Q(room__topic__name__icontains=q) |
      Q(body__icontains=q)
    )

    context = {
      'rooms': rooms,
      'topics': topics,
      'room_count': room_count,
      'room_messages': room_messages
    }

    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
        
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}

    if request.method == 'POST':
      message = Message.objects.create(
        user=request.user,
        room=room,
        body=request.POST.get('body')
      )
      room.participants.add(request.user)
      
      return redirect('room', pk=room.id)

    # return HttpResponse("Room") # i can add response directly like this
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
  user = User.objects.get(id=pk)
  rooms = user.room_set.all()
  room_messages = user.message_set.all()
  topics = Topic.objects.all()

  context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics':topics}
  return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateUser(request):
  form = UserForm(instance=request.user)
  
  if request.method == "POST":
    form = UserForm(request.POST, instance=request.user)
    if form.is_valid():
      form.save()
      return redirect('user-profile', pk=request.user.id)

  
  context={'form': form}
  return render(request, 'base/update-user.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
      topic_name = request.POST.get('topic')
      topic, created = Topic.objects.get_or_create(name=topic_name)

      Room.objects.create(
        host=request.user,
        topic=topic,
        name=request.POST.get('name'),
        description=request.POST.get('description')
      )

      return redirect('home')
      
      
      # here i could do some logic to check if the fields are valid
      
      # or i can use the built in thing
      # form = RoomForm(request.POST)
      # if form.is_valid():
      #   room = form.save(commit=False)
      #   room.host = request.user
      #   room.save()
      #   return redirect('home')

    context={'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  topics = Topic.objects.all()
  
  form = RoomForm(instance=room)

  if not request.user == room.host:
    return HttpResponse('You are not allowed to update this')

  if request.method == "POST":
    topic_name = request.POST.get('topic')
    topic, created = Topic.objects.get_or_create(name=topic_name)

    room.name = request.POST.get('name')
    room.description = request.POST.get('description')
    room.topic = topic
    room.save()

    return redirect('home')

    # form = RoomForm(request.POST, instance=room)
    # if form.is_valid():
    #   form.save()
    #   return redirect('home')
  
  
  
  context = {'form':form, 'topics':topics, 'room': room}
  return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)

  if not request.user == room.host:
    return HttpResponse('You are not allowed to delete this')

  if request.method == "POST":
    room.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
  message = Message.objects.get(id=pk)

  if not request.user == message.user:
    return HttpResponse('You are not allowed to delete this')

  if request.method == "POST":
    message.delete()
    return redirect('home')
  
  return render(request, 'base/delete.html', {'obj': message})