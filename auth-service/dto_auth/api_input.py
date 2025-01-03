from marshmallow import Schema, fields, pre_load

class BaseDTO(Schema):
    @pre_load
    def check_min_value(self, data, **kwargs):
        for field in data:
            if isinstance(data[field], int) and data[field] < 0:
                data[field] = None
        return data

    @pre_load
    def clean_letter(self, data, **kwargs):
        if 'letter' in data and data['letter']:
            data['letter'] = ' '.join(data['letter'].split()).lower()
        return data


class UserDTO(BaseDTO):
    username = fields.Str(required=False, missing=None)
    password = fields.Str(required=False, missing=None)
    email = fields.Str(required=False, missing=None)

