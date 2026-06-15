import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Booking, Report
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# --- Authentication Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['name'] = user.name
            session['role'] = user.role
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
        
    user_id = session['user_id']
    bookings = Booking.query.filter_by(patient_id=user_id).order_by(Booking.booking_date.desc()).all()
    total_bookings = len(bookings)
    reports_available = sum(1 for b in bookings if b.report)
    
    return render_template('patient_dashboard.html', 
                           bookings=bookings, 
                           total_bookings=total_bookings,
                           reports_available=reports_available)

@app.route('/book-test', methods=['GET', 'POST'])
@login_required
def book_test():
    if session.get('role') == 'admin':
        flash('Admins cannot book tests.', 'warning')
        return redirect(url_for('admin_dashboard'))

    available_tests = [
        'Blood Test', 'CBC', 'Thyroid Profile', 
        'Diabetes Test', 'Lipid Profile', 'Liver Function Test'
    ]

    if request.method == 'POST':
        patient_name = request.form['patient_name']
        age = request.form['age']
        gender = request.form['gender']
        mobile = request.form['mobile']
        test_name = request.form['test_name']
        
        if not all([patient_name, age, gender, mobile, test_name]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('book_test'))

        new_booking = Booking(
            patient_id=session['user_id'],
            patient_name=patient_name,
            age=int(age),
            gender=gender,
            mobile=mobile,
            test_name=test_name
        )
        db.session.add(new_booking)
        db.session.commit()
        
        flash('Test booked successfully!', 'success')
        return redirect(url_for('patient_dashboard'))

    return render_template('book_test.html', tests=available_tests)

@app.route('/reports')
@login_required
def reports():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
        
    user_id = session['user_id']
    bookings = Booking.query.filter_by(patient_id=user_id).join(Report).all()
    return render_template('reports.html', bookings=bookings)

@app.route('/download-report/<int:report_id>')
@login_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    if session.get('role') != 'admin' and report.booking.patient_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
        
    return send_from_directory(app.config['UPLOAD_FOLDER'], report.report_file, as_attachment=True)

# --- Admin Routes ---

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_patients = User.query.filter_by(role='patient').count()
    total_bookings = Booking.query.count()
    pending_tests = Booking.query.filter(Booking.status != 'Completed').count()
    completed_tests = Booking.query.filter_by(status='Completed').count()
    
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html', 
                           total_patients=total_patients,
                           total_bookings=total_bookings,
                           pending_tests=pending_tests,
                           completed_tests=completed_tests,
                           recent_bookings=recent_bookings)

@app.route('/admin/bookings', methods=['GET', 'POST'])
@admin_required
def admin_bookings():
    search_query = request.args.get('search', '')
    if search_query:
        bookings = Booking.query.filter(
            (Booking.patient_name.ilike(f'%{search_query}%')) |
            (Booking.test_name.ilike(f'%{search_query}%'))
        ).order_by(Booking.booking_date.desc()).all()
    else:
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()

    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        new_status = request.form.get('status')
        booking = Booking.query.get(booking_id)
        if booking:
            booking.status = new_status
            db.session.commit()
            flash(f'Booking {booking_id} status updated to {new_status}.', 'success')
            return redirect(url_for('admin_bookings'))

    return render_template('admin_bookings.html', bookings=bookings, search_query=search_query)

@app.route('/admin/upload-report/<int:booking_id>', methods=['GET', 'POST'])
@admin_required
def upload_report(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if request.method == 'POST':
        if 'report_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['report_file']
        remarks = request.form.get('remarks', '')
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(f"booking_{booking.id}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            report = Report(booking_id=booking.id, report_file=filename, remarks=remarks)
            db.session.add(report)
            booking.status = 'Completed'
            db.session.commit()
            
            flash('Report uploaded successfully.', 'success')
            return redirect(url_for('admin_bookings'))
        else:
            flash('Only PDF files are allowed.', 'danger')
            
    return render_template('upload_report.html', booking=booking)

def setup_database():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@lab.com').first():
            hashed_pw = generate_password_hash('admin123')
            admin = User(name='Administrator', email='admin@lab.com', password=hashed_pw, role='admin')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    setup_database()
    app.run(debug=True, port=5000)
