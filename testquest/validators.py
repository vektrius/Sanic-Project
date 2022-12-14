
from pydantic import BaseModel


class UserValidator(BaseModel):
    username : str
    password : str


class BuyProductValidator(BaseModel):
    product_id : int
    invoice_id : int


class WebhookValidator(BaseModel):
    signature : str
    transaction_id : int
    user_id : int
    invoice_id : int
    amount : int


class ProductValidator(BaseModel):
    name : str
    discription : str
    price : float




class ProductUpdateValidator(BaseModel):
    name : str = None
    discription : str = None
    price : float = None
