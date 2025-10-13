#!/bin/bash

# SSL/HTTPS Setup Script for GivePulse
# This script sets up SSL certificate using Let's Encrypt

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

echo "🔒 Setting up SSL/HTTPS for GivePulse..."

# Check if domain is provided
if [ -z "$1" ]; then
    print_error "Please provide your domain name"
    print_error "Usage: ./ssl_setup.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1

print_status "Setting up SSL for domain: $DOMAIN"

# Install Certbot
print_status "Installing Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Stop Nginx temporarily
print_status "Stopping Nginx..."
sudo systemctl stop nginx

# Get SSL certificate
print_status "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Update Nginx configuration for HTTPS
print_status "Updating Nginx configuration for HTTPS..."
sudo tee /etc/nginx/sites-available/givepulse > /dev/null << EOF
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
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

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Start Nginx
print_status "Starting Nginx..."
sudo systemctl start nginx
sudo systemctl reload nginx

# Update Django settings for HTTPS
print_status "Updating Django settings for HTTPS..."
cd /var/www/givepulse

# Update .env file to enable HTTPS settings
sed -i 's/SECURE_SSL_REDIRECT=False/SECURE_SSL_REDIRECT=True/' .env
sed -i 's/SECURE_HSTS_SECONDS=0/SECURE_HSTS_SECONDS=31536000/' .env
sed -i 's/SECURE_HSTS_INCLUDE_SUBDOMAINS=False/SECURE_HSTS_INCLUDE_SUBDOMAINS=True/' .env
sed -i 's/SECURE_HSTS_PRELOAD=False/SECURE_HSTS_PRELOAD=True/' .env
sed -i 's/SESSION_COOKIE_SECURE=False/SESSION_COOKIE_SECURE=True/' .env
sed -i 's/CSRF_COOKIE_SECURE=False/CSRF_COOKIE_SECURE=True/' .env

# Update ALLOWED_HOSTS to include domain
sed -i "s/ALLOWED_HOSTS=13.61.22.133/ALLOWED_HOSTS=13.61.22.133,$DOMAIN/" .env

# Restart Django application
print_status "Restarting Django application..."
sudo systemctl restart givepulse

# Set up automatic certificate renewal
print_status "Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --reload-hook 'systemctl reload nginx'") | crontab -

print_status "SSL setup completed successfully! 🎉"
print_status "Your application is now accessible at: https://$DOMAIN"
print_warning "Make sure to:"
print_warning "1. Update your DNS records to point $DOMAIN to 13.61.22.133"
print_warning "2. Test the SSL certificate: https://www.ssllabs.com/ssltest/"
print_warning "3. Update any hardcoded HTTP URLs in your application to HTTPS"

