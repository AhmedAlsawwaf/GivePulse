#!/bin/bash

# GivePulse AWS EC2 Deployment Script
# Run this script on your EC2 instance to deploy the application

set -e  # Exit on any error

echo "🚀 Starting GivePulse Deployment on AWS EC2..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    mysql-server mysql-client libmysqlclient-dev \
    nginx git curl wget unzip \
    build-essential libssl-dev libffi-dev

# Start and enable MySQL
print_status "Configuring MySQL..."
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure MySQL installation
print_status "Securing MySQL installation..."
sudo mysql_secure_installation

# Create application directory
print_status "Setting up application directory..."
sudo mkdir -p /var/www/givepulse
sudo chown $USER:$USER /var/www/givepulse

# Clone or copy application files
print_status "Setting up application files..."
cd /var/www/givepulse

# If you're copying files from local machine, use scp:
# scp -r /path/to/your/give_pulse/* user@13.61.22.133:/var/www/givepulse/

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Copy environment file
print_status "Setting up environment configuration..."
cp env.production .env

print_warning "IMPORTANT: Please edit .env file with your actual values:"
print_warning "1. Change SECRET_KEY to a secure random string"
print_warning "2. Set a strong database password"
print_warning "3. Configure email settings if needed"
print_warning "Run: nano .env"

# Create MySQL database and user
print_status "Setting up MySQL database..."
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

# Run Django migrations
print_status "Running Django migrations..."
export DJANGO_SETTINGS_MODULE=give_pulse.settings_production
python manage.py migrate

# Create superuser
print_status "Creating superuser account..."
python manage.py createsuperuser

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Set up Gunicorn
print_status "Setting up Gunicorn service..."
sudo tee /etc/systemd/system/givepulse.service > /dev/null << EOF
[Unit]
Description=GivePulse Gunicorn daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/givepulse
Environment="PATH=/var/www/givepulse/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=give_pulse.settings_production"
ExecStart=/var/www/givepulse/venv/bin/gunicorn --workers 3 --bind unix:/var/www/givepulse/givepulse.sock give_pulse.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Set up Nginx
print_status "Setting up Nginx configuration..."
sudo tee /etc/nginx/sites-available/givepulse > /dev/null << EOF
server {
    listen 80;
    server_name 13.61.22.133;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/givepulse;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /var/www/givepulse;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/givepulse/givepulse.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/givepulse /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Set proper permissions
sudo chown -R $USER:www-data /var/www/givepulse
sudo chmod -R 755 /var/www/givepulse

# Start and enable services
print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl start givepulse
sudo systemctl enable givepulse
sudo systemctl restart nginx

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw --force enable

print_status "Deployment completed successfully! 🎉"
print_status "Your application should be accessible at: http://13.61.22.133"
print_warning "Next steps:"
print_warning "1. Edit .env file with your actual configuration"
print_warning "2. Restart services: sudo systemctl restart givepulse"
print_warning "3. Set up SSL certificate with Let's Encrypt"
print_warning "4. Load initial data (governments, hospitals, cities)"

echo
print_status "To check service status:"
echo "sudo systemctl status givepulse"
echo "sudo systemctl status nginx"
echo
print_status "To view logs:"
echo "sudo journalctl -u givepulse -f"
echo "tail -f /var/www/givepulse/logs/django.log"

