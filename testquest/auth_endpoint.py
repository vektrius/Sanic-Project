from typing import TypedDict

from Crypto.Hash import SHA256
from pydantic import ValidationError
from sanic import text, Blueprint
from sanic_jwt import exceptions

from testquest.app import SECRET_KEY
from testquest.database import async_db_session
from testquest.models import User
from testquest.validators import UserValidator

auth = Blueprint('auth', url_prefix="/auth")


async def authenticate(request, *args, **kwargs):
    try:
        user_data = UserValidator.parse_obj(request.json)
    except ValidationError as e:
        return e.json()

    username = user_data.username
    password = user_data.password

    user = await User.authenticate(username, password)
    return user


class ReceivedUser(TypedDict):
    user_id: int
    exp: int


async def retrieve_user(request, user: ReceivedUser, *args, **kwargs):
    user = await async_db_session.get(User, user['user_id'])
    return user


@auth.route("/registration", methods=["POST"])
async def registration(request):
    try:
        user_data = UserValidator.parse_obj(request.json)
    except ValidationError as e:
        return e.json()

    username = user_data.username
    password = user_data.password

    user = User(username=username, password=password)

    async_db_session.add(user)
    await async_db_session.commit()
    user_hash = SHA256.new(f'{user.username}.{user.password}.{SECRET_KEY}'.encode()).hexdigest()
    activate_url = f'/activate?hash={user_hash}&username={username}'
    return text(f"Go to url {activate_url}")


@auth.route("/activate", methods=["GET"])
async def activate(request):
    user_hash = request.args.get('hash', None)
    username = request.args.get('username', None)
    await User.activate(username=username, hash=user_hash)
    return text('User activated!')
