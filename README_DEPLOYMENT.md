# 🚀 GivePulse AWS EC2 Deployment Guide

This guide will help you deploy GivePulse to your AWS EC2 instance at `13.61.22.133`.

## 📋 Prerequisites

- AWS EC2 instance running Ubuntu 20.04/22.04
- SSH access to your EC2 instance
- Domain name (optional, for SSL)

## 🛠️ Files Created for Deployment

### Configuration Files
- `settings_production.py` - Production Django settings
- `env.production` - Environment variables template
- `gunicorn.conf.py` - Gunicorn configuration
- `nginx.conf` - Nginx configuration
- `givepulse.service` - Systemd service file

### Scripts
- `deploy.sh` - Complete deployment script
- `quick_deploy.sh` - Streamlined deployment
- `ssl_setup.sh` - SSL/HTTPS setup
- `load_initial_data.py` - Load initial data (governments, hospitals, cities)

## 🚀 Quick Deployment Steps

### 1. Upload Files to EC2

```bash
# From your local machine, upload files to EC2
scp -r /path/to/your/give_pulse/* ubuntu@13.61.22.133:/home/ubuntu/
```

### 2. Connect to EC2 and Run Deployment

```bash
# SSH into your EC2 instance
ssh ubuntu@13.61.22.133

# Make scripts executable
chmod +x *.sh

# Run the quick deployment script
./quick_deploy.sh
```

### 3. Configure Environment Variables

```bash
# Edit the environment file
nano .env

# Update these critical values:
SECRET_KEY=your-very-secure-secret-key-here
DB_PASSWORD=your-secure-database-password
ALLOWED_HOSTS=13.61.22.133
```

### 4. Generate Secret Key

```bash
# Generate a secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Restart Services

```bash
# Restart the application
sudo systemctl restart givepulse
sudo systemctl restart nginx
```

## 🔒 SSL/HTTPS Setup (Optional)

If you have a domain name:

```bash
# Set up SSL certificate
./ssl_setup.sh yourdomain.com
```

## 📊 Initial Data Loading

The deployment script automatically loads:
- 27 Governorates (States/Provinces)
- 25+ Cities
- 15+ Districts
- 15+ Hospitals

## 🔧 Service Management

### Check Service Status
```bash
sudo systemctl status givepulse
sudo systemctl status nginx
```

### View Logs
```bash
# Application logs
sudo journalctl -u givepulse -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django logs
tail -f /var/www/givepulse/logs/django.log
```

### Restart Services
```bash
sudo systemctl restart givepulse
sudo systemctl restart nginx
```

## 🗄️ Database Management

### Access MySQL
```bash
mysql -u givepulse -p givepulse
```

### Backup Database
```bash
mysqldump -u givepulse -p givepulse > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
mysql -u givepulse -p givepulse < backup_file.sql
```

## 📁 File Structure on EC2

```
/var/www/givepulse/
├── give_pulse/                 # Django project
├── give_pulse_app/            # Django app
├── staticfiles/               # Collected static files
├── media/                     # User uploaded files
├── logs/                      # Application logs
├── venv/                      # Python virtual environment
├── .env                       # Environment variables
├── gunicorn.conf.py          # Gunicorn configuration
└── manage.py                 # Django management
```

## 🔍 Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   python manage.py collectstatic --clear
   sudo systemctl restart givepulse
   ```

2. **Database connection issues**
   - Check database credentials in `.env`
   - Verify MySQL is running: `sudo systemctl status mysql`
   - Check firewall settings

3. **Permission issues**
   ```bash
   sudo chown -R ubuntu:www-data /var/www/givepulse
   sudo chmod -R 755 /var/www/givepulse
   ```

4. **Gunicorn issues**
   ```bash
   sudo systemctl status givepulse
   sudo journalctl -u givepulse -f
   ```

### Health Check

Visit these URLs to verify deployment:
- Main application: `http://13.61.22.133`
- Health check: `http://13.61.22.133/health/`
- Admin panel: `http://13.61.22.133/admin/`

## 🔐 Security Checklist

- [ ] Changed default SECRET_KEY
- [ ] Set strong database password
- [ ] Configured ALLOWED_HOSTS
- [ ] Set up SSL/HTTPS (if using domain)
- [ ] Configured firewall (UFW)
- [ ] Set up regular backups
- [ ] Configured monitoring

## 📈 Performance Optimization

### Static Files
- Static files are served by Nginx
- Gzip compression enabled
- Browser caching configured

### Database
- MySQL optimized for production
- Connection pooling via Gunicorn

### Application
- Gunicorn with multiple workers
- Preload app enabled
- Worker recycling configured

## 🆘 Support

If you encounter issues:
1. Check the logs first
2. Verify all services are running
3. Check firewall and security groups
4. Ensure all environment variables are set

## 📞 Useful Commands

```bash
# Check all services
sudo systemctl status givepulse nginx mysql

# View real-time logs
sudo journalctl -u givepulse -f

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep gunicorn
```

---

**Your GivePulse application should now be running at: http://13.61.22.133** 🎉
