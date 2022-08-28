from Crypto.Hash import SHA1
from sanic import json
from sanic_jwt.exceptions import AuthenticationFailed
from sqlalchemy import Column, INTEGER, String, Boolean, update, select, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.database import Base, async_db_session
from exceptions import ObjectNotFoundException


class BaseModel(Base):
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True)


class User(BaseModel):
    __tablename__ = 'users'
    username = Column(String(120), unique=True)
    password = Column(String(120))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    invoices = relationship("Invoice", back_populates='user')

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.password = SHA1.new(kwargs.get('password').encode()).hexdigest()

    def to_dict(self):
        return {
            'user_id': self.id,
            'username': self.username,
            'is_active': self.is_active
        }

    @classmethod
    async def is_active_set(cls, user, value: bool):
        if user is None:
            raise ObjectNotFoundException

        update_user_query = (
            update(cls).where(User.id == user.id).values(is_active=value).execution_options(
                synchronize_session="fetch")
        )
        await async_db_session.execute(update_user_query)
        await async_db_session.commit()

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

    def to_dict(self):
        return {
            'invoice_id': self.id,
            'amount': self.amount,
            'user_id': self.user_id,
        }

    @classmethod
    async def get_invoice_from_user(cls, invoice_id: int, user_id: int):
        get_invoice_query = (
            select(Invoice).where(Invoice.user_id == user_id, Invoice.id == invoice_id)
        )
        scalars_invoices = await async_db_session.scalars(get_invoice_query)
        invoice = scalars_invoices.first()
        return invoice

    async def payment(self, amount, transaction_id):
        # write_off_invoice_query = (
        #     update(Invoice).where(Invoice.id == self.id).values(amount=self.amount + amount).execution_options(
        #         synchronize_session="fetch")
        # )
        self.amount = amount + self.amount
        transaction = Transaction(id=transaction_id, invoices_id=self.id, amount=amount)

        async_db_session.add(transaction)
        await async_db_session.commit()


class Product(BaseModel):
    __tablename__ = 'products'
    name = Column(String(120))
    discription = Column(String)
    price = Column(Float)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'discription': self.discription,
            'price': self.price
        }


class Transaction(BaseModel):
    __tablename__ = 'transactions'
    invoices_id = Column(Integer, ForeignKey('invoices.id'))
    invoice = relationship('Invoice', back_populates='transactions')
    amount = Column(Float)

    def to_dict(self):
        return {
            'invoice_id': self.invoices_id,
            'amount': self.amount
        }


def scalars_to_json(scalar_query):
    return json(list(map(lambda x: x.to_dict(), scalar_query.all())))
# asyncio.run(async_db_session.create_all())
