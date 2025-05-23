from flask import current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from auth_microservice.Bussines_layer.dto.bl_output import OutputLogin
from auth_microservice.Data_layer.models import User
import bcrypt
# from logger.logger import Logger
from jinja2 import Environment, FileSystemLoader
import os
from flask_jwt_extended import create_access_token,create_refresh_token, decode_token
from .auth_strategy import AuthManager
from auth_microservice.Data_layer.dto import JwtDTO, RefreshTokenDTO, AdditionalClaimsDTO
from datetime import datetime
import time
import hashlib
from flask_jwt_extended import get_jwt
from auth_microservice.API.request_helper import RequestHelper
from types import SimpleNamespace


JTI = 'jti'
SPORT_TYPE = "sport"
TEAM_TYPE = "team"
PREFERENCES = "preferences"
SPORTS = "sports_id"


class UserAuthLogic:
    def __init__(self, user_dal, preferences_dal, sport_dal, access_tokens_dal, refresh_dal, teams_dal):
        self._user_dal = user_dal
        self._access_tokens_dal = access_tokens_dal
        self._refresh_dal = refresh_dal
        self._serializer = URLSafeTimedSerializer(current_app.secret_key)
        # self._logger = Logger("logger", "all.log").logger


    def has_ip_country_changed(self, stored_country: str) -> bool:
        current_country = self.get_country_from_ip()
        return stored_country != current_country

    def has_device_changed(self, stored_device: str) -> bool:
        current_device = self.get_user_device()
        return stored_device != current_device

    def generate_nonce(self):
        nonce = hashlib.sha256(f"{time.time()}{os.urandom(16)}".encode()).hexdigest()
        return nonce
    
    def is_nonce_used(self, user_id: int, nonce: str) -> bool:
        return self._refresh_dal.is_nonce_used(user_id, nonce)
    
    def get_valid_refresh_token_by_user(self, user_id: int):
        return self._refresh_dal.get_valid_refresh_token_by_user(user_id)


    def get_user_by_email_or_username(self, email=None, username=None):
        return self._user_dal.get_user_by_email_or_username(email, username)


    def get_existing_user(self, email=None, username=None):
        return self._user_dal.get_existing_user(email, username)


    async def sign_up_user(self, email, username, password):
        existing_user = self.get_existing_user(email = email, username = username)
        if existing_user:
            pass
            # self._logger.debug("User already exist")
            # raise UserAlreadyExistError()

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        new_user = User(email = email, username = username, password_hash = hashed_password.decode('utf-8'))
        
        self.create_user(new_user)
        
        user = OutputLogin(email = new_user.email, token = new_user, user_id = new_user.user_id, username = new_user.username, new_user = True, access_token=None, refresh_token=None)
        access_token, refresh_token = await self.create_tokens(user)
        user.access_token = access_token
        user.refresh_token = refresh_token
        
        return user
    

    def revoke_all_refresh_and_access_tokens(self, user_id: int) -> int:
        return self._refresh_dal.revoke_all_refresh_and_access_tokens_for_user(user_id)
    
    
    def create_user(self, new_user):
        return self._user_dal.create_user(new_user)


    def request_password_reset(self, email: str):
        existing_user = self.get_user_by_email_or_username(email = email)
        if not existing_user:
            pass
            # raise UserDoesNotExistError(email)

        token = self.__get_reset_token(existing_user.email)
        self.__send_reset_email(existing_user, token)


    def __message_to_user_gmail(self, user: User, reset_url):
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        env = Environment(loader = FileSystemLoader(template_dir))
        template = env.get_template("reset_password_email.html")

        return template.render(username = user.username, reset_url = reset_url)


    def __send_reset_email(self, user: User, token: str):
        reset_url = url_for('login_app.reset_password', token = token, _external = True)
        msg = Message(
            'Password Reset Request',
            sender = current_app.config['MAIL_USERNAME'],
            recipients = [user.email],
            html = self.__message_to_user_gmail(user, reset_url)
        )
        current_app.extensions['mail'].send(msg)


    def __get_reset_token(self, email) -> str:
        user = self.get_user_by_email_or_username(email = email)
        if not user:
            pass
            # raise UserDoesNotExistError(email)

        return self._serializer.dumps(user.username, salt = "email-confirm")
    

    async def reset_user_password(self, token, new_password: str):
        username = self.confirm_token(token)
        user = self.get_user_by_email_or_username(username = username)
        if not user:
            pass
            # raise UserDoesNotExistError(username)

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

        self._user_dal.update_user_password(user, hashed_password.decode('utf-8')) 
        return user
        


    def confirm_token(self, token: str, expiration=3600):
        try:
            user = self._serializer.loads(token, salt = "email-confirm", max_age = expiration)
            return user

        except SignatureExpired:
            pass
            # raise SignatureExpiredError()
        except BadSignature:
            pass
            # raise IncorrectSignatureError()


    async def log_in(self, credentials):
        login_context = AuthManager(self)

        user = await login_context.authenticate(credentials)
        existing_access_token, existing_refresh_token = self._refresh_dal.get_valid_tokens_by_user(user.user_id)

        if existing_access_token and existing_refresh_token:
            user.access_token = existing_access_token
            user.refresh_token = existing_refresh_token
            return user
            
        else:
            access_token, refresh_token=await self.create_tokens(user=user)
            user.access_token = access_token
            user.refresh_token = refresh_token
            return user


    async def __generate_auth_token(self, user, salt):
        return self._serializer.dumps(user.email, salt = salt)


    async def get_generate_auth_token(self, user):
        return await self.__generate_auth_token(user, salt = "user-auth-token")
    
    def __get_user_id_from_token(self):
        jwt = get_jwt()
        user_id = jwt.get('sub')
        return user_id

    def save_tokens_to_db(self, user, access_token: str, refresh_token: str):
        decode_access_token = decode_token(access_token)
        decode_refresh_token = decode_token(refresh_token)
        
        access_expires_at = datetime.utcfromtimestamp(decode_access_token['exp'])
        refresh_expires_at = datetime.utcfromtimestamp(decode_refresh_token['exp'])

        access_jwt_dto = JwtDTO(
            user_id=user.user_id,
            jti=decode_access_token[JTI],   
            token_type="access",
            token=access_token,
            revoked=False,
            expires_at=access_expires_at
        )
        self._access_tokens_dal.save_access_token(access_jwt_dto)

        refresh_jwt_dto = JwtDTO(
            user_id=user.user_id,
            jti=decode_refresh_token[JTI],
            token_type="refresh",
            token=refresh_token,
            revoked=False,
            expires_at=refresh_expires_at  
        )
        id = self._access_tokens_dal.save_access_token(refresh_jwt_dto)

        refresh_dto = RefreshTokenDTO(
            id=id,
            user_id=user.user_id,
            last_ip=RequestHelper.get_country_from_ip(),
            last_device=RequestHelper.get_user_device(),
            nonce=self.generate_nonce()
        )
        self._refresh_dal.save_refresh_token(refresh_dto)


    async def create_tokens(self, user):
        additional_claims = AdditionalClaimsDTO(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            new_user=user.new_user
        )

        access_token = create_access_token(identity=user.email, additional_claims=additional_claims.model_dump())

        nonce = self.generate_nonce()

        refresh_claims_dict = additional_claims.model_dump()
        refresh_claims_dict["nonce"] = nonce
        refresh_claims = AdditionalClaimsDTO(**refresh_claims_dict)

        refresh_token = create_refresh_token(identity=user.email, additional_claims=refresh_claims.model_dump())

        self.save_tokens_to_db(user, access_token, refresh_token)

        return access_token, refresh_token
    
    async def create_access_token(self, user):
        additional_claims = AdditionalClaimsDTO(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            new_user=False
        )

        access_token = create_access_token(identity=user.email, additional_claims=additional_claims.model_dump())
        
        decode_access_token = decode_token(access_token)
        access_expires_at = datetime.utcfromtimestamp(decode_access_token['exp'])        
        
        access_jwt_dto = JwtDTO(
            user_id=user.user_id,
            jti=decode_access_token[JTI],   
            token_type="access",
            token=access_token,
            revoked=False,
            expires_at=access_expires_at
        )
        self._access_tokens_dal.save_access_token(access_jwt_dto)

        return access_token

        
        
    async def verify_nonce(self, user_email: str, token_nonce: str) -> bool:
        user = await self._user_dal.get_user_by_email(user_email)
        saved_nonce = self._refresh_dal.get_nonce_by_user_id(user.user_id)

        return saved_nonce == token_nonce


    async def update_refresh_token(self, user_email: str):
        user = await self._user_dal.get_user_by_email(user_email)
        
        refresh_dto = RefreshTokenDTO(
            user_id=user.user_id,
            last_ip=self.__get_country_from_ip(),
            last_device=self.get_user_device(),
            nonce=self.generate_nonce()
        )

        self._refresh_dal.update_refresh_token(user.user_id, refresh_dto)
        
    async def refresh_tokens(self): 
        current_refresh_token = get_jwt()  
        identity = current_refresh_token.get("sub")  
        user_data = self._user_dal.get_user_by_email(identity)
        user_data = SimpleNamespace(**user_data.__dict__, new_user=False)

        new_access_token, new_refresh_token = await self.create_tokens(user_data)
        
        user = OutputLogin(
            email=user_data.email,
            user_id=user_data.user_id,
            token=new_access_token,
            username=user_data.username,
            new_user=False,
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

        return user


    async def verify_jwt(self, token: str):
        pass