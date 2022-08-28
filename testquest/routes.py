from sanic import Blueprint
from sanic_jwt import Initialize

from testquest.app import app, SECRET_KEY
from testquest.endpoints.admin_endpoint import admin
from testquest.endpoints.auth_endpoint import auth, authenticate, retrieve_user
from testquest.endpoints.invoices_endpoint import invoices
from testquest.endpoints.product_endpoint import products
from testquest.endpoints.webhook_endpoint import webhook

main_blueprint = Blueprint.group(products,auth,admin,webhook,invoices,url_prefix='')

Initialize(
    app,
    authenticate=authenticate,
    secret=SECRET_KEY,
    retrieve_user=retrieve_user,
    url_prefix='/auth',
    path_to_authenticate='/login'
)

app.blueprint(main_blueprint)


def load_routes():
    print('Routes load!')