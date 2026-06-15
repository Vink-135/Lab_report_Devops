from app import app, db
from models import User, Booking, Report
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

with app.app_context():
    # Ensure database is created
    db.create_all()
    
    # Check if we already have test data
    if not User.query.filter_by(email='patient@lab.com').first():
        print("Creating sample test data...")
        
        # Add a sample patient
        patient_pw = generate_password_hash('patient123')
        patient = User(name='John Doe', email='patient@lab.com', password=patient_pw, role='patient')
        db.session.add(patient)
        db.session.commit()
        
        # Add sample bookings
        booking1 = Booking(
            patient_id=patient.id,
            patient_name='John Doe',
            age=45,
            gender='Male',
            mobile='9876543210',
            test_name='Blood Test',
            status='Completed',
            booking_date=datetime.utcnow() - timedelta(days=2)
        )
        
        booking2 = Booking(
            patient_id=patient.id,
            patient_name='Jane Doe',
            age=40,
            gender='Female',
            mobile='9876543210',
            test_name='Thyroid Profile',
            status='Pending',
            booking_date=datetime.utcnow()
        )
        
        db.session.add_all([booking1, booking2])
        db.session.commit()
        print("Sample data seeded successfully.")
        print("Admin Login: admin@lab.com / admin123")
        print("Patient Login: patient@lab.com / patient123")
    else:
        print("Sample data already exists.")
