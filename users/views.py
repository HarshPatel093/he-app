from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
            return redirect('signup')

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()

        # Create profile
        profile = UserProfile(user=user, date_of_birth=date_of_birth, gender=gender)
        profile.save()

        # Auto-login
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # This will be your dashboard page

    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # later we make dashboard
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
