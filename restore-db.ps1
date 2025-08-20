# restore-db.ps1

# ===== Config =====
$DB_NAME = "he-app"
$DB_USER = "HolidayExplorers"
$DB_PASSWORD = "1212"
$SUPERUSER_NAME = "melaniedancer@holidayexolorers.com.au"
$SUPERUSER_EMAIL = "melaniedancer@holidayexolorers.com.au"
$SUPERUSER_PASSWORD = "Crows2017!"

Write-Host "=== Activating virtual environment ==="
.\venv\Scripts\activate

Write-Host "=== Installing dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "=== Restoring PostgreSQL database from backup ==="
psql -U postgres -h localhost -p 5432 -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"
psql -U postgres -h localhost -p 5432 -d "$DB_NAME" -f "he-app_backup.sql"

Write-Host "=== Running Django migrations ==="
python manage.py migrate

Write-Host "=== Creating superuser (if not exists) ==="
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$SUPERUSER_NAME").exists():
    User.objects.create_superuser("$SUPERUSER_NAME", "$SUPERUSER_EMAIL", "$SUPERUSER_PASSWORD")
    print("Superuser created: $SUPERUSER_NAME / $SUPERUSER_PASSWORD")
else:
    print("Superuser already exists.")
EOF

Write-Host "=== Setup complete! Run the server with: python manage.py runserver ==="


