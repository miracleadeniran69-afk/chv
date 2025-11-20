from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import secrets
import json
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
CORS(app)

openai_client = None
if os.environ.get('OPENAI_API_KEY'):
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    except Exception as e:
        print(f"OpenAI initialization warning: {e}")
        openai_client = None

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(50),
                district VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                patient_id VARCHAR(50) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                age INTEGER,
                gender VARCHAR(10),
                village VARCHAR(255),
                district VARCHAR(255),
                phone VARCHAR(50),
                emergency_contact VARCHAR(50),
                diabetes_type VARCHAR(20),
                diagnosis_date DATE,
                registered_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS glucose_readings (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER REFERENCES patients(id),
                chv_id INTEGER REFERENCES users(id),
                glucose_level FLOAT NOT NULL,
                reading_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                medication_taken BOOLEAN,
                diet_description TEXT,
                stress_level VARCHAR(50),
                food_availability VARCHAR(50),
                symptoms TEXT,
                notes TEXT
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id SERIAL PRIMARY KEY,
                reading_id INTEGER REFERENCES glucose_readings(id),
                patient_id INTEGER REFERENCES patients(id),
                risk_level VARCHAR(20) NOT NULL,
                risk_score FLOAT,
                ai_advice TEXT,
                warning_flags TEXT,
                referral_recommended BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER REFERENCES patients(id),
                risk_assessment_id INTEGER REFERENCES risk_assessments(id),
                alert_type VARCHAR(50),
                message TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS visit_summaries (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER REFERENCES patients(id),
                chv_id INTEGER REFERENCES users(id),
                visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                summary TEXT,
                recommendations TEXT,
                follow_up_date DATE
            )
        ''')
        
        admin_hash = generate_password_hash('admin123')
        cur.execute('''
            INSERT INTO users (username, password_hash, full_name, role, email, district)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', ('admin', admin_hash, 'System Administrator', 'admin', 'admin@arch.cm', 'Central'))
        
        chv_hash = generate_password_hash('chv123')
        cur.execute('''
            INSERT INTO users (username, password_hash, full_name, role, email, district)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', ('chv_demo', chv_hash, 'Demo CHV Worker', 'chv', 'chv@arch.cm', 'Bafoussam'))
        
        conn.commit()
        cur.close()

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'chv':
            return redirect(url_for('chv_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
    
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        session['role'] = user['role']
        return jsonify({'success': True, 'role': user['role']})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/chv-dashboard')
def chv_dashboard():
    if 'user_id' not in session or session.get('role') != 'chv':
        return redirect(url_for('index'))
    return render_template('chv_dashboard.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')

@app.route('/patient-registration')
def patient_registration():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('patient_registration.html')

@app.route('/patient-dashboard/<int:patient_id>')
def patient_dashboard(patient_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('patient_dashboard.html', patient_id=patient_id)

@app.route('/glucose-input/<int:patient_id>')
def glucose_input(patient_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('glucose_input.html', patient_id=patient_id)

@app.route('/api/register-patient', methods=['POST'])
def register_patient():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    patient_id = f"ARCH-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            INSERT INTO patients (patient_id, full_name, age, gender, village, district, phone, 
                                 emergency_contact, diabetes_type, diagnosis_date, registered_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, patient_id
        ''', (patient_id, data.get('full_name'), data.get('age'), data.get('gender'),
              data.get('village'), data.get('district'), data.get('phone'),
              data.get('emergency_contact'), data.get('diabetes_type'),
              data.get('diagnosis_date'), session['user_id']))
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
    
    return jsonify({'success': True, 'patient': result})

@app.route('/api/search-patients')
def search_patients():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    query = request.args.get('q', '')
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            SELECT id, patient_id, full_name, age, gender, village, phone
            FROM patients
            WHERE full_name ILIKE %s OR patient_id ILIKE %s
            LIMIT 20
        ''', (f'%{query}%', f'%{query}%'))
        
        patients = cur.fetchall()
        cur.close()
    
    return jsonify({'patients': patients})

@app.route('/api/patient/<int:patient_id>')
def get_patient(patient_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('SELECT * FROM patients WHERE id = %s', (patient_id,))
        patient = cur.fetchone()
        
        cur.close()
    
    return jsonify({'patient': patient})

@app.route('/api/glucose-reading', methods=['POST'])
def add_glucose_reading():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            INSERT INTO glucose_readings (patient_id, chv_id, glucose_level, medication_taken,
                                         diet_description, stress_level, food_availability, symptoms, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (data.get('patient_id'), session['user_id'], data.get('glucose_level'),
              data.get('medication_taken'), data.get('diet_description'),
              data.get('stress_level'), data.get('food_availability'),
              data.get('symptoms'), data.get('notes')))
        
        reading = cur.fetchone()
        reading_id = reading['id']
        
        risk_data = generate_risk_assessment(data.get('patient_id'), data.get('glucose_level'),
                                             data.get('medication_taken'), data.get('stress_level'),
                                             data.get('symptoms'), cur)
        
        cur.execute('''
            INSERT INTO risk_assessments (reading_id, patient_id, risk_level, risk_score,
                                         ai_advice, warning_flags, referral_recommended)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (reading_id, data.get('patient_id'), risk_data['risk_level'],
              risk_data['risk_score'], risk_data['advice'], 
              json.dumps(risk_data['warnings']), risk_data['referral_needed']))
        
        assessment = cur.fetchone()
        
        if risk_data['risk_level'] == 'High':
            cur.execute('''
                INSERT INTO alerts (patient_id, risk_assessment_id, alert_type, message)
                VALUES (%s, %s, %s, %s)
            ''', (data.get('patient_id'), assessment['id'], 'high_risk',
                  f"High-risk patient detected. Glucose: {data.get('glucose_level')} mg/dL"))
        
        conn.commit()
        cur.close()
    
    return jsonify({'success': True, 'risk_assessment': risk_data})

def generate_risk_assessment(patient_id, glucose_level, medication_taken, stress_level, symptoms, cur):
    glucose = float(glucose_level)
    
    risk_score = 0
    warnings = []
    
    if glucose < 70:
        risk_score += 40
        warnings.append('Hypoglycemia detected')
    elif glucose > 180:
        risk_score += 30
        warnings.append('Hyperglycemia detected')
    elif glucose > 250:
        risk_score += 50
        warnings.append('Severe hyperglycemia')
    
    if not medication_taken:
        risk_score += 20
        warnings.append('Medication not taken')
    
    if stress_level in ['High', 'Very High']:
        risk_score += 15
    
    cur.execute('''
        SELECT glucose_level, reading_time
        FROM glucose_readings
        WHERE patient_id = %s
        ORDER BY reading_time DESC
        LIMIT 5
    ''', (patient_id,))
    
    recent_readings = cur.fetchall()
    if len(recent_readings) >= 3:
        high_count = sum(1 for r in recent_readings if r['glucose_level'] > 180)
        if high_count >= 3:
            risk_score += 25
            warnings.append('Consistently high readings')
    
    if risk_score >= 70:
        risk_level = 'High'
        referral_needed = True
    elif risk_score >= 40:
        risk_level = 'Medium'
        referral_needed = False
    else:
        risk_level = 'Low'
        referral_needed = False
    
    if os.environ.get('OPENAI_API_KEY'):
        try:
            advice = generate_ai_advice(glucose, medication_taken, stress_level, symptoms, risk_level)
        except:
            advice = get_default_advice(glucose, risk_level)
    else:
        advice = get_default_advice(glucose, risk_level)
    
    return {
        'risk_level': risk_level,
        'risk_score': risk_score,
        'advice': advice,
        'warnings': warnings,
        'referral_needed': referral_needed
    }

def generate_ai_advice(glucose, medication_taken, stress_level, symptoms, risk_level):
    if not openai_client:
        return get_default_advice(glucose, risk_level)
    
    prompt = f"""
You are a healthcare AI assistant for rural diabetes management in Cameroon. Provide personalized advice.

Patient Data:
- Glucose Level: {glucose} mg/dL
- Medication Taken: {'Yes' if medication_taken else 'No'}
- Stress Level: {stress_level}
- Symptoms: {symptoms}
- Risk Level: {risk_level}

Provide:
1. Immediate actions (1-2 sentences)
2. Dietary recommendations using local foods (fufu, yam, beans, plantain, etc.)
3. Lifestyle advice
4. When to seek urgent care

Keep advice practical, culturally relevant, and concise.
"""
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def get_default_advice(glucose, risk_level):
    if glucose < 70:
        return "⚠️ Low blood sugar detected. Take 15g of fast-acting carbs (3 teaspoons of sugar or honey). Rest for 15 minutes and retest. If symptoms persist, seek immediate medical care."
    elif glucose > 250:
        return "🚨 Very high blood sugar. Drink plenty of water, take prescribed medication if missed. Avoid heavy meals. Contact clinic immediately if you feel very unwell, have difficulty breathing, or are vomiting."
    elif glucose > 180:
        return "📊 Blood sugar is high. Reduce portion sizes, choose boiled yam or beans instead of fufu. Take a 20-minute walk. Ensure you're taking medications as prescribed. Drink water regularly."
    else:
        return "✅ Good reading! Maintain your current diet and medication routine. Continue eating balanced meals with vegetables, lean protein, and whole grains. Keep up regular physical activity."

@app.route('/api/patient/<int:patient_id>/readings')
def get_patient_readings(patient_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    days = request.args.get('days', 30, type=int)
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            SELECT gr.*, ra.risk_level, ra.risk_score, ra.ai_advice
            FROM glucose_readings gr
            LEFT JOIN risk_assessments ra ON ra.reading_id = gr.id
            WHERE gr.patient_id = %s
            AND gr.reading_time >= NOW() - make_interval(days => %s)
            ORDER BY gr.reading_time DESC
        ''', (patient_id, days))
        
        readings = cur.fetchall()
        cur.close()
    
    return jsonify({'readings': readings})

@app.route('/api/chv/stats')
def chv_stats():
    if 'user_id' not in session or session.get('role') != 'chv':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            SELECT COUNT(DISTINCT patient_id) as total_patients
            FROM glucose_readings
            WHERE chv_id = %s
        ''', (session['user_id'],))
        stats = cur.fetchone()
        
        cur.execute('''
            SELECT COUNT(*) as tests_today
            FROM glucose_readings
            WHERE chv_id = %s AND DATE(reading_time) = CURRENT_DATE
        ''', (session['user_id'],))
        today = cur.fetchone()
        
        cur.execute('''
            SELECT COUNT(DISTINCT a.patient_id) as high_risk_count
            FROM alerts a
            JOIN glucose_readings gr ON gr.patient_id = a.patient_id
            WHERE gr.chv_id = %s AND a.status = 'pending'
            AND a.created_at >= NOW() - INTERVAL '7 days'
        ''', (session['user_id'],))
        alerts = cur.fetchone()
        
        cur.execute('''
            SELECT p.id, p.patient_id, p.full_name, p.village, ra.risk_level,
                   gr.glucose_level, gr.reading_time
            FROM patients p
            JOIN glucose_readings gr ON gr.patient_id = p.id
            JOIN risk_assessments ra ON ra.reading_id = gr.id
            WHERE gr.chv_id = %s AND ra.risk_level = 'High'
            AND gr.reading_time >= NOW() - INTERVAL '7 days'
            ORDER BY gr.reading_time DESC
            LIMIT 10
        ''', (session['user_id'],))
        high_risk_patients = cur.fetchall()
        
        cur.close()
    
    return jsonify({
        'total_patients': stats['total_patients'] or 0,
        'tests_today': today['tests_today'] or 0,
        'high_risk_count': alerts['high_risk_count'] or 0,
        'high_risk_patients': high_risk_patients
    })

@app.route('/api/admin/stats')
def admin_stats():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('SELECT COUNT(*) as total_patients FROM patients')
        patients = cur.fetchone()
        
        cur.execute('SELECT COUNT(*) as total_chvs FROM users WHERE role = %s', ('chv',))
        chvs = cur.fetchone()
        
        cur.execute('''
            SELECT COUNT(*) as total_readings
            FROM glucose_readings
            WHERE reading_time >= NOW() - INTERVAL '30 days'
        ''')
        readings = cur.fetchone()
        
        cur.execute('''
            SELECT COUNT(*) as active_alerts
            FROM alerts
            WHERE status = 'pending'
        ''')
        alerts = cur.fetchone()
        
        cur.execute('''
            SELECT u.full_name, u.district, COUNT(DISTINCT gr.patient_id) as patient_count,
                   COUNT(gr.id) as reading_count
            FROM users u
            LEFT JOIN glucose_readings gr ON gr.chv_id = u.id
            WHERE u.role = 'chv'
            GROUP BY u.id, u.full_name, u.district
            ORDER BY reading_count DESC
        ''')
        chv_performance = cur.fetchall()
        
        cur.execute('''
            SELECT ra.risk_level, COUNT(*) as count
            FROM risk_assessments ra
            WHERE ra.created_at >= NOW() - INTERVAL '30 days'
            GROUP BY ra.risk_level
        ''')
        risk_distribution = cur.fetchall()
        
        cur.close()
    
    return jsonify({
        'total_patients': patients['total_patients'],
        'total_chvs': chvs['total_chvs'],
        'total_readings': readings['total_readings'],
        'active_alerts': alerts['active_alerts'],
        'chv_performance': chv_performance,
        'risk_distribution': risk_distribution
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
