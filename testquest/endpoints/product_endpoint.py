from sanic import Blueprint, text, json
from sanic_ext import validate
from sanic_ext.extensions.openapi import openapi
from sanic_jwt import protected, inject_user
from sqlalchemy import select, update
from sqlalchemy.sql import Delete

from testquest.database.database import async_db_session
from testquest.database.models import Product, scalars_to_json, User, Invoice
from testquest.exceptions import ObjectNotFoundException, NotEnoughBalance, OnlyAdminException
from testquest.swagger.swagger_model import ProductOpenAPIModel, ProductOpenAPIBuyModel
from testquest.validators import BuyProductValidator, ProductValidator, ProductUpdateValidator

products = Blueprint("products", url_prefix="/product")


@products.route("/", methods=["GET"])
@openapi.response(200, [ProductOpenAPIModel])
@protected()
async def products_list(request):
    result_query = await async_db_session.scalars((select(Product)))
    return scalars_to_json(result_query)


@products.route("/buy", methods=["POST"])
@openapi.body({"application/json": ProductOpenAPIBuyModel},
              description="Take product id and you invoice id",
              required=True, )
@inject_user()
@protected()
@validate(json=BuyProductValidator)
async def buy_product(request, user: User, body: BuyProductValidator):
    product_id = body.product_id
    invoice_id = body.invoice_id

    product = await async_db_session.get(Product, product_id)
    invoice = await Invoice.get_invoice_from_user(invoice_id, user.id)

    if product is None:
        raise ObjectNotFoundException

    if invoice is None:
        raise ObjectNotFoundException

    finaly_amount = invoice.amount - product.price

    if finaly_amount < 0:
        raise NotEnoughBalance

    write_off_invoice_query = (
        update(Invoice).where(Invoice.id == invoice.id).values(amount=finaly_amount).execution_options(
            synchronize_session="fetch")
    )

    await async_db_session.execute(write_off_invoice_query)
    await async_db_session.commit()

    return text("Succes buy")


@products.route("/", methods=["POST"])
@openapi.body({"application/json": ProductOpenAPIModel},
              description="Create Product",
              required=True, )
@openapi.response(200, ProductOpenAPIModel)
@inject_user()
@protected()
@validate(json=ProductValidator)
async def create_product(request, user: User, body: ProductValidator):
    if not user.is_admin:
        raise OnlyAdminException
    product = Product(name=body.name,
                      discription=body.discription,
                      price=body.price)
    async_db_session.add(product)

    await async_db_session.commit()
    return json(product.to_dict())


@products.route("/<product_id:int>", methods=["PUT"])
@openapi.body({"application/json": ProductOpenAPIModel},
              description="Update Product, not all fields are required",
              required=False, )
@inject_user()
@protected()
@validate(json=ProductUpdateValidator)
async def update_product(request, user: User, body: ProductUpdateValidator, product_id: int):
    if not user.is_admin:
        raise OnlyAdminException

    update_fields = dict(filter(lambda x: x[1] is not None, body.dict().items()))

    product_update_query = (
        update(Product).where(Product.id == product_id).values(**update_fields).execution_options(
            synchronize_session="fetch")
    )
    await async_db_session.execute(product_update_query)
    await async_db_session.commit()
    return text('Updated product!')


@products.route("/<product_id:int>", methods=["DELETE"])
@openapi.description("Delete product on product id")
@inject_user()
@protected()
async def delete_product(request, user: User, product_id: int):
    if not user.is_admin:
        raise OnlyAdminException

    product = await async_db_session.get(Product, product_id)

    if product is None:
        raise ObjectNotFoundException

    product_update_query = (
        Delete(Product).where(Product.id == product_id)
    )
    await async_db_session.execute(product_update_query)
    await async_db_session.commit()
    return text('Deleted product!')
