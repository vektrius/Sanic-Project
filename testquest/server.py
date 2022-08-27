import asyncio
import os

from Crypto.Hash import SHA256
from sanic import Sanic
from sanic.response import text, json
from sanic_ext import Extend, serializer
from sanic_jwt import Initialize, exceptions
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import create_async_engine, async_session

from testquest.database import async_db_session
from testquest.models import User, Product

SECRET_KEY = os.getenv('SECRET_KEY')


async def authenticate(request, *args, **kwargs):
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")

    user = await User.authenticate(username, password)
    return user


app = Sanic("MyHelloWorldApp")
Initialize(
    app,
    authenticate=authenticate,
    secret=os.getenv('SECRET_KEY'),
)


@app.post("/registration")
async def registration(request):
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User(username=username, password=password)

    async_db_session.add(user)
    await async_db_session.commit()
    user_hash = SHA256.new(f'{user.username}.{user.password}.{SECRET_KEY}'.encode()).hexdigest()
    activate_url = f'/activate?hash={user_hash}&username={username}'
    return text(f"Go to url {activate_url}")


@app.get("/activate")
async def activate(request):
    user_hash = request.args.get('hash', None)
    username = request.args.get('username', None)
    get_user_query = select(User).where(User.username == username)
    results = await async_db_session.execute(get_user_query)
    user = results.scalars().first()

    if user is None:
        raise

    current_user_hash = SHA256.new(f'{user.username}.{user.password}.{SECRET_KEY}'.encode()).hexdigest()

    if current_user_hash == user_hash:
        update_user_query = (
            update(User).where(User.id == user.id).values(is_active=True).execution_options(synchronize_session="fetch")
        )
        await async_db_session.execute(update_user_query)
        await async_db_session.commit()

    return text('User activated!')



@app.get("product/")
async def products(request):
    products_get_query = (select(Product))
    print(products_get_query)
    return text('test')