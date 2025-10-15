from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('client', 'Client'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_clients'
    )

    def __str__(self):
        return self.name if self.name else self.user.email

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="feedback_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GoalType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Goal(models.Model): 
    client = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="goals")
    goal_type = models.ForeignKey(GoalType, on_delete=models.CASCADE, null=True, blank=True)
    progress = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.name} - {self.goal_type.name if self.goal_type else 'Unknown'} ({self.progress}%)"

class Shift(models.Model):
    staff = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="staff_shifts",
        limit_choices_to={'role': 'staff'}  
    )
    clients = models.ManyToManyField(
        UserProfile,
        related_name="client_shifts",
        limit_choices_to={'role': 'client'}
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        client_names = ", ".join([c.name for c in self.clients.all()[:3]])  
        if self.clients.count() > 3:
            client_names += "..."
        return f"Shift: {self.staff.name} with {client_names} on {self.date}"