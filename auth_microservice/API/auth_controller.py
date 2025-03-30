from flask import request, redirect
from flask_smorest import Blueprint
from auth_microservice.Bussines_layer.dto.api_input import InputUserDTO, InputUserLogInDTO, NewPasswordDTO
from .common_response import CommonResponse
# from logger.logger import Logger
from dependency_injector.wiring import inject, Provide
from auth_microservice.Bussines_layer.user_auth_logic import UserAuthLogic
from .request_helper import RequestHelper
from auth_microservice.Bussines_layer.DI_container import Container
from flask_jwt_extended import jwt_required
import os
from dotenv import load_dotenv


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
load_dotenv()
FRONT_RESET_PASSWORD_URL = os.getenv('FRONT_RESET_PASSWORD_URL')

# logger = Logger("logger", "all.log")

auth_app = Blueprint('login_app', __name__, description="Login options", url_prefix='/user')


@auth_app.route('/sign-up', methods=['POST'])
@inject
# @handle_exceptions
# @logger.log_function_call()
async def create_account_endpoint(service: UserAuthLogic = Provide[Container.user_service]):
    try:
        data = request.get_json()
        dto = InputUserDTO().load(data)
        user = await service.sign_up_user(dto.email, dto.username, dto.password)

        response = await RequestHelper.set_tokens_and_create_response(user)
        return response

    except Exception as e:
        print(e)


@auth_app.route('/reset-password-request', methods=['POST'])
@inject
# @handle_exceptions
# @logger.log_function_call()
def request_password_reset(service: UserAuthLogic = Provide[Container.user_service]):
    try:
        data = request.get_json()
        dto = NewPasswordDTO().load(data)
        service.request_password_reset(dto.email)

        return CommonResponse().to_dict()

    except Exception as e:
        print(e)


@auth_app.route('/reset-password/<token>', methods=['GET', 'POST'])
@inject
# @handle_exceptions
# @logger.log_function_call()
async def reset_password(token, service: UserAuthLogic = Provide[Container.user_service]):
    try:
        if request.method == "GET":
            user = service.confirm_token(token)

            reset_front_url = f"{FRONT_RESET_PASSWORD_URL}/{token}"

            return redirect(reset_front_url)

        if request.method == "POST":
            data = request.get_json()
            dto = NewPasswordDTO().load(data)
            token = await service.reset_user_password(token, dto.password)

            return token

    except Exception as e:
        print(e)


@auth_app.route('/login', methods=['POST'])
@inject
# @handle_exceptions
# @logger.log_function_call()
async def log_in(service: UserAuthLogic = Provide[Container.user_service]):
    try:
        current_ip = RequestHelper.get_country_from_ip()
        current_device = RequestHelper.get_user_device()
        data = request.get_json()
        data.update({"current_ip": current_ip, "current_device": current_device})

        dto = InputUserLogInDTO().load(data)
        user = await service.log_in(dto)

        response = await RequestHelper.set_tokens_and_create_response(user)

        return response

    except Exception as e:
        print(e)


@auth_app.route("/refresh", methods=['POST'])
@jwt_required(refresh=True)
@inject
# @handle_exceptions
async def refresh(service: UserAuthLogic = Provide[Container.user_service]):
    try:
        user = await service.refresh_tokens()
        response = await RequestHelper.set_tokens_and_create_response(user)

        return response

    except Exception as e:
        print(e)


@auth_app.route("/verify", methods=['GET'])
@inject
# @handle_exceptions
# @logger.log_function_call()
async def verify_token(token: str, service: UserAuthLogic = Provide[Container.user_service]):
    try:
        decoded_token = service.verify_jwt(token)
        return jsonify(decoded_token)

    except CustomQSportException as e:
        logger.error(f"Error in /verify: {str(e)}")
        return get_custom_error_response(e)

