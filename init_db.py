# Create a file called init_db.py in your project root
from app import create_app
from app.extensions import db
from app.models import User  # Import all your models here

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    
    # Optionally, create an initial admin user
    # Uncomment if you want this functionality
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            email='admin@example.com',
            name='Admin User'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")
    else:
        print("Admin user already exists")
    
    
    print("Database initialized successfully!")