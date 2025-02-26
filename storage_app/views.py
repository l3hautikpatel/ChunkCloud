from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def index(request): 
    # return HttpResponse("hello Home")
    return render(request,'index.html')


def register(request):
    """
    Handles user registration using the custom registration form.
    Extra fields (full_name, date_of_birth, gender) are collected.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Example: Save full_name in the first_name field.
            user.first_name = form.cleaned_data.get('full_name')
            user.email = form.cleaned_data.get('email')
            user.save()
            # Here you might also create a UserProfile to store date_of_birth and gender.
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    """
    Handles user login using the custom authentication form.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    """
    Logs out the current user.
    """
    logout(request)
    return redirect('login')



def profile(request):
    return render(request, 'profile.html')


# For forgot password functionality, we can use Django’s built-in views.
# You can also customize these in your URL patterns with custom templates.