from sanic_routing import route

from testquest.app import app
import routes

if __name__ == '__main__':
    routes.load_routes()
    app.run(host='127.0.0.1',port='8000')