# Gunicorn configuration file for GivePulse
# This file contains production-ready Gunicorn settings

import multiprocessing
import os

# Server socket
bind = "unix:/var/www/givepulse/givepulse.sock"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/www/givepulse/logs/gunicorn_access.log"
errorlog = "/var/www/givepulse/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "givepulse"

# Server mechanics
daemon = False
pidfile = "/var/www/givepulse/givepulse.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    'DJANGO_SETTINGS_MODULE=give_pulse.settings_production',
]

# Preload app for better performance
preload_app = True

# Worker timeout for graceful shutdown
graceful_timeout = 30

# Maximum number of pending connections
listen = 2048

# Enable worker recycling
max_worker_memory = 200  # MB

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
