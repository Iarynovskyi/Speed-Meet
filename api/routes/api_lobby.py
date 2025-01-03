from flask import Blueprint, request
from api.routes.cache import cache

CACHE_TIMEOUT_SECONDS = 60 * 1.3
lobby_app = Blueprint('lobby_app', __name__)

@lobby_app.route('/', methods=['GET'])
def lobby_endpoint():
    return 'Welcome to Speed Meet!'
