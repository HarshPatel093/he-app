from django.contrib.auth import get_user_model
from django.conf import settings
import os

def run():
    User = get_user_model()
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "harshpatel.adl@gmail.com")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "harshpatel.adl@gmail.com")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Harsh@7104")

    if not User.objects.filter(username=username).exists():
        print(f"Creating default superuser: {username}")
        User.objects.create_superuser(username=username, email=email, password=password)
    else:
        print(f"Superuser {username} already exists")
