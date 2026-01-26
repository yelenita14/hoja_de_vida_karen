#!/usr/bin/env bash
# Salir si ocurre un error
set -o errexit

# Actualizar paquetes e instalar wkhtmltopdf
apt-get update
apt-get install -y wkhtmltopdf

# Instalar librerías Python
pip install -r requirements.txt

# Archivos estáticos
python manage.py collectstatic --no-input

# Crear las tablas en la base de datos de Render (Postgres)
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py migrate

# Crear tu usuario automáticamente si no existe
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
