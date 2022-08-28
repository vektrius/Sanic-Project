from pydantic import ValidationError
from sanic import text, Blueprint
from sanic_jwt import protected, inject_user
from sqlalchemy import select, update

from testquest.database import async_db_session
from testquest.models import Product, scalars_to_json, Invoice
from testquest.validators import BuyProductValidator

products = Blueprint("products", url_prefix="/product")


@products.route("/", methods=["GET"])
@protected()
async def products_list(request):
    result_query = await async_db_session.scalars((select(Product)))
    return scalars_to_json(result_query)


@products.route("/buy", methods=["POST"])
@inject_user()
@protected()
async def buy_product(request, user):
    try:
        request_data = BuyProductValidator.parse_obj(request.json)
    except ValidationError as e:
        return e.json()

    product_id = request_data.product_id
    invoice_id = request_data.invoice_id

    product = await async_db_session.get(Product, product_id)
    invoice = await Invoice.get_invoice_from_user(invoice_id, user.id)

    if product is None:
        raise Exception("Product not query")

    if invoice is None:
        raise Exception("Invoice not query")

    finaly_amount = invoice.amount - product.price

    write_off_invoice_query = (
        update(Invoice).where(Invoice.id == invoice.id).values(amount=finaly_amount).execution_options(
            synchronize_session="fetch")
    )

    await async_db_session.execute(write_off_invoice_query)
    await async_db_session.commit()

    return text("Succes buy")
