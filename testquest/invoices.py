from sanic import Blueprint, Request, HTTPResponse
from sanic_jwt import inject_user, protected
from sqlalchemy import select

from testquest.database import async_db_session
from testquest.models import Invoice, scalars_to_json, User, Transaction

invoices = Blueprint("invoices", url_prefix="/invoices")


@invoices.route("/", methods=["GET"])
@inject_user()
@protected()
async def invoices_list(request: Request, user: User) -> HTTPResponse:
    invoices_get_query = (
        select(Invoice).where(Invoice.user_id == user.id)
    )
    scalars_invoices = await async_db_session.scalars(invoices_get_query)

    return scalars_to_json(scalars_invoices)


@invoices.route("/<invoice_id:int>/transaction")
@inject_user()
@protected()
async def transaction_list(request: Request, user: User, invoice_id: int) -> HTTPResponse:
    get_invoice_from_user = (
        select(Transaction).join(Invoice, Transaction.invoices_id == invoice_id).where(Invoice.user_id == user.id)
    )
    results = await async_db_session.scalars(get_invoice_from_user)
    return scalars_to_json(results)
