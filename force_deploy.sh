LOG_FILE="/home/fongetha/connections-api/connections-backend/daily_deploy_cron.log"
echo "New commits detected. Deploying..."
# Apply Django migrations
source /home/fongetha/connections-api/connections-backend/venv/bin/activate
python manage.py makemigrations
python manage.py migrate
deactivate
sudo systemctl restart apache2
echo "Deployment completed successfully!" >> "$LOG_FILE"