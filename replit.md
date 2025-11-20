# ARCH System - AI-Driven Rural Care Hub

## Project Overview
A comprehensive healthcare platform for rural diabetes management in Cameroon. The system empowers Community Health Volunteers (CHVs) with AI-powered tools for blood glucose monitoring, risk assessment, and personalized patient care.

## Technology Stack
- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML, CSS (Glassmorphism design), Vanilla JavaScript
- **Database**: PostgreSQL
- **AI/ML**: OpenAI GPT-4o-mini for risk assessment and personalized advice
- **Charts**: Chart.js for data visualization

## Key Features
1. **CHV Authentication**: Secure role-based access (CHV, Admin, System Admin) with Werkzeug password hashing
2. **Patient Management**: Registration, search, and profile management
3. **Glucose Monitoring**: Input readings with contextual factors (diet, stress, symptoms)
4. **AI Risk Assessment**: Real-time ML-based risk scoring (Low/Medium/High)
5. **Personalized Advice**: Context-aware dietary and behavioral recommendations using local Cameroonian foods
6. **Dashboards**: 
   - CHV: Daily tasks, high-risk cases, performance metrics
   - Patient: Glucose trends with Chart.js visualizations (7/14/30-day)
   - Admin: System-wide analytics, CHV performance
7. **Alert System**: Automated high-risk patient detection

## Architecture
```
/
├── app.py                 # Flask backend with secure API endpoints
├── requirements.txt       # Python dependencies
├── README.md             # User documentation
├── replit.md             # Project memory and architecture
├── templates/            # HTML templates
│   ├── login.html        # Glassmorphism login page
│   ├── chv_dashboard.html
│   ├── patient_registration.html
│   ├── glucose_input.html
│   ├── patient_dashboard.html
│   └── admin_dashboard.html
└── static/
    └── css/style.css     # Beautiful glassmorphism styling
```

## Database Schema
- **users**: CHV accounts with secure password hashing
- **patients**: Patient demographic and medical information
- **glucose_readings**: Blood glucose measurements with context
- **risk_assessments**: AI-generated risk scores and advice
- **alerts**: High-risk patient notifications
- **visit_summaries**: Auto-generated visit records

## Security Features (Production-Ready)
- ✅ Secure password hashing with Werkzeug (PBKDF2)
- ✅ SQL injection prevention with parameterized queries
- ✅ Proper database connection management with context managers
- ✅ Session-based authentication with role-based access control
- ✅ No connection leaks

## Default Credentials
- **CHV**: username: `chv_demo`, password: `chv123`
- **Admin**: username: `admin`, password: `admin123`

⚠️ **Change these in production!**

## Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)
- `SESSION_SECRET`: Flask session secret (auto-generated)
- `OPENAI_API_KEY`: OpenAI API key for AI features (optional - app works without it)

## Recent Changes (Nov 20, 2025)
- ✅ Complete Flask application with all MVP features
- ✅ Beautiful glassmorphism UI with white-dominant color scheme
- ✅ Chart.js integration for glucose trend visualization
- ✅ Integrated OpenAI for AI-powered risk assessment
- ✅ **SECURITY FIX**: Implemented secure password hashing with Werkzeug
- ✅ **BUG FIX**: Fixed database connection leaks with context managers
- ✅ **BUG FIX**: Fixed SQL INTERVAL query bug in patient dashboard
- ✅ All code reviewed and approved by architect - production ready!

## User Preferences
- Modern, clean design with glassmorphism effects
- Professional aesthetics with white as dominant color
- Purple gradient background for visual appeal
- Tablet-optimized interface for CHV field use
- Using only HTML, CSS, JavaScript, and Python (no React/TypeScript)

## Project Goals
- Improve diabetes management in rural Cameroon
- Enable affordable, accessible blood glucose monitoring
- Provide AI-driven personalized care recommendations
- Reduce complications through early intervention
- Create sustainable, scalable healthcare solution

## Status
✅ **READY FOR USE** - All features implemented and tested. Application is running and accessible!

## Next Steps (Future Enhancements)
- SMS/WhatsApp integration for referral alerts (Twilio)
- Appointment and follow-up reminder notifications
- Data export functionality (CSV, Excel) for monthly reports
- Geographic mapping of rural hotspots
- Offline-first capability for poor connectivity areas
- Continuous ML model improvement from collected data
