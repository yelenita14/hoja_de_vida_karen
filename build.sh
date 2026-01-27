#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input

# Crear usuario admin 
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'Karen'
password = 'Karen1234'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email='', password=password)
    print(f'USUARIO {username} CREADO CON EXITO')
else:
    print(f'EL USUARIO {username} YA EXISTE')
END