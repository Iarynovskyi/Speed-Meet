from .base_dto import BaseDTO
from marshmallow import fields

class NewPasswordDTO(BaseDTO):
    password = fields.Str(required=True)
