from flask import Flask
from flask_cors import CORS
from api.routes import api_lobby
from api.routes.cache import cache


def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['JSON_AS_ASCII'] = False
    cache.init_app(app)

    app.register_blueprint(api_lobby.lobby_app, url_prefix='/lobby')

    return app


app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5695, debug=True)

