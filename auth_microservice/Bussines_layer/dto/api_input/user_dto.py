from .base_dto import BaseDTO
from marshmallow import fields


class InputUserDTO(BaseDTO):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
