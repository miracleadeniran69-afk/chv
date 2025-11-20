# 🏥 ARCH System - AI-Driven Rural Care Hub

A comprehensive healthcare platform for rural diabetes management in Cameroon, empowering Community Health Volunteers (CHVs) with AI-powered tools for blood glucose monitoring, risk assessment, and personalized patient care.

## ✨ Features

### For Community Health Volunteers (CHVs)
- **Patient Registration**: Easy-to-use form for registering new patients with demographic and medical information
- **Quick Patient Search**: Find existing patients instantly by name or Patient ID
- **Glucose Reading Input**: Record blood glucose with contextual factors (diet, stress, symptoms, medication adherence)
- **AI-Powered Risk Assessment**: Real-time risk scoring (Low/Medium/High) with personalized advice
- **Daily Dashboard**: View tasks, high-risk cases, and performance metrics
- **High-Risk Alerts**: Automatic notifications for patients needing urgent attention

### For Patients
- **Personal Dashboard**: View glucose history and trends
- **Visual Analytics**: Interactive charts showing 7-day, 14-day, and 30-day glucose trends
- **Personalized Advice**: AI-generated dietary and behavioral recommendations using local foods
- **Risk Monitoring**: Color-coded risk levels with clear indicators

### For Administrators
- **System Overview**: Monitor total patients, CHVs, readings, and active alerts
- **CHV Performance Tracking**: Analyze productivity and patient coverage by CHV
- **Risk Distribution Analytics**: Visualize community-level health trends
- **Data Export**: Generate reports for health planning and policy decisions

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database (automatically configured in Replit)
- OpenAI API key (optional, for AI features)

### Running the Application

The application is already running! Simply open the webview to access the login page.

### Default Credentials

**CHV Account:**
- Username: `chv_demo`
- Password: `chv123`

**Admin Account:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important**: Change these default passwords in production!

## 🎨 Design

- **Glassmorphism UI**: Modern, professional design with frosted glass effects
- **White-Dominant Color Scheme**: Clean, medical-grade aesthetics
- **Purple Gradient Background**: Beautiful and calming visual experience
- **Responsive Design**: Optimized for tablets and mobile devices used by CHVs in the field

## 🤖 AI Features

### Risk Assessment Algorithm
The system analyzes multiple factors to calculate risk scores:
- Blood glucose levels (hypoglycemia, hyperglycemia detection)
- Medication adherence
- Stress levels
- Symptoms reported
- Historical reading patterns

### Personalized Advice
When an OpenAI API key is provided, the system generates:
- Context-aware dietary recommendations using local Cameroonian foods (fufu, yam, beans, plantain)
- Behavioral guidance based on patient's specific situation
- Clear instructions on when to seek urgent medical care

### Fallback Mode
Without an OpenAI API key, the system uses intelligent default advice based on glucose levels.

## 📊 Database Schema

- **users**: CHV accounts with role-based access control
- **patients**: Patient demographic and medical information
- **glucose_readings**: Blood glucose measurements with contextual data
- **risk_assessments**: AI-generated risk scores and personalized advice
- **alerts**: High-risk patient notifications
- **visit_summaries**: Auto-generated visit records

## 🔒 Security Features

- **Secure Password Hashing**: Uses Werkzeug's industry-standard password hashing (PBKDF2)
- **Session Management**: Secure Flask sessions with role-based access control
- **SQL Injection Prevention**: Parameterized queries throughout
- **Connection Management**: Proper database connection lifecycle with context managers

## 🛠 Technology Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Database**: PostgreSQL
- **AI/ML**: OpenAI GPT-4o-mini
- **Charts**: Chart.js
- **Styling**: Custom CSS with Glassmorphism effects

## 📱 User Guide

### For CHVs

1. **Login** with your credentials
2. **Register a patient** or search for existing patients
3. **Record glucose readings** with contextual information
4. **Review AI-generated risk assessment** and personalized advice
5. **Monitor high-risk patients** from your dashboard
6. **View patient history** and trends

### For Admins

1. **Login** with admin credentials
2. **View system-wide statistics** on the dashboard
3. **Monitor CHV performance** across the district
4. **Analyze risk distribution** in the community
5. **Identify high-risk areas** needing intervention

## 🌍 Impact

The ARCH System addresses critical healthcare challenges in rural Cameroon:

- **Problem**: Limited access to affordable blood glucose monitoring (costs $0.5-$1.0 per test, clinics >50km away)
- **Impact**: 80% of diabetic patients undiagnosed, presenting only in crisis states
- **Solution**: Affordable, AI-powered testing hubs with CHVs providing personalized care
- **Outcome**: Early intervention, reduced complications, improved glycemic control

## 📈 Future Enhancements

- SMS/WhatsApp integration for referral alerts
- Appointment and follow-up reminders
- Offline-first capability for poor connectivity areas
- Geographic mapping of rural hotspots
- Data export (CSV, Excel) for monthly reports
- Continuous ML model improvement from collected data

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (auto-configured)
- `SESSION_SECRET`: Flask session secret (auto-generated)
- `OPENAI_API_KEY`: OpenAI API key for AI features (optional)

To enable AI features, set your OpenAI API key:
1. Click the "Secrets" tab in Replit
2. Add a new secret with key `OPENAI_API_KEY`
3. Paste your OpenAI API key as the value
4. Restart the application

## 📄 License

This project is designed to improve healthcare access in rural Cameroon. For healthcare use.

## 👥 Team

- **Divine Ndamnsa** - Public Health & Biostatistics
- **Muhammed Adediran** - Machine Learning Engineering
- **Muzi Shabangu** - Health Information Management
- **Emmanuel Oladipo** - Full-Stack Development

---

**Built with ❤️ for rural healthcare workers in Cameroon**
