#!/bin/bash

# Navigate to the Django project directory
cd /home/fongetha/dev-connections-backend

# Activate the virtual environment
source venv/bin/activate

# Run Django development server
python manage.py runserver 0.0.0.0:8080