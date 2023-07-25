from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room
from .forms import RoomForm
from .models import Topic

# from django.http import HttpResponse

# rooms = [
#   {'id': 1, 'name': 'lets learn python!'},
#   {'id': 2, 'name': 'lets learn python2!'},
#   {'id': 3, 'name': 'lets learn python3!'},
# ]


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

    context = {
      'rooms': rooms,
      'topics': topics,
      'room_count': room_count,
    }

    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
        
    context = {'room': room}

    # return HttpResponse("Room") # i can add response directly like this
    return render(request, 'base/room.html', context)

def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
      # here i could do some logic to check if the fields are valid
      
      # or i can use the built in thing
      form = RoomForm(request.POST)
      if form.is_valid():
        form.save()
        return redirect('home')

    context={'form': form}
    return render(request, 'base/room_form.html', context)


def updateRoom(request, pk):
  room = Room.objects.get(id=pk)
  form = RoomForm(instance=room)

  if request.method == "POST":
    form = RoomForm(request.POST, instance=room)
    if form.is_valid():
      form.save()
      return redirect('home')
  
  context = {'form':form}
  return render(request, 'base/room_form.html', context)

def deleteRoom(request, pk):
  room = Room.objects.get(id=pk)
  if request.method == "POST":
    room.delete()
    return redirect('home')
  return render(request, 'base/delete.html', {'obj': room})