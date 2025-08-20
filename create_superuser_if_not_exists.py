import os
import django
from dotenv import load_dotenv

def run():
    load_dotenv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if username and email and password:
        if not User.objects.filter(username=username).exists():
            print(f"Creating superuser {username}...")
            User.objects.create_superuser(username=username, email=email, password=password)
        else:
            print(f"Superuser {username} already exists.")
    else:
        print("Missing environment variables for superuser.")
