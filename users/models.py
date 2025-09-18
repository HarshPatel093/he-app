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

    def __str__(self):
        return self.user.email

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

    def __str__(self):
        return f"{self.client.name} - {self.goal_type.name if self.goal_type else 'Unknown'} ({self.progress}%)"