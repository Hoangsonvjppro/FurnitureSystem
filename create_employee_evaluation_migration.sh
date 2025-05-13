#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Create migrations for staff app
echo "Creating migrations for staff app..."
python manage.py makemigrations staff

# Apply migration
echo "Applying migrations..."
python manage.py migrate staff

echo "Staff migrations completed!" 