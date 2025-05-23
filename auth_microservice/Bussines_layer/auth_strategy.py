from abc import ABC, abstractmethod
from enum import Enum
import bcrypt
import requests
from flask import current_app, request
from oauthlib.oauth2 import WebApplicationClient
from auth_microservice.Data_layer.models import User
from .dto.api_input import InputUserLogInDTO
from .dto.bl_output import OutputLogin
from typing import Generic, TypeVar

T = TypeVar("T")

class AuthStrategies(Enum):
    SIMPLE = "simple"
    GOOGLE = "google"


class AuthHandler(ABC, Generic[T]):
    def __init__(self, user_service):
        self._user_service = user_service
        
    def _is_suspicious_login(self, user_id: int, current_ip:str, current_device:str) -> bool:
            refresh_entry = self._user_service.get_valid_refresh_token_by_user(user_id)
            if not refresh_entry:
                return False  

            suspicious_conditions = [
                refresh_entry.last_ip and refresh_entry.last_ip == current_ip,
                refresh_entry.last_device and refresh_entry.last_device != current_device,
                self._user_service.is_nonce_used(user_id, refresh_entry.nonce)
            ]

            return any(suspicious_conditions) 

    @abstractmethod
    def _authenticate(self, credentials: T):
        pass
    
    async def authenticate(self, credentials: T):
        result = await self._authenticate(credentials)
        if result:
            self._is_suspicious_login(result.user_id, credentials.current_ip, credentials.current_device)
        return result

class AuthManager(AuthHandler):
    def __init__(self, user_service):
        self._user_service = user_service
        self.strategies = {
            AuthStrategies.SIMPLE.value: SimpleAuthHandler(user_service = self._user_service),
            AuthStrategies.GOOGLE.value: GoogleAuthHandler(user_service = self._user_service),
        }
   

    async def _authenticate(self, credentials: T):
        strategy = credentials.auth_provider
        if strategy not in self.strategies:
            pass
            # raise IncorrectLogInStrategyError(strategy)

        return await self.strategies[strategy].authenticate(credentials)


class SimpleAuthHandler(AuthHandler[T]):
    async def _authenticate(self, credentials: T):
        user = self._user_service.get_user_by_email_or_username(credentials.email_or_username, credentials.email_or_username)

        if not user:
            self._user_service._logger.warning("User does not exist")
            pass
            # raise UserDoesNotExistError(credentials.email_or_username)

        if not bcrypt.checkpw(credentials.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            self._user_service._logger.warning("Some log in data is incorrect")
            pass
            # raise IncorrectUserDataError()

        token = await self._user_service.get_generate_auth_token(user)

        return OutputLogin(email = user.email, token = token, user_id= user.user_id, username = user.username, new_user = False, access_token = None, refresh_token = None)


class GoogleAuthHandler(AuthHandler[T]):
    async def _authenticate(self, credentials: T):
        with current_app.app_context():
            client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
            token_url, headers, body = client.prepare_token_request(
                current_app.config['TOKEN_URL'],
                client_secret=current_app.config['GOOGLE_CLIENT_SECRET'],
                authorization_response=request.url,
                redirect_url=current_app.config['REDIRECT_URI']
            )
        token_response = requests.post(token_url, headers=headers, data=body)

        if not token_response.ok:
            pass
            #raise InvalidAuthenticationDataError(credentials.auth_provider)

        client.parse_request_body_response(token_response.text)

        user_info_response = requests.get(
            current_app.config['USER_INFO_URL'],
            headers={'Authorization': f'Bearer {client.token["access_token"]}'}
        )

        if not user_info_response.ok:
            pass
            # raise InvalidAuthenticationDataError(credentials.auth_provider)

        data = user_info_response.json()
        user_info = InputUserLogInDTO().load(data)

        user = self._user_service.get_user_by_email_or_username(email=user_info.email)
        output_login = OutputLogin(email=user_info.email, token=None, user_id=None, username=None, new_user=True, access_token = None, refresh_token = None)

        if not user:
            user = User(email=user_info.email, username=user_info.email.split('@')[0])
            new_user = self._user_service.create_user(user)
            output_login.user_id = new_user.user_id
            output_login.username = new_user.username
            await self._user_service.create_tokens(user=output_login)
        else:
            output_login.new_user = False   
        
        token = await self._user_service.get_generate_auth_token(user)
        
        output_login.token = token
        output_login.user_id = user.user_id
        output_login.username = user.username

        return output_login