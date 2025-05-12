#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Run migrations for each app in the correct order
echo "Creating migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations products
python manage.py makemigrations inventory
python manage.py makemigrations branches
python manage.py makemigrations cart
python manage.py makemigrations orders
python manage.py makemigrations suppliers
python manage.py makemigrations staff
python manage.py makemigrations reports

# Apply migrations
echo "Applying migrations..."
python manage.py migrate accounts
python manage.py migrate
python manage.py migrate contenttypes
python manage.py migrate admin
python manage.py migrate auth
python manage.py migrate sites
python manage.py migrate sessions
python manage.py migrate messages
python manage.py migrate staticfiles
python manage.py migrate allauth
python manage.py migrate products
python manage.py migrate inventory
python manage.py migrate branches
python manage.py migrate cart
python manage.py migrate orders
python manage.py migrate suppliers
python manage.py migrate staff
python manage.py migrate reports

echo "Migrations completed!" 