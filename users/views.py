from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CreateUser
from .models import Feedback
from django.db.models import Q
from .models import Goal

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('signup')

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()

        # Create profile
        profile = UserProfile(user=user, name=name, date_of_birth=date_of_birth, gender=gender)
        profile.save()

        # Auto-login
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard_redirect') 
        
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
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")
    return render(request, 'users/admin_dashboard.html')

@login_required
def staff_dashboard(request):
    if request.user.userprofile.role != "staff":
        return redirect("dashboard_redirect")
    return render(request, 'users/staff_dashboard.html')

@login_required
def client_dashboard(request):
    if request.user.userprofile.role != "client":
        return redirect("dashboard_redirect")
    return render(request, 'users/client_dashboard.html')

@login_required
def client_profile(request):
    profile=request.user.userprofile
    return render(request, 'users/client_profile.html',{
        'user_obj':request.user,
        'profile':profile

    })

@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']

            # Use email as username
            user = User.objects.create_user(
                username=email, 
                email=email,
                password=password,
            )

            UserProfile.objects.create(
                user=user,
                name=name,
                date_of_birth=form.cleaned_data['date_of_birth'],
                gender=form.cleaned_data['gender'],
                role=form.cleaned_data['role']
            )

            return redirect('manage_users')
        
    else:
        form = CreateUser()

    return render(request, 'users/create_user.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    query = request.GET.get("q")
    users = User.objects.all().select_related('userprofile').order_by("userprofile__name") 

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(userprofile__name__icontains=query))

    return render(request, "users/manage_users.html", {"users": users, "query": query})

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, f"User {user.username} deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    
    return redirect('manage_users')

@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        role = request.POST.get("role")

        user.username = email
        user.email = email

        if password:
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect("edit_user", user_id=user.id)
            user.set_password(password)

        user.save()

        profile.name = name 
        if date_of_birth:
            profile.date_of_birth = date_of_birth
        profile.gender = gender
        profile.role = role
        profile.save()

        messages.success(request, f"User {user.email} updated successfully.")
        return redirect("manage_users")

    initial_data = {
        "name": profile.name,
        "email": user.email,
        "date_of_birth": profile.date_of_birth,
        "gender": profile.gender,
        "role": profile.role,
    }

    return render(request, "users/edit_user.html", {
    "user_obj": user,
    "name": profile.name,
    "email": user.email,
    "date_of_birth": profile.date_of_birth,
    "gender": profile.gender,
    "role": profile.role,
    })

@login_required
def clients_list(request):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")
    clients = UserProfile.objects.filter(role="client").order_by("name")
    return render(request, "users/clients_list.html", {"clients": clients})

@login_required
def client_detail(request, client_id):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")

    client = get_object_or_404(UserProfile, id=client_id, role="client")

    if not client.goals.exists():
        Goal.objects.create(client=client, name="Goal 1", progress=0)
        Goal.objects.create(client=client, name="Goal 2", progress=0)
        Goal.objects.create(client=client, name="Goal 3", progress=0)

    goals = client.goals.all()

    return render(request, "users/client_detail.html", {
        "client": client,
        "goals": goals,
    })

@login_required
def client_feedback(request):
    if request.method == "POST":
        mood = request.POST.get("mood")
        comment = request.POST.get("comment")
        photo = request.FILES.get("photo")

        Feedback.objects.create(
            user=request.user,
            mood=mood,
            comment=comment,
            photo=photo
        )
        return redirect("client_dashboard")
    return render(request, 'users/client_feedback.html')

@login_required
def admin_profile(request):
    profile=getattr(request.user, "userprofile", None)
    return render(request, "users/admin_profile.html",{
        "user_obj": request.user,
        "profile":profile,

    })
