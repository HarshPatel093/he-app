""" 
Developed database models for the Holiday Explorers System.

This module contains all of the system's essential data structures.
    - UserProfile: Enhances Django's User model by adding fields like roles, date_of_birth, name.
    - Feedback: Keeps track of client mood, comments, and optional images.
    - GoalType and Goal: Represent the user's goals and progress.
    - Shift: Holds client/staff shift allocations.
    - StaffNote: Notes taken by staff during client sessions.

Each model has string representations for easier readability in the admin UI.
"""
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """ 
    Extends the Django User model with new characteristics and roles.

    Fields:
        user (OneToOneField): Associates each profile with exactly one Django User.
        Name (CharField): The user's display name.
        Date_of_birth (DateField): An optional date of birth.
        User role (CharField): ('admin','staff', or 'client').
        assigned_staff (ForeignKey): Refers to a client's assigned staff person.

    Purpose: - Represent staff, admins, and clients within the system.
        - Implement a role-based access and assignment structure.
    """
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

    # Returns a readable name for the admin interface, if name is missing it returns user's email
    def __str__(self):
        return self.name if self.name else self.user.email

class Feedback(models.Model):
    """ 
    Stores feedbacks from clients.

    Fields:
        User (ForeignKey): Client who provided the feedback.
        mood (IntegerField): An emoji-based mood score (1 to 5).
        Comment (TextField): Optional written feedback.
        photo (ImageField): An optional uploaded image (located in MEDIA_ROOT).
        created_at (DateTimeField): Submission timestamp.
        is_staff_feedback (booleanField): Distinguishes between staff notes and customer feedback.

    Purpose: - Gather clients' session reflections.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="feedback_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff_feedback = models.BooleanField(default=False)
    
    # Returns email of staff/client based on feedback submiited by
    def __str__(self):
        return f"{self.user.email} - {'Staff' if self.is_staff_feedback else 'Client'} Feedback"
    
class GoalType(models.Model):
    """ 
    Refers to a general goal category (e.g., meet new people).

    Fields include the goal category name (CharField).
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Goal(models.Model):
    """ Represents a client's specified goal.

    Fields: 
        - client (ForeignKey): Connects the goal to a UserProfile with the role 'client'.
        - goal_type (ForeignKey): The category of the goal.
        - Progress (IntegerField): Completion % (0-100).
        - created_at (DateTimeField): indicates when the goal was added.

    Purpose: - Track customer goals and progress.
        - Provide admin dashboard reporting (e.g., goals by type and goals added throughtout the month).
    """ 
    client = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="goals")
    goal_type = models.ForeignKey(GoalType, on_delete=models.CASCADE, null=True, blank=True)
    progress = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Returns a readable representation: Client - GoalType (progress%)
    def __str__(self):
        return f"{self.client.name} - {self.goal_type.name if self.goal_type else 'Unknown'} ({self.progress}%)"

class Shift(models.Model):
    """ 
    Shows daily shift assigned to a staff person with many clients.

    Fields: 
        - Staff (ForeignKey): The person in charge of the shift.
        - clients (ManyToManyField): All clients who are assigned to staff in the shift.
        - date (DateField): Shift date.
        - start_time (TimeField): The start time.
        - end_time (TimeField): The finish time.

    Purpose: Provide role-based scheduling.
        - Provide admin shift management.
    """
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

    # Returns a readable summary (eg., Shift: staff1 with client 1,2 etc on YYYY/MM/DD)
    def __str__(self):
        client_names = ", ".join([c.name for c in self.clients.all()[:3]])  
        if self.clients.count() > 3:
            client_names += "..."
        return f"Shift: {self.staff.name} with {client_names} on {self.date}"
    
class StaffNote(models.Model):
    """ 
    Staff-written session notes for clients.

    Fields:
        - Staff (ForeignKey): The staff member who wrote the note.
        - client (ForeignKey): The client receiving assistance from staff.
        - Summary (TextField): A description of the session.
        - created_at (DateTimeField): The timestamp of note creation.

    Purpose: 
        - Enables staff to record session summaries.
        - Admins can later examine behavioural patterns.
    """ 
    staff = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name="notes", limit_choices_to={'role': 'staff'}

    ) 
    client = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE,
        related_name="staff_notes", limit_choices_to={'role': 'client'}
        )
    summary= models.TextField()
    created_at= models.DateTimeField(auto_now_add=True)

    # Returns a formatted label with staff, client, and date.
    def __str__(self):
        return f"{self.staff.name} → {self.client.name} ({self.created_at:%Y-%m-%d})"