#!/usr/bin/env python
"""
Database initialization script for the Order Management API.
This script creates the initial migration and applies it to the database.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import create_app
from app.extensions import db
from app.models import User, Product, Order, OrderProduct

# Create the Flask application
app = create_app()


def run_command(command):
    """Run a shell command and print the output."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               text=True, capture_output=True)
        print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return False


def initialize_database():
    """Initialize the database with migrations."""
    with app.app_context():
        # Check if migrations directory exists
        migrations_dir = project_root / 'migrations'
        if not migrations_dir.exists():
            print("Initializing migrations directory...")
            if not run_command("flask db init"):
                return False
            
        # Create initial migration
        print("Creating initial migration...")
        if not run_command("flask db migrate -m 'Initial migration'"):
            return False
            
        # Apply the migration
        print("Applying migration...")
        if not run_command("flask db upgrade"):
            return False
        
        print("Database initialization completed successfully.")
        return True


def seed_sample_data():
    """Seed the database with sample data for testing."""
    print("Seeding sample data...")
    
    with app.app_context():
        # Check if we already have users
        if User.query.first():
            print("Database already contains data. Skipping seed.")
            return True
            
        try:
            # Create sample users
            users = [
                User(email="john@example.com", name="John Smith"),
                User(email="maria@example.com", name="Maria Garcia")
            ]
            db.session.bulk_save_objects(users)
            db.session.commit()
            print(f"Created {len(users)} sample users.")
            
            # Retrieve users for relationships
            users = User.query.all()
            
            # Create sample products
            products = [
                Product(name="Coffee", price=3.50),
                Product(name="Sandwich", price=8.75),
                Product(name="Salad", price=9.25),
                Product(name="Burger", price=12.00),
                Product(name="Fries", price=4.50)
            ]
            db.session.bulk_save_objects(products)
            db.session.commit()
            print(f"Created {len(products)} sample products.")
            
            # Retrieve products for relationships
            products = Product.query.all()
            
            # Create sample orders
            order1 = Order(
                user_id=users[0].id,
                customer_name="Alice Johnson",
                total_price=16.75  # Coffee + Sandwich + Fries
            )
            
            order2 = Order(
                user_id=users[1].id,
                customer_name="Bob Williams",
                total_price=25.25  # Coffee + Burger + Salad
            )
            
            db.session.add(order1)
            db.session.add(order2)
            db.session.flush()
            
            # Create order products
            order_products = [
                # Order 1
                OrderProduct(order_id=order1.id, product_id=products[0].id, quantity=1, unit_price=3.50),  # Coffee
                OrderProduct(order_id=order1.id, product_id=products[1].id, quantity=1, unit_price=8.75),  # Sandwich
                OrderProduct(order_id=order1.id, product_id=products[4].id, quantity=1, unit_price=4.50),  # Fries
                
                # Order 2
                OrderProduct(order_id=order2.id, product_id=products[0].id, quantity=1, unit_price=3.50),  # Coffee
                OrderProduct(order_id=order2.id, product_id=products[3].id, quantity=1, unit_price=12.00), # Burger
                OrderProduct(order_id=order2.id, product_id=products[2].id, quantity=1, unit_price=9.25)   # Salad
            ]
            
            db.session.bulk_save_objects(order_products)
            db.session.commit()
            print(f"Created {len(order_products)} sample order products across {2} orders.")
            
            print("Sample data seeded successfully.")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding data: {e}")
            return False


if __name__ == "__main__":
    if initialize_database():
        seed_sample_data()
    else:
        print("Database initialization failed.")
        sys.exit(1)