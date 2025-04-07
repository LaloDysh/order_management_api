from app.extensions import db
from datetime import datetime
import uuid


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    products = db.relationship('OrderProduct', backref='order', cascade='all, delete-orphan')

    def __init__(self, user_id, customer_name, total_price):
        self.user_id = user_id
        self.customer_name = customer_name
        self.total_price = total_price

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'customer_name': self.customer_name,
            'total_price': self.total_price,
            'created_at': self.created_at.isoformat(),
            'products': [product.to_dict() for product in self.products]
        }

    def __repr__(self):
        return f'<Order {self.id}>'
