""" 
This utility script automatically creates a Django superuser based on environment variables.

During application starting, this module checks for the presence of a superuser with administrative privileges.  
If the username, email, and password are provided via environment variables,
the script checks for an existing superuser and creates one if necessary.

Environment Variables Required:
    - Username: DJANGO 
    - Email: DJANGO 
    - Password: DJANGO.

Functions include run(), which loads environment variables, initializes Django, 
and conditionally establishes the superuser account.

 This script works alongside core/settings.py in the RUN_MAIN guard to prevent duplicate execution during autoreload.
"""
import os
import django
from dotenv import load_dotenv

def run():
    """
    Create a Django superuser if one does not already exist.

    Steps:
        1. Load environment variables from .env file.
        2. Initialize Django settings.
        3. Retrieve superuser credentials from env file.
        4. Check whether a superuser with the given username exists.
        5. Create the superuser if it does not already exist.

    Returns:
        None
    """
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
