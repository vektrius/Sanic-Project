from sanic_ext.extensions.openapi import openapi


class UserOpenAPIModel:
    username = openapi.String(description="Username")
    password = openapi.Password(description="Password")
    is_active = openapi.Boolean(description="is active")

class UserRegistrationOpenAPIModel:
    username = openapi.String(description="Username")
    password = openapi.Password(description="Password")

class ProductOpenAPIModel:
    name = openapi.String(description="name")
    discription = openapi.String(description="discription")
    price = openapi.Float(description="Price")

class ProductOpenAPIBuyModel:
    product_id = openapi.Integer(description="product id")
    invoice_id = openapi.Integer(description="invoice id")

class InvoicesOpenAPIModel:
    invoice_id = openapi.Integer(description="invoice id")
    amount = openapi.Float(description="amount")
    user_id = openapi.Integer(description="user id")

class TransactionOpenAPIModel:
    invoice_id = openapi.Integer(description="invoice id")
    amount = openapi.Float(description="amount")