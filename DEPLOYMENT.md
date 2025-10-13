# Deployment Guide

This guide will help you deploy GivePulse to a production environment.

## 🚀 Quick Deployment Options

### 1. Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```

4. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### 2. DigitalOcean App Platform

1. **Connect GitHub Repository**
   - Go to DigitalOcean App Platform
   - Connect your GitHub repository
   - Select the main branch

2. **Configure Environment**
   - Set environment variables in the dashboard
   - Configure build and run commands

3. **Deploy**
   - The platform will automatically build and deploy

### 3. VPS Deployment (Ubuntu/Debian)

1. **Server Setup**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx postgresql
   ```

2. **Create User and Directory**
   ```bash
   sudo adduser givepulse
   sudo mkdir /var/www/givepulse
   sudo chown givepulse:givepulse /var/www/givepulse
   ```

3. **Clone and Setup**
   ```bash
   cd /var/www/givepulse
   git clone https://github.com/yourusername/givepulse.git .
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   sudo -u postgres createdb givepulse
   sudo -u postgres createuser givepulse
   sudo -u postgres psql -c "ALTER USER givepulse PASSWORD 'your-password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE givepulse TO givepulse;"
   ```

5. **Configure Django**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   python manage.py migrate
   python manage.py collectstatic
   python manage.py createsuperuser
   ```

6. **Setup Gunicorn**
   ```bash
   # Create gunicorn.service file
   sudo nano /etc/systemd/system/givepulse.service
   ```

   ```ini
   [Unit]
   Description=GivePulse Gunicorn daemon
   After=network.target

   [Service]
   User=givepulse
   Group=www-data
   WorkingDirectory=/var/www/givepulse
   Environment="PATH=/var/www/givepulse/venv/bin"
   ExecStart=/var/www/givepulse/venv/bin/gunicorn --workers 3 --bind unix:/var/www/givepulse/givepulse.sock give_pulse.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

7. **Setup Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/givepulse
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /var/www/givepulse;
       }
       location /media/ {
           root /var/www/givepulse;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/givepulse/givepulse.sock;
       }
   }
   ```

8. **Enable and Start Services**
   ```bash
   sudo ln -s /etc/nginx/sites-available/givepulse /etc/nginx/sites-enabled
   sudo systemctl start givepulse
   sudo systemctl enable givepulse
   sudo systemctl restart nginx
   ```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Django Settings
SECRET_KEY=your-very-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/givepulse

# Email (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security (for production)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 📊 Database Migration

### From SQLite to PostgreSQL

1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create Database**
   ```bash
   sudo -u postgres createdb givepulse
   sudo -u postgres createuser givepulse
   ```

3. **Export Data from SQLite**
   ```bash
   python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json
   ```

4. **Update Settings**
   ```python
   # In settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'givepulse',
           'USER': 'givepulse',
           'PASSWORD': 'your-password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Import Data**
   ```bash
   python manage.py migrate
   python manage.py loaddata data.json
   ```

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt (Certbot)

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Get Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **Auto-renewal**
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

## 📈 Performance Optimization

### 1. Static Files
```bash
python manage.py collectstatic --noinput
```

### 2. Database Optimization
```python
# In settings.py
DATABASES = {
    'default': {
        # ... your database config
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 3. Caching
```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## 🔍 Monitoring and Logging

### 1. Setup Logging
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/givepulse/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Health Checks
```python
# Create health check endpoint
def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

## 🚨 Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --clear
   ```

2. **Database Connection Issues**
   - Check database credentials
   - Verify database server is running
   - Check firewall settings

3. **Permission Issues**
   ```bash
   sudo chown -R www-data:www-data /var/www/givepulse
   sudo chmod -R 755 /var/www/givepulse
   ```

4. **Gunicorn Issues**
   ```bash
   sudo systemctl status givepulse
   sudo journalctl -u givepulse -f
   ```

## 📱 Mobile App Integration

The API endpoints are ready for mobile app integration:

- `/api/donors/` - Donor management
- `/api/requests/` - Blood requests
- `/api/matches/` - Donor matching
- `/api/appointments/` - Appointment management

## 🔄 Backup Strategy

### Database Backup
```bash
# Daily backup script
pg_dump givepulse > backup_$(date +%Y%m%d).sql
```

### Media Files Backup
```bash
# Backup media files
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

## 📞 Support

For deployment issues:
- Check the logs: `sudo journalctl -u givepulse -f`
- Review Django logs: `/var/log/givepulse/django.log`
- Check Nginx logs: `/var/log/nginx/error.log`

---

**Happy Deploying!** 🚀
