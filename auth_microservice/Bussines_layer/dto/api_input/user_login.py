from .base_dto import BaseDTO
from marshmallow import fields


class InputUserLogInDTO(BaseDTO):
    email = fields.Str(required=False, missing=None)
    email_or_username = fields.Str(required=False, missing=None)
    password = fields.Str(required=False, missing=None)
    auth_provider = fields.String(required=False, missing=None)
    current_ip = fields.String(required=False, missing=None)
    current_device = fields.String(required=False, missing=None)
