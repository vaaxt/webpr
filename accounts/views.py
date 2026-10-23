from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserProfileForm
from .models import UserProfile


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')


@login_required
def profile_view(request):
    profile = request.user.profile
    return render(
        request,
        'accounts/profile.html',
        {'profile': profile, 'profile_user': request.user},
    )


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные профиля сохранены.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(
        request,
        'accounts/profile_edit.html',
        {'form': form, 'profile': profile},
    )
