from pydantic import ValidationError
from sanic import json

from testquest.app import app


class OnlyAdminException(Exception):
    def __str__(self):
        return "Only admin endpoint"


class HashException(Exception):
    def __str__(self):
        return "Wrong Hash"


class ObjectNotFoundException(Exception):
    def __str__(self):
        return "Object not Found"


class NotEnoughBalance(Exception):
    def __str__(self):
        return "Balance is not enough"



def admin_acces_handler(status):
    async def custom_error_handler(request, exception):
        return json({"succes": False, "error": str(exception)}, status=status)

    return custom_error_handler


app.error_handler.add(OnlyAdminException, admin_acces_handler(400))
app.error_handler.add(HashException, admin_acces_handler(400))
app.error_handler.add(ObjectNotFoundException, admin_acces_handler(400))
app.error_handler.add(NotEnoughBalance, admin_acces_handler(400))
app.error_handler.add(ValidationError, admin_acces_handler(400))
