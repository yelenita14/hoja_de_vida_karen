#!/usr/bin/env bash
# Salir si ocurre un error
set -o errexit

# 1. Instalar librerías
pip install -r requirements.txt

# 2. Archivos estáticos
python manage.py collectstatic --no-input

# 3. Crear las tablas en la base de datos de Render (Postgres)
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py migrate

# 4. Crear tu usuario automáticamente si no existe
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'Karen'
password = 'Karen1234'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email='', password=password)
    print(f'USUARIO {username} CREADO CON EXITO')
else:
    print(f'EL USUARIO {username} YA EXISTE EN POSTGRES')
END
