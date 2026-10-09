from django.shortcuts import redirect, render, get_object_or_404
from .models import Event
from .forms import EventForm


def event_list(request):
    events = Event.objects.all()
    return render(request, "events/event_list.html", {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, "events/event_detail.html", {'event': event})


def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('events:event_list')
    else:
        form = EventForm()

    return render(request, "events/event_form.html", {'form': form, 'action': 'create'})


def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('events:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, "events/event_form.html", {'form': form, 'action': 'update'})


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        event.delete()
        return redirect('events:event_list')

    return render(request, "events/event_confirm_delete.html", {'event': event})


