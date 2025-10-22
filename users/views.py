from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserProfile
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CreateUser
from .models import Feedback
from django.db.models import Q
from .models import Goal, GoalType
from django.urls import reverse
from .forms import ShiftForm
from .models import Shift
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.db.models.functions import TruncWeek
from datetime import timedelta, datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
from django.utils import timezone
from users.models import Shift, UserProfile
from django.template.loader import get_template 
from io import BytesIO
from django.utils.timezone import localtime
from users.models import Shift, UserProfile, StaffNote 

from collections import defaultdict

from datetime import datetime
from django.utils import timezone
import calendar


def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        date_of_birth = request.POST.get('date_of_birth')

        if password != confirm_password:
            messages.error(request, "Passwords do not match", extra_tags="signup")
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists!", extra_tags="signup")
            return redirect('signup')

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()

        # Create profile
        profile = UserProfile(user=user, name=name, date_of_birth=date_of_birth)
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
            messages.error(request, "Invalid credentials!", extra_tags="login")
            return redirect("login")

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
def month_bounds(year:int, month:int):
    start = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
    if month == 12: 
        nxt = datetime(year +1, 1,1, tzinfo=timezone.get_current_timezone())
    else:
        nxt = datetime(year, month+1, 1, tzinfo=timezone.get_current_timezone())
    return start, nxt
@login_required
def admin_dashboard(request):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")
    
    now = timezone.now()
    param = request.GET.get("month")
    if param:
        try:
            year, month = map(int, param.split("-"))
        except Exception:
            year, month = now.year, now.month
    else:
        year, month = now.year, now.month
    start_of_month, next_month= month_bounds(year, month) 

    

    monthly_goals = Goal.objects.filter(
        created_at__gte=start_of_month, created_at__lt=next_month
    )

    goal_week_data = {f"Week {i+1}": 0 for i in range(4)}

    for goal in monthly_goals:
        local_date = localtime(goal.created_at).date()
        day_of_month = local_date.day

        week_number = ((day_of_month - 1) // 7) + 1
        if 1 <= week_number <= 4:
            goal_week_data[f"Week {week_number}"] += 1

    goal_labels = list(goal_week_data.keys())
    goal_data = list(goal_week_data.values())
    
    monthly_feedback = Feedback.objects.filter(
        created_at__gte=start_of_month, created_at__lt=next_month
    )

    feedback_week_data = {f"Week {i+1}": 0 for i in range(4)}

    for fb in monthly_feedback:
        local_date = localtime(fb.created_at).date()
        day_of_month = local_date.day
        week_number = ((day_of_month - 1) // 7) + 1
        if 1 <= week_number <= 4:
            feedback_week_data[f"Week {week_number}"] += 1

    feedback_labels = list(feedback_week_data.keys())
    feedback_data = list(feedback_week_data.values())

    goal_type_summary = (
        Goal.objects.filter(created_at__gte=start_of_month, created_at__lt=next_month)
        .values('goal_type__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    goal_type_labels = [item['goal_type__name'] if item['goal_type__name'] else 'Uncategorized' for item in goal_type_summary]
    goal_type_data = [item['total'] for item in goal_type_summary]


    staff_feedbacks = Feedback.objects.filter(
    is_staff_feedback=True,
    created_at__gte=start_of_month,
    created_at__lt=next_month)

    staff_per_week = defaultdict(set)

    for fb in staff_feedbacks:
        local_date = localtime(fb.created_at).date()
        day_of_month = local_date.day
        week_number = ((day_of_month - 1) // 7) + 1
        if 1 <= week_number <= 4:
            staff_per_week[f"Week {week_number}"].add(fb.user.id)

    staff_week_data = {f"Week {i+1}": len(staff_per_week.get(f"Week {i+1}", set())) for i in range(4)}

    staff_labels = list(staff_week_data.keys())
    staff_data = list(staff_week_data.values())

    month_name = today.strftime("%B %Y")

    
    options=[]
    cur_y, cur_m = now.year, now.month
    for k in range(12):
        m = cur_m -k
        y = cur_y
        while m<= 0:
            m += 12
            y -= 1
        value=f"{y:04d}-{m:02d}"
        label=f"{calendar.month_name[m]} {y}"
        


    context = {
        'goal_labels': goal_labels,
        'goal_data': goal_data,
        "feedback_labels": feedback_labels,
        "feedback_data": feedback_data,
        'goal_type_labels': goal_type_labels,
        'goal_type_data': goal_type_data,
        'staff_labels': staff_labels,
        'staff_data': staff_data,
        'month_name': month_name,
    }
    return render(request, 'users/admin_dashboard.html', context)

@login_required
def staff_dashboard(request):
    if request.user.userprofile.role != "staff":
        return redirect("dashboard_redirect")
    staff_id = request.user.userprofile
    today = timezone.localdate()
    
    shifts = Shift.objects.filter(
        staff=staff_id,
        date = today
    ).prefetch_related("clients")
    
    client_shift_data = []
    for shift in shifts:
        for client in shift.clients.all():
            client_shift_data.append({
                'client': client,
                'shift': shift
            })
    
    return render(request, 'users/staff_dashboard.html', {
        "clients": client_shift_data,
        "today": today
    })


@login_required
def client_dashboard(request):
    if request.user.userprofile.role != "client":
        return redirect("dashboard_redirect")

    client = request.user.userprofile
    goals = client.goals.all()

    latest_shift = (
        Shift.objects.filter(clients=client)
        .order_by("-date", "-end_time")
        .first()
    )

    session_ended = False
    if latest_shift:
        shift_end = datetime.combine(latest_shift.date, latest_shift.end_time)
        shift_end = timezone.make_aware(shift_end)

        if timezone.localtime(timezone.now()) > shift_end:
            session_ended = True

    return render(request, 'users/client_dashboard.html', {
        "client": client,
        "goals": goals,
        "session_ended": session_ended,
    })

@login_required
def client_profile(request):
    profile=request.user.userprofile
    return render(request, 'users/client_profile.html',{
        'user_obj':request.user,
        'profile':profile

    })

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def create_user(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']

            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already exists!")
                return render(request, 'users/create_user.html', {'form': form})
            
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
                role=form.cleaned_data['role']
            )

            messages.success(request, "User created successfully.")
            return render(request, 'users/create_user.html', {'form': form, 'redirect_after_success': True})
        else:
            errors = form.errors.as_data()
            for field, field_errors in errors.items():
                for e in field_errors:
                    messages.error(request, e.message)

    else:
        form = CreateUser()

    return render(request, 'users/create_user.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def manage_users(request):
    query = request.GET.get("q")
    users = User.objects.all().select_related('userprofile').order_by("userprofile__name") 

    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(userprofile__name__icontains=query))

    return render(request, "users/manage_users.html", {"users": users, "query": query})

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, f"User {user.username} deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")
    
    return redirect('manage_users')

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        date_of_birth = request.POST.get("date_of_birth")
        role = request.POST.get("role")

        user.username = email
        user.email = email

        if password:
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                if "from_client_detail" in request.GET:
                    url = reverse("edit_user", kwargs={"user_id": user.id}) + "?from_client_detail=1"
                    return redirect(url)
                return redirect("edit_user", user_id=user.id)
            user.set_password(password)

        user.save()

        profile.name = name 
        if date_of_birth:
            profile.date_of_birth = date_of_birth
        profile.role = role
        profile.save()

        messages.success(request, f"{name} updated successfully.")
        if "from_client_detail" in request.GET:
            return redirect("client_detail", client_id=profile.id)
        return redirect("manage_users")

    initial_data = {
        "name": profile.name,
        "email": user.email,
        "date_of_birth": profile.date_of_birth,
        "role": profile.role,
    }

    return render(request, "users/edit_user.html", {
    "user_obj": user,
    "name": profile.name,
    "email": user.email,
    "date_of_birth": profile.date_of_birth,
    "role": profile.role,
    })

@login_required
def clients_list(request):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")
    query = request.GET.get("q", "")
    clients = UserProfile.objects.filter(role="client").order_by("name")
    if query:
        clients=clients.filter(name__icontains=query)
    return render(request, "users/clients_list.html" ,{"clients": clients, "query": query})

@login_required
def client_detail(request, client_id):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")

    client = get_object_or_404(UserProfile, id=client_id, role="client")

    default_types = [
        "Meet new people", "Build friendships", "Learn a new skill", "Stay active",
        "Feel included", "Improve transport knowledge", "Improve communication skills",
        "Learn money handling", "Gain confidence", "Connect to community",
        "Explore independently", "Gain independence"
    ]

    if not client.goals.exists():
        for t in default_types[:3]: 
            goal_type, _ = GoalType.objects.get_or_create(name=t)
            Goal.objects.create(client=client, goal_type=goal_type, progress=0)

    goals = client.goals.select_related("goal_type").all()

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

def admin_feedback_list(request):
    feedbacks = Feedback.objects.filter(is_staff_feedback=False).order_by('-created_at')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    mood = request.GET.get('mood')

    if start_date:
        feedbacks = feedbacks.filter(created_at__date__gte=start_date)
    if end_date:
        feedbacks = feedbacks.filter(created_at__date__lte=end_date)
    if mood and mood != "all":
        feedbacks = feedbacks.filter(mood=mood)

    return render(request, 'users/admin_feedback_list.html', {
        'feedbacks': feedbacks
    })

def feedback_detail(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    return render(request, 'users/feedback_detail.html', {'feedback':feedback})

@login_required
def admin_profile(request):
    profile=getattr(request.user, "userprofile", None)
    return render(request, "users/admin_profile.html",{
        "user_obj": request.user,
        "profile":profile,
        "has_profile":bool(profile),

    })

@login_required
def edit_goals(request, client_id):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")

    client = get_object_or_404(UserProfile, id=client_id, role="client")

    goals = client.goals.select_related("goal_type").all()

    goal_choices = GoalType.objects.all()

    if request.method == "POST":
        for goal in goals:
            progress_value = request.POST.get(f"goal_progress_{goal.id}")
            if progress_value is not None:
                try:
                    goal.progress = int(progress_value)
                except ValueError:
                    pass

            goal_value = request.POST.get(f"goal_name_{goal.id}")
            if goal_value:
                goal_type, _ = GoalType.objects.get_or_create(name=goal_value)
                goal.goal_type = goal_type

            goal.save()

        return redirect("client_detail", client_id=client.id)

    return render(request, "users/edit_goals.html", {
        "client": client,
        "goals": goals,   
        "goal_choices": [(g.name, g.name) for g in goal_choices],
    })

@login_required

@user_passes_test(lambda u: u.userprofile.role == "admin")
def shift_list(request):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  
    end_of_week = start_of_week + timedelta(days=6)           

    weekly_shifts = Shift.objects.filter(date__range=[start_of_week, end_of_week])

    chart_labels = [(start_of_week + timedelta(days=i)).strftime("%d/%m/%y") for i in range(7)]
    chart_data = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        staff_count = weekly_shifts.filter(date=day).values("staff").distinct().count()
        chart_data.append(staff_count)

    shifts = Shift.objects.select_related("staff").prefetch_related("clients").filter(date__gte=timezone.now().date()).order_by("date","date", "start_time")[:6]

    return render(request, "users/shift_list.html", {"shifts": shifts, "chart_labels": chart_labels,
        "chart_data": chart_data,})

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def allocate_shift(request):
    if request.method == "POST":
        form = ShiftForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Shift allocated successfully!", extra_tags="shift")
            return render(request, 'users/allocate_shift.html', {
                'form': ShiftForm() 
            }) 
    else:
        form = ShiftForm()
    
    return render(request, 'users/allocate_shift.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def edit_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    from_param = request.GET.get("from", "")
    if request.method == "POST":
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, "Shift updated successfully!", extra_tags="shift")
            else:
                messages.info(request, "No changes were made to the shift.", extra_tags="shift")
            url = reverse("edit_shift", kwargs={"shift_id": shift.id})
            if from_param:
                url += f"?from={from_param}"
            return redirect(url)
    else:
        form = ShiftForm(instance=shift)
    return render(request, "users/edit_shift.html", {"form": form, "shift": shift})

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def delete_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    if request.method == "POST":
        shift.delete()
        from_param = request.GET.get("from", "")

        if from_param == "all":
            target_url = reverse("all_shifts") + "?deleted=1"
        else:
            target_url = reverse("shift_list") + "?deleted=1"

        return render(request, "users/redirect_replace.html", {"target_url": target_url})

    return redirect("shift_list")
    
@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def all_shifts(request):
    if request.user.userprofile.role != "admin":
        return redirect("dashboard_redirect")

    shifts = (
        Shift.objects
        .select_related("staff")
        .prefetch_related("clients")
        .order_by("-date", "-start_time")
    )

    return render(request, "users/all_shifts.html", {"shifts": shifts})
@login_required
def staff_profile(request):
    if request.user.userprofile.role != "staff":
        return redirect("dashboard_redirect")
    profile = request.user.userprofile
    return render(request, "users/staff_profile.html", {
        "user_obj": request.user,
        "profile": profile,

    })

@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def export_shifts_pdf(request):
    qs = (Shift.objects
          .select_related("staff")
          .prefetch_related("clients")
          .order_by("date", "start_time"))
    buf =BytesIO()
    doc = SimpleDocTemplate(buf, pagesize = landscape(A4), leftMargin = 24, rightMargin = 24, topMargin = 24, bottomMargin = 24  )
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("ShiftLog", styles["Title"]))
    story.append(Spacer(1,8))
    data=[["Date", "Staff", "Clients", "Start", "End", ]]
    if qs.exists():
        for s in qs:
            clients = ", ".join(c.name for c in s.clients.all()) or "-"
            data.append([
                s.date.strftime("%d/%m/%Y") if s.date else "-",
                getattr(s.staff, "name", "-"),
                clients,
                s.start_time.strftime("%I:%M %p").lower() if s.start_time else "-",
                s.end_time.strftime("%I:%M %p").lower() if s.end_time else "-",])
    else:
        data.append(["No shifts allocated yet.", "", "", "", ""])
    table = Table(data, colWidths =[90,140,380,90,90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eef2ff")),
        ("GRID", (0,0),(-1,-1),0.5, colors.HexColor("#d8dce7")),
        ("FONTNAME", (0,0), (-1,-1), "Times-Roman"),
        ("FONTSIZE", (0,0),(-1,-1),10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0),(-1,0),"CENTER"),
    ]))
    story.append(table)
    doc.build(story)
    pdf = buf.getvalue(); 
    buf.close()
    resp = HttpResponse(pdf,content_type = "application/pdf")
    resp["Content-Disposition"] = 'attachment; filename="shift_log.pdf"'
    return resp

@login_required
@login_required
def client_info(request, client_id):
    # Restrict to staff users only
    if request.user.userprofile.role != "staff":
        return redirect("dashboard_redirect")

    # Get the target client profile
    client = get_object_or_404(UserProfile, id=client_id, role="client")

    if request.method == "POST":
        summary = request.POST.get("summary", "").strip()
        if summary:
            # ✅ Use Feedback instead of StaffNote
            Feedback.objects.create(
                user=request.user,           # staff who wrote it
                comment=summary,             # their note
                is_staff_feedback=True       # identifies it as staff feedback
            )

            messages.success(request, "Feedback submitted successfully.")
            return redirect("staff_dashboard")

        messages.error(request, "Please type feedback before submitting.")

    return render(request, "users/staff_notes.html", {"client": client})


@login_required
@user_passes_test(lambda u: u.userprofile.role == "admin")
def staff_feedback_list(request):
    feedbacks = Feedback.objects.filter(is_staff_feedback=True).order_by('-created_at')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        feedbacks = feedbacks.filter(created_at__date__gte=start_date)
    if end_date:
        feedbacks = feedbacks.filter(created_at__date__lte=end_date)

    return render(request, "users/staff_feedback_list.html", {"feedbacks": feedbacks})