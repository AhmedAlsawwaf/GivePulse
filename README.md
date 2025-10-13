# GivePulse - Blood Donation Management System

A comprehensive Django-based web application for managing blood donation requests, donor matching, and hospital coordination.

## 🌟 Features

### For Donors
- **User Registration**: Easy donor registration with profile management
- **Blood Request Browsing**: View and respond to blood donation requests
- **AJAX Matching**: Smooth, real-time blood request matching without page reloads
- **Match Notifications**: Get notified when your blood type is needed
- **Donation History**: Track your donation history and certificates
- **QR Code Verification**: Secure appointment verification system
- **Cooldown Management**: Automatic cooldown periods between donations

### For Staff
- **Hospital Management**: Register and manage hospital information
- **Blood Request Creation**: Create urgent blood donation requests
- **Donor Matching**: Automatic matching with compatible donors
- **Appointment Management**: Schedule and manage donation appointments
- **QR Code Generation**: Generate QR codes for appointment verification
- **Match Management**: Review and manage donor matches

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
- **AJAX**: Modern JavaScript with fetch API
- **PDF Generation**: ReportLab for certificates
- **QR Codes**: qrcode library for appointment verification

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AhmedAlsawwaf/GivePulse.git
   cd GivePulse
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

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/

## 🎯 Key Features

### AJAX-Powered Matching
- Real-time blood request matching without page reloads
- Smooth user experience with loading states
- Immediate feedback for successful matches
- Error handling for various scenarios

### Smart Blood Type Compatibility
- Automatic blood type compatibility checking
- Support for ABO and Rh factor matching
- Comprehensive compatibility matrix

### QR Code System
- Secure appointment verification
- QR code generation for appointments
- Mobile-friendly verification process

### Admin Management
- Custom admin interface with enhanced UI/UX
- Comprehensive user management
- Hospital and staff verification system
- Real-time statistics and monitoring

## 🗂️ Project Structure

```
GivePulse/
├── give_pulse/                 # Django project settings
├── give_pulse_app/            # Main application
│   ├── static/               # Static files (CSS, JS, images)
│   ├── templates/            # HTML templates
│   ├── management/           # Custom management commands
│   └── models.py             # Database models
├── media/                    # User uploads
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
└── README.md               # This file
```

## 🔧 Management Commands

The project includes useful management commands:

- `cleanup_sessions` - Clean up invalid user sessions
- `verify_entities` - Verify or unverify hospitals and staff

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Interface**: Clean, professional design
- **Bootstrap Integration**: Consistent styling and components
- **Custom CSS**: Tailored styling for the blood donation theme
- **Interactive Elements**: Smooth animations and transitions

## 🔐 Security Features

- **Custom User Model**: Secure authentication system
- **Password Validation**: Strong password requirements
- **Session Management**: Secure session handling
- **CSRF Protection**: Built-in CSRF protection
- **Input Validation**: Comprehensive form validation

## 📱 Mobile Support

- Fully responsive design
- Touch-friendly interface
- Mobile-optimized forms
- QR code scanning support

## 🚀 Deployment

The application is ready for deployment with:

- **Production Settings**: Configured for production deployment
- **Static Files**: Proper static file handling
- **Database Support**: PostgreSQL ready
- **Environment Variables**: Secure configuration management

See `DEPLOYMENT.md` for detailed deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 👥 Team

- **Ahmed Alsawwaf** - Project Lead & Developer
- **Contributors** - See GitHub contributors page

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team

## 🔄 Recent Updates

- ✅ Fixed Django admin compatibility issues
- ✅ Added AJAX functionality for blood request matching
- ✅ Enhanced admin interface with custom styling
- ✅ Improved user experience with real-time feedback
- ✅ Added comprehensive error handling
- ✅ Optimized static files configuration
- ✅ Cleaned up codebase and removed unnecessary files

---

**GivePulse** - Connecting donors with those in need, one drop at a time. 🩸❤️