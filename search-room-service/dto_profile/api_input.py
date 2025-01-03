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


class UserProfileDTO(BaseDTO):
    first_name = fields.Str(required=False, missing=None)
    last_name = fields.Str(required=False, missing=None)
    country = fields.Str(required=False, missing=None)
    age = fields.Integer(required=False, missing=None)
    gender = fields.Str(required=False, missing=None)


class UserPreferencesDTO(BaseDTO):
    gender = fields.Str(required=False, missing=None)
    age_min = fields.Int(required=False, missing=None)
    age_max = fields.Int(required=False, missing=None)
    country = fields.Str(required=False, missing=None)