#!/bin/bash

REPO_DIR="/home/fongetha/connections-api/connections-backend"
BRANCH="main"
LOG_FILE="/home/fongetha/connections-api/connections-backend/daily_deploy_cron.log"

# Write the timestamp
echo "----- $(date) -----" >> "$LOG_FILE"

cd $REPO_DIR

# Fetch changes
git fetch origin $BRANCH

# Check for updates from remote
LOCAL=$(git rev-parse $BRANCH)
REMOTE=$(git rev-parse origin/$BRANCH)

if [ $LOCAL != $REMOTE ]; then
    echo "New commits detected. Deploying..."
    git reset --hard origin/$BRANCH
    # Apply Django migrations
    source /home/fongetha/connections-api/connections-backend/venv/bin/activate
    python manage.py makemigrations
    python manage.py migrate
    deactivate
    sudo systemctl restart apache2
    echo "Deployment completed successfully!" >> "$LOG_FILE"
else
    echo "No new commits." >> "$LOG_FILE"
fi
