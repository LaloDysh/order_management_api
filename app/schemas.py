from pydantic import BaseModel, Field, StrictStr, StrictInt, StrictFloat, field_validator
from typing import List
import re

class UserCreate(BaseModel):
    name: StrictStr = Field(min_length=3, max_length=50)
    email: StrictStr = Field(pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    
    @field_validator('name')
    @classmethod
    def validate_name_letters_only(cls, v):
        if not isinstance(v, str):
            raise ValueError('must be a string')
        if v.lower() in ["true", "false"]:
            raise ValueError('cannot be the string "True" or "False"')
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('must contain only letters and spaces - no numbers or symbols')
        return v
    
    model_config = {
        "extra": "forbid",
        "validate_assignment": True
    }

class UserLogin(BaseModel):
    email: StrictStr = Field(pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    
    model_config = {
        "extra": "forbid",
        "validate_assignment": True
    }

class OrderItemCreate(BaseModel):
    name: StrictStr = Field(min_length=3, max_length=50)
    price: StrictFloat = Field(gt=0)
    quantity: StrictInt = Field(gt=0)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not isinstance(v, str):
            raise ValueError('must be a string')
        if v.lower() in ["true", "false"]:
            raise ValueError('cannot be the string "True" or "False"')
        return v
    
    model_config = {
        "extra": "forbid", 
        "validate_assignment": True,
        "json_schema_extra": {
            "example": {
                "name": "Sandwich",
                "price": 9.25,
                "quantity": 2
            }
        }
    }

class OrderCreate(BaseModel):
    customer_name: StrictStr = Field(min_length=3, max_length=50)
    products: List[OrderItemCreate] = Field(min_items=1)
    
    @field_validator('customer_name')
    @classmethod
    def validate_customer_name(cls, v):
        if not isinstance(v, str):
            raise ValueError('must be a string')
        if v.lower() in ["true", "false"]:
            raise ValueError('cannot be the string "True" or "False"')
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('must contain only letters and spaces - no numbers or symbols')
        return v
    
    model_config = {
        "extra": "forbid",
        "validate_assignment": True,
        "json_schema_extra": {
            "example": {
                "customer_name": "John Doe",
                "products": [
                    {
                        "name": "Sandwich",
                        "price": 9.00,
                        "quantity": 2
                    },
                    {
                        "name": "Salad",
                        "price": 9.25,
                        "quantity": 2
                    }
                ]
            }
        }
    }