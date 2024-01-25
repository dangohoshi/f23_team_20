#!/bin/bash

# Remove the SQLite database file
rm -f db.sqlite3

# Remove all files in the migrations directory except __init__.py
find lifesync/migrations/ -type f ! -name '__init__.py' -delete

# Make and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the Django development server
python manage.py runserver &

# Run the register.py script
python register.py

# Wait for a user input to close
read -p "Press any key to continue..."
