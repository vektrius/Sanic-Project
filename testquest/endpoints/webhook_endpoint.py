from Crypto.Hash import SHA1
from sanic import Blueprint, json
from sanic_ext import validate

from app import SECRET_KEY
from database.database import async_db_session
from exceptions import HashException
from database.models import Invoice, Transaction
from validators import WebhookValidator

webhook = Blueprint("webhook", url_prefix='/payment')


@webhook.route("/webhook", methods=["POST"])
@validate(json=WebhookValidator)
async def payment(request,body: WebhookValidator):
    signature = body.signature
    transaction_id = body.transaction_id
    user_id = body.user_id
    invoice_id = body.invoice_id
    amount = body.amount

    if not await _check_signature(signature, transaction_id,
                                  user_id, invoice_id, amount):
        return HashException

    invoice = await _payment_to_invoice(user_id, invoice_id, transaction_id, amount)
    return json(invoice.to_dict())


async def _check_signature(signature: str, transaction_id: int,
                           user_id: int, invoice_id: int, amount: float) -> bool:
    true_signature = SHA1.new(f'{SECRET_KEY}:{transaction_id}:{user_id}:{invoice_id}:{amount}'.encode()).hexdigest()
    return true_signature == signature


async def _payment_to_invoice(user_id: int, invoice_id: int, transaction_id: int, amount: float) -> Invoice:
    invoice = await Invoice.get_invoice_from_user(invoice_id, user_id)
    if invoice is None:
        return await _add_invoice_to_user(user_id, transaction_id, invoice_id, amount)

    await invoice.payment(amount=amount, transaction_id=transaction_id)
    return invoice


async def _add_invoice_to_user(user_id: int, transaction_id: id, invoice_id: int, amount: float) -> Invoice:
    invoice = Invoice(id=invoice_id, amount=amount, user_id=user_id)
    transcation = Transaction(id=transaction_id, amount=amount, invoices_id=invoice_id)
    async_db_session.add(invoice)
    async_db_session.add(transcation)
    await async_db_session.commit()

    return invoice
