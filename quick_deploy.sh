#!/bin/bash

# Quick Deployment Script for GivePulse on AWS EC2
# This script provides a streamlined deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

echo "🚀 GivePulse Quick Deployment Script"
echo "====================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Step 1: System Update and Dependencies
print_header "Step 1: Installing System Dependencies"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    mysql-server mysql-client libmysqlclient-dev \
    nginx git curl wget unzip \
    build-essential libssl-dev libffi-dev

# Step 2: MySQL Setup
print_header "Step 2: Configuring MySQL"
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure MySQL installation
print_warning "You'll need to set a MySQL root password and secure the installation:"
sudo mysql_secure_installation

# Step 3: Application Setup
print_header "Step 3: Setting up Application"
sudo mkdir -p /var/www/givepulse
sudo chown $USER:$USER /var/www/givepulse
cd /var/www/givepulse

print_warning "Please copy your application files to /var/www/givepulse/"
print_warning "You can use: scp -r /path/to/your/give_pulse/* user@13.61.22.133:/var/www/givepulse/"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p staticfiles

# Step 4: Environment Configuration
print_header "Step 4: Environment Configuration"
cp env.production .env

print_warning "CRITICAL: Please edit .env file with your actual values:"
print_warning "1. Generate a secure SECRET_KEY"
print_warning "2. Set a strong database password"
print_warning "3. Configure email settings if needed"
echo
print_warning "To generate a SECRET_KEY, run:"
echo "python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""

# Step 5: Database Setup
print_header "Step 5: Database Setup"
read -p "Enter MySQL root password: " -s mysql_root_password
echo

# Create database and user
mysql -u root -p$mysql_root_password << EOF
CREATE DATABASE IF NOT EXISTS givepulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'givepulse'@'localhost' IDENTIFIED BY 'your-secure-password';
GRANT ALL PRIVILEGES ON givepulse.* TO 'givepulse'@'localhost';
FLUSH PRIVILEGES;
EOF

print_warning "Database created. Please update DB_PASSWORD in .env file with the password you just set."

# Step 6: Django Setup
print_header "Step 6: Django Application Setup"
export DJANGO_SETTINGS_MODULE=give_pulse.settings_production

# Run migrations
python manage.py migrate

# Create superuser
print_warning "Creating superuser account..."
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Load initial data
print_warning "Loading initial data (governments, hospitals, cities)..."
python load_initial_data.py

# Step 7: Gunicorn Setup
print_header "Step 7: Configuring Gunicorn"
sudo cp givepulse.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start givepulse
sudo systemctl enable givepulse

# Step 8: Nginx Setup
print_header "Step 8: Configuring Nginx"
sudo cp nginx.conf /etc/nginx/sites-available/givepulse
sudo ln -sf /etc/nginx/sites-available/givepulse /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start Nginx
sudo systemctl restart nginx

# Step 9: Firewall Configuration
print_header "Step 9: Configuring Firewall"
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

# Step 10: Final Setup
print_header "Step 10: Final Configuration"
sudo chown -R $USER:www-data /var/www/givepulse
sudo chmod -R 755 /var/www/givepulse

# Restart services
sudo systemctl restart givepulse
sudo systemctl restart nginx

print_status "🎉 Deployment completed successfully!"
echo
print_status "Your application is now accessible at: http://13.61.22.133"
echo
print_warning "Next steps:"
print_warning "1. Edit .env file with your actual configuration"
print_warning "2. Restart services: sudo systemctl restart givepulse"
print_warning "3. Set up SSL certificate: ./ssl_setup.sh yourdomain.com"
print_warning "4. Test your application thoroughly"
echo
print_status "Useful commands:"
echo "  Check service status: sudo systemctl status givepulse"
echo "  View logs: sudo journalctl -u givepulse -f"
echo "  Restart services: sudo systemctl restart givepulse nginx"
echo "  Check Nginx: sudo nginx -t"
