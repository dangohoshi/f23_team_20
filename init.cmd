@echo off

mkdir lifesync\migrations
del db.sqlite3
del lifesync\migrations\*.*
echo. > lifesync\migrations\__init__.py

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
start cmd "/k python manage.py runserver"

python register.py

pause
