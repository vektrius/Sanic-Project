from Crypto.Hash import SHA1
from pydantic import ValidationError
from sanic import Blueprint, json

from testquest.app import SECRET_KEY
from testquest.database import async_db_session
from testquest.models import Invoice, Transaction
from testquest.validators import WebhookValidator

webhook = Blueprint("webhook", url_prefix='/payment')


@webhook.route("/webhook", methods=["POST"])
async def payment(request):
    try:
        data = WebhookValidator.parse_obj(request.json)
    except ValidationError as e:
        return e.json()

    signature = data.signature
    transaction_id = data.transaction_id
    user_id = data.user_id
    invoice_id = data.invoice_id
    amount = data.amount

    if not await _check_signature(signature, transaction_id,
                                  user_id, invoice_id, amount):
        return Exception("Error Signature")

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
