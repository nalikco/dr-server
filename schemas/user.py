from marshmallow import Schema, fields, validate, validates_schema
from .validations import name_regex, register_other_validations


class UserSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    created_at = fields.DateTime()


class LoginQueryArgsSchema(Schema):
    email = fields.Email(
        required=True,
    )
    password = fields.Str(
        required=True,
    )


class SignUpQueryArgsSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[validate.Length(max=124, min=2)]
    )
    first_name = fields.Str(
        required=True,
        validate=[validate.Length(max=50, min=1), name_regex]
    )
    last_name = fields.Str(
        required=True,
        validate=[validate.Length(max=100, min=1), name_regex]
    )
    password = fields.Str(
        required=True,
        validate=[validate.Length(max=124, min=6)]
    )
    password_repeat = fields.Str(required=True)

    @validates_schema
    def validate_user(self, data, **kwargs):
        register_other_validations(data)
