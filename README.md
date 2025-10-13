# GivePulse - Blood Donation Management System

A comprehensive Django-based web application for managing blood donation requests, donor matching, and hospital coordination.

## 🌟 Features

### For Donors
- **User Registration**: Easy donor registration with profile management
- **Blood Request Browsing**: View and respond to blood donation requests
- **Match Notifications**: Get notified when your blood type is needed
- **Donation History**: Track your donation history and certificates
- **QR Code Verification**: Secure appointment verification system

### For Staff
- **Hospital Management**: Register and manage hospital information
- **Blood Request Creation**: Create urgent blood donation requests
- **Donor Matching**: Automatic matching with compatible donors
- **Appointment Management**: Schedule and manage donation appointments
- **QR Code Generation**: Generate QR codes for appointment verification

### For Administrators
- **Admin Dashboard**: Comprehensive admin interface with statistics
- **User Management**: Manage donors, staff, and hospitals
- **Verification System**: Verify hospitals and staff members
- **System Monitoring**: Track donations, requests, and matches
- **Custom Admin Interface**: Beautiful, responsive admin panel

## 🚀 Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Styling**: Custom CSS with Bootstrap integration
- **Icons**: Bootstrap Icons
- **Fonts**: Poppins (Google Fonts)

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/givepulse.git
   cd givepulse
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 🎨 Design Features

### Color Scheme
- **Primary Green**: `#a5b68e` - Main brand color
- **Secondary Red**: `#ed3744` - Accent color for important actions
- **Clean Design**: Modern, responsive interface with smooth animations

### Responsive Design
- Mobile-first approach
- Bootstrap 5 grid system
- Touch-friendly interface
- Optimized for all screen sizes

## 📱 User Roles

### Donor
- Register and create profile
- Browse blood requests
- Respond to matches
- Track donation history
- Manage appointments

### Staff
- Create blood requests
- Manage hospital information
- Schedule appointments
- Verify QR codes
- View donor matches

### Administrator
- Manage all users
- Verify hospitals and staff
- Monitor system statistics
- Configure system settings
- Generate reports

## 🔧 Management Commands

The application includes several custom management commands:

```bash
# Populate sample data
python manage.py populate_sample_data

# Clean up expired sessions
python manage.py cleanup_sessions

# Regenerate certificates
python manage.py regenerate_certificates

# Regenerate QR codes
python manage.py regenerate_qr_codes

# Verify entities
python manage.py verify_entities --action verify --type staff
```

## 📁 Project Structure

```
givepulse/
├── give_pulse/              # Django project settings
├── give_pulse_app/          # Main application
│   ├── management/          # Custom management commands
│   ├── migrations/          # Database migrations
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # HTML templates
│   ├── admin.py            # Admin configuration
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   └── urls.py             # URL patterns
├── media/                  # User uploaded files
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

## 🗄️ Database Models

### Core Models
- **User**: Base user model with role-based permissions
- **Donor**: Donor-specific information and blood type
- **Staff**: Hospital staff with verification status
- **Hospital**: Hospital information and verification
- **BloodRequest**: Blood donation requests
- **Match**: Donor-request matching system
- **DonationAppointment**: Scheduled donation appointments
- **Donation**: Completed donation records

### Location Models
- **Governorate**: Administrative regions
- **City**: Cities within governorates
- **District**: Districts within cities

### Content Models
- **SuccessStory**: Success stories and testimonials
- **ContactMessage**: Contact form submissions

## 🔐 Security Features

- **User Authentication**: Secure login/logout system
- **Role-based Access**: Different permissions for different user types
- **Verification System**: Hospital and staff verification process
- **QR Code Security**: Secure appointment verification
- **CSRF Protection**: Cross-site request forgery protection
- **SQL Injection Protection**: Django ORM protection

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False` in settings
2. Configure `ALLOWED_HOSTS`
3. Set up a production database (PostgreSQL recommended)
4. Configure static file serving
5. Set up media file serving
6. Configure email settings
7. Set up SSL/HTTPS

### Environment Variables
Create a `.env` file with:
```
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=your-database-url
EMAIL_HOST=your-email-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the responsive CSS framework
- All contributors and testers

## 📞 Support

If you have any questions or need support, please:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added admin interface improvements
- **v1.2.0** - Enhanced UI/UX with Bootstrap 5
- **v1.3.0** - Added verification system and QR codes

---

**GivePulse** - Connecting donors with those in need, one drop at a time. 🩸❤️
