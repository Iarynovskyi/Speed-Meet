from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
import os
from dotenv import load_dotenv
from auth_microservice.API.auth_controller import auth_app
from auth_microservice.API.cache import cache
from auth_microservice.Bussines_layer.DI_container import Container
from auth_microservice.Data_layer.session import DATABASE_URL


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cert_file = os.path.join(BASE_DIR, "localhost.pem")
key_file = os.path.join(BASE_DIR, "localhost-key.pem")

load_dotenv()
db = SQLAlchemy()
mail = Mail()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['JSON_AS_ASCII'] = False
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60 * 5
    cache.init_app(app)

    app.secret_key = os.getenv('SECRET_KEY')
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    mail.init_app(app)

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    jwt.init_app(app)

    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
    app.config['REDIRECT_URI'] = os.getenv('GOOGLE_REDIRECT_URI')
    app.config['AUTHORIZATION_BASE_URL'] = os.getenv('GOOGLE_AUTHORIZATION_BASE_URL')
    app.config['TOKEN_URL'] = os.getenv('GOOGLE_TOKEN_URL')
    app.config['USER_INFO_URL'] = os.getenv('GOOGLE_USER_INFO_URL')
    app.config['SCOPES'] = os.getenv('GOOGLE_SCOPES')

    app.config["API_TITLE"] = "Speed-Meet API"
    app.config["API_VERSION"] = "1.0"
    app.config["OPENAPI_VERSION"] = "3.0.2"

    app.container = Container()

    return app


def create_swagger_documentation():
    api = Api(app)
    SWAGGER_URL = '/swagger'
    API_URL = '/openapi.json'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "QSPORT API",
        },
    )

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    api.register_blueprint(auth_app, url_prefix='/')

    @app.route('/openapi.json')
    def openapi_spec():
        return jsonify(api.spec.to_dict())


app = create_app()

if __name__ == '__main__':
    create_swagger_documentation()
    app.run(host='0.0.0.0', port=9001, debug=True, use_reloader=True)

