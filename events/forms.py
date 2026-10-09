from django import forms
from .models import Event

class EventForm(forms.ModelForm) :
    class Meta :
        model = Event
        fields = ['title', 'slug', 'summary', 'description', 'poster', 'starts_at', 'is_published']

        widgets = {
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }