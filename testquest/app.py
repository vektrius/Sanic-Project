import os

from sanic import Sanic

SECRET_KEY = os.getenv('SECRET_KEY')

app = Sanic("Test")
