from datetime import datetime
from flask import request
import re


def format_error_message(err):
    if isinstance(err['loc'], tuple) and len(err['loc']) > 0:
        field_name = err['loc'][-1]
    else:
        field_name = err['loc'][0] if err['loc'] else "unknown field"
    
    message = err['msg']
    
    return f"{field_name}: {message}"


def get_pagination_params():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
        
    return page, per_page