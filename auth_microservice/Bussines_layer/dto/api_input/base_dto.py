import re
from collections import namedtuple
from marshmallow import Schema, pre_load, post_load, ValidationError, EXCLUDE


class BaseDTO(Schema):
    class Meta:
        unknown = EXCLUDE

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

    @pre_load
    def to_lower(self, data, **kwargs):
        if 'auth_provider' in data and data['auth_provider']:
            data['auth_provider'] = data['auth_provider'].lower()
        return data

    @post_load
    def make_object(self, data, **kwargs):
        class_name = self.__class__.__name__.replace("Schema", "") or "DTO"
        return namedtuple(class_name, data.keys())(*data.values())

    @pre_load
    def validate_email(self, data, **kwargs):
        if 'email' in data:
            if not re.match(r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', data['email']):
                raise ValidationError("Invalid email format", field_name="email")
        return data

    @pre_load
    def validate_username(self, data, **kwargs):
        if 'username' in data:
            regex = re.compile(r'[ @!#$%^&*()<>?/\|}{~:;,+=]')
            if regex.search(data['username']) or not data['username']:
                raise ValidationError("Invalid username format", field_name="username")
        return data

    @pre_load
    def validate_password(self, data, **kwargs):
        if 'password' in data:
            regex = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?!.*\s){8,}')
            if not re.match(regex, data['password']):
                raise ValidationError("Invalid password format", field_name="password_hash")
        return data

    # @pre_load
    # def process_models(self, data, **kwargs):
    #     if "models" in data and isinstance(data["models"], list):
    #         processed_models = []
    #         for item in data["models"]:
    #             dto_class = self.detect_dto(item)
    #             if dto_class:
    #                 processed_models.append(dto_class().load(item))
    #         data["models"] = processed_models
    #     return data
