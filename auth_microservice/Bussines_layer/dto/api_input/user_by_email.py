from .base_dto import BaseDTO
from marshmallow import fields


class InputUserByEmailDTO(BaseDTO):
    email = fields.Str(required=True)
