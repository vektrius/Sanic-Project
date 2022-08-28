from sanic import Blueprint, json
from sanic_ext.extensions.openapi import openapi
from sanic_jwt import inject_user, protected
from sqlalchemy import select

from database.database import async_db_session
from database.models import User, scalars_to_json, Invoice
from exceptions import OnlyAdminException
from swagger.swagger_model import UserOpenAPIModel, InvoicesOpenAPIModel

admin = Blueprint("admin", url_prefix="/admin")


@admin.route("/users",methods=["GET"])
@openapi.response(200,[UserOpenAPIModel])
@openapi.summary("Get users list")
@inject_user()
@protected()
async def users(request, user):
    if not user.is_admin:
        raise OnlyAdminException("You not have acces")

    result_query = await async_db_session.scalars((select(User)))
    return scalars_to_json(result_query)


@admin.route("/users/<user_id:int>/invoices")
@openapi.response(200,[InvoicesOpenAPIModel])
@openapi.summary("Get invoices list")
@inject_user()
@protected()
async def invoices(request,user,user_id):
    if not user.is_admin:
        raise OnlyAdminException("You not have acces")

    invoices_get_query = (
        select(Invoice).where(Invoice.user_id == user_id)
    )
    scalars_invoices = await async_db_session.scalars(invoices_get_query)

    return scalars_to_json(scalars_invoices)

@admin.route("/users/<user_id:int>/activate",methods=["PUT"])
@openapi.response(200,UserOpenAPIModel)
@openapi.description("Activate user on user id")
@inject_user()
@protected()
async def activate_user(request,user,user_id):
    if not user.is_admin:
        raise OnlyAdminException("You not have acces")

    select_user = await async_db_session.get(User,user_id)
    await User.is_active_set(user=select_user,value=True)
    return json(select_user.to_dict())


@admin.route("/users/<user_id:int>/deactivate",methods=["PUT"])
@openapi.response(200,UserOpenAPIModel)
@openapi.description("Deactivate user on user id")
@inject_user()
@protected()
async def deactivate_user(request,user,user_id):
    if not user.is_admin:
        raise OnlyAdminException("You not have acces")

    select_user = await async_db_session.get(User,user_id)
    await User.is_active_set(user=select_user,value=False)
    return json(select_user.to_dict())
