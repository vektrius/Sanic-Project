from sanic import Blueprint
from sanic_jwt import inject_user, protected
from sqlalchemy import select

from testquest.database import async_db_session
from testquest.models import User, scalars_to_json

admin = Blueprint("admin", url_prefix="/admin")

@admin.route("/users",methods=["GET"])
@inject_user()
@protected()
async def users(request, user):
    if not user.is_admin:
        raise Exception("You not have acces")

    result_query = await async_db_session.scalars((select(User)))
    return scalars_to_json(result_query)



