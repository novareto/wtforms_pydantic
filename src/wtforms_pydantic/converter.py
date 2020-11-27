import datetime
import decimal
from collections import namedtuple

import pydantic
import wtforms.fields
import wtforms.fields.html5
import wtforms.validators


class Converter:
    """convert pydantic fields into wtforms fields.
    """

    converters = {
        str: wtforms.fields.StringField,
        int: wtforms.fields.IntegerField,
        float: wtforms.fields.FloatField,
        decimal.Decimal: wtforms.fields.DecimalField,
        datetime.date: wtforms.fields.html5.DateField,
        datetime.datetime: wtforms.fields.html5.DateTimeField,
        datetime.time: wtforms.fields.html5.TimeField,
        pydantic.SecretStr: wtforms.fields.PasswordField,
        pydantic.networks.EmailStr: wtforms.fields.html5.EmailField
    }

    @staticmethod
    def field_options(field: dict, **override):
        options = {
            "label": field.field_info.title or field.name,
            "validators": [],
            "filters": [],
            "default": field.default or field.field_info.default_factory,
            'description': field.field_info.description or ''
        }
        required = override.pop('required', field.required)
        if required:
            options["validators"].append(
                wtforms.validators.DataRequired()
            )
        else:
            options["validators"].append(
                wtforms.validators.Optional()
            )
        options.update(override)
        return options

    @classmethod
    def convert(cls, fields: dict, **overrides):

        wtfields = {}
        for name, field in fields.items():
            wtf_type = cls.converters.get(field.outer_type_)
            if wtf_type is None:
                raise TypeError(
                    f'No converter found for `{field.type_}.`')

            options = cls.field_options(field, **overrides.get(name, {}))
            wtfields[name] = wtf_type(**options)

        return wtfields


def model_fields(model, only=None, exclude=None) -> dict:
    if (only or exclude) and not bool(only) ^ bool(exclude):
        raise AssertionError(
            'You need to specify either `only` or `exclude`')

    if only:
        return {
            name: field for name, field in model.__fields__.items()
            if name in only
        }
    if exclude:
        return {
            name: field for name, field in model.__fields__.items()
            if name not in exclude
        }
    return model.__fields__
