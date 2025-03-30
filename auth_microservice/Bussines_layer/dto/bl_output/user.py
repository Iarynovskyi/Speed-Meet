from marshmallow import Schema, fields


class OutputUser(Schema):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
