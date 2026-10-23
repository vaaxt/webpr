from django import forms
from django.db import transaction

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = UserProfile
        fields = ('avatar', 'city', 'about')
        labels = {
            'avatar': 'Аватар',
            'city': 'Город',
            'about': 'О себе',
        }
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.email = self.cleaned_data['email']

        if commit:
            with transaction.atomic():
                profile.save()
                self.user.save(update_fields=('first_name', 'last_name', 'email'))
                self.save_m2m()

        return profile
