from sanic import Blueprint, Request, HTTPResponse
from sanic_ext.extensions.openapi import openapi
from sanic_jwt import inject_user, protected
from sqlalchemy import select

from database.database import async_db_session
from database.models import Invoice, scalars_to_json, User, Transaction
from swagger.swagger_model import InvoicesOpenAPIModel, TransactionOpenAPIModel

invoices = Blueprint("invoices", url_prefix="/invoices")


@invoices.route("/", methods=["GET"])
@openapi.response(200,[InvoicesOpenAPIModel])
@openapi.summary("Get invoices list")
@inject_user()
@protected()
async def invoices_list(request: Request, user: User) -> HTTPResponse:
    invoices_get_query = (
        select(Invoice).where(Invoice.user_id == user.id)
    )
    scalars_invoices = await async_db_session.scalars(invoices_get_query)

    return scalars_to_json(scalars_invoices)


@invoices.route("/<invoice_id:int>/transaction")
@openapi.response(200,[TransactionOpenAPIModel])
@openapi.summary("Get transaction list")
@inject_user()
@protected()
async def transaction_list(request: Request, user: User, invoice_id: int) -> HTTPResponse:
    get_invoice_from_user = (
        select(Transaction).join(Invoice, Transaction.invoices_id == invoice_id).where(Invoice.user_id == user.id)
    )
    results = await async_db_session.scalars(get_invoice_from_user)
    return scalars_to_json(results)
