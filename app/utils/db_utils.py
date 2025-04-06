# from app.extensions import db
# from app.models import Product
# from sqlalchemy import func


# def get_or_create_product(name, price):
#     product = Product.query.filter(func.lower(Product.name) == func.lower(name)).first()
#     if not product:
#         product = Product(name=name, price=price)
#         db.session.add(product)
#         db.session.flush()        
#     return product

# def optimize_query(query, limit=None):
#     if limit:
#         query = query.limit(limit)
#     return query

# def transaction(func):
#     def wrapper(*args, **kwargs):
#         try:
#             result = func(*args, **kwargs)
#             db.session.commit()
#             return result
#         except Exception as e:
#             db.session.rollback()
#             raise e
#     return wrapper