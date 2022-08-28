from typing import TypedDict

from Crypto.Hash import SHA256
from sanic import Blueprint, text
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sqlalchemy import select

from app import SECRET_KEY
from database.database import async_db_session
from database.models import User
from exceptions import HashException, ObjectNotFoundException
from swagger.swagger_model import UserOpenAPIModel, UserRegistrationOpenAPIModel
from validators import UserValidator

auth = Blueprint('auth', url_prefix="/auth")

@validate(json=UserValidator)
async def authenticate(request, body: UserValidator,*args, **kwargs):
    username = body.username
    password = body.password

    user = await User.authenticate(username, password)
    return user


class ReceivedUser(TypedDict):
    user_id: int
    exp: int


async def retrieve_user(request, user: ReceivedUser, *args, **kwargs):
    user = await async_db_session.get(User, user['user_id'])
    return user


@auth.route("/registration", methods=["POST"])
@openapi.body({"application/json": UserRegistrationOpenAPIModel},
              description="Registration user",
              required=True, )
@openapi.response(200,"url activate")
@validate(json=UserValidator)
async def registration(request,body: UserValidator):
    username = body.username
    password = body.password

    user = User(username=username, password=password)

    async_db_session.add(user)
    await async_db_session.commit()
    user_hash = SHA256.new(f'{user.username}.{user.password}.{SECRET_KEY}'.encode()).hexdigest()
    activate_url = f'/auth/activate?hash={user_hash}&username={username}'
    return text(f"Go to url {activate_url}")


@auth.route("/activate", methods=["GET"])
@openapi.description("Activated user")
async def activate(request):
    user_hash = request.args.get('hash', None)
    username = request.args.get('username', None)

    user = await _get_user_from_username(username)

    true_user_hash = SHA256.new(f'{user.username}.{user.password}.{SECRET_KEY}'.encode()).hexdigest()
    if not true_user_hash == user_hash:
        raise HashException("Hash error")

    await User.is_active_set(user=user,value=True)
    return text('User activated!')


async def _get_user_from_username(username):
    get_user_query = select(User).where(User.username == username)
    results = await async_db_session.execute(get_user_query)
    user = results.scalars().first()
    if user is None:
        raise ObjectNotFoundException
    return user