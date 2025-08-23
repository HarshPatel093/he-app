from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CreateUser

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
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')

@login_required
def dashboard_redirect(request):
    profile = request.user.userprofile
    if profile.role == 'admin':
        return redirect('admin_dashboard')
    elif profile.role == 'staff':
        return redirect('staff_dashboard')
    else:
        return redirect('client_dashboard')

@login_required
def admin_dashboard(request):
    return render(request, 'users/admin_dashboard.html')

@login_required
def staff_dashboard(request):
    return render(request, 'users/staff_dashboard.html')

@login_required
def client_dashboard(request):
    return render(request, 'users/client_dashboard.html')

@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Use email as username
            user = User.objects.create_user(
                username=email, 
                email=email,
                password=password,
            )

            UserProfile.objects.create(
                user=user,
                date_of_birth=form.cleaned_data['date_of_birth'],
                gender=form.cleaned_data['gender'],
                role=form.cleaned_data['role']
            )

            return redirect('dashboard_redirect')
        
    else:
        form = CreateUser()

    return render(request, 'users/create_user.html', {'form': form})