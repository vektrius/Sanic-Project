import asyncio

from Crypto.Hash import SHA1
from sanic_jwt.exceptions import AuthenticationFailed
from sqlalchemy import Column, Integer, String, Boolean, INTEGER, ForeignKey, Float, select
from sqlalchemy.orm import relationship
from sqlalchemy import update as sqlalchemy_update
from testquest.database import Base, async_db_session


class BaseModel(Base):
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True)


class User(BaseModel):
    __tablename__ = 'users'
    username = Column(String(120),unique=True)
    password = Column(String(120))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean,default=False)
    invoices = relationship("Invoice", back_populates='user')

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.password = SHA1.new(kwargs.get('password').encode()).hexdigest()

    def to_dict(self):
        return {
            'user_id': self.id,
            'username': self.username,
        }

    @classmethod
    async def authenticate(cls, username: str, password: str):
        query = select(cls).where(cls.username == username)
        results = await async_db_session.execute(query)
        user = results.scalars().first()
        if user is None:
            raise AuthenticationFailed("User not found.")

        if not user.is_active:
            raise AuthenticationFailed("User not activated.")

        password_hash = SHA1.new(password.encode()).hexdigest()
        if user.password != password_hash:
            raise AuthenticationFailed("No user with password")
        return user


class Invoice(BaseModel):
    __tablename__ = 'invoices'
    amount = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates='invoices', cascade="all, delete")
    transactions = relationship("Transaction", back_populates='invoice')


class Product(BaseModel):
    __tablename__ = 'products'
    name = Column(String(120))
    discription = Column(String)
    price = Column(Float)

    def to_dict(self):
        return {
            'name' : self.name,
            'discription' : self.discription,
            'price' : self.price
        }

class Transaction(BaseModel):
    __tablename__ = 'transactions'
    invoices_id = Column(Integer, ForeignKey('invoices.id'))
    invoice = relationship('Invoice', back_populates='transactions')
    amount = Column(Float)


# asyncio.run(async_db_session.create_all())