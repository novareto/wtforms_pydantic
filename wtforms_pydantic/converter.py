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
        pydantic.SecretStr: wtforms.fields.PasswordField
    }

    @classmethod
    def convert(cls, fields: dict, **overrides):

        wtfields = {}
        for name, field in fields.items():
            wtf_type = cls.converters.get(field.type_)
            if wtf_type is None:
                raise TypeError(
                    f'No converter found for `{field.type_}.`')

            options = {
                "label": field.field_info.title or name,
                "validators": [],
                "filters": [],
                "default": field.default,
                'description': field.field_info.description or ''
            }
            if field.required:
                options["validators"].append(
                    wtforms.validators.Required()
                )
            else:
                options["validators"].append(
                    wtforms.validators.Optional()
                )
                if field.nullable:
                    # do something.
                    pass

            if name in overrides:
                options.update(overrides[name])
            wtfields[name] = wtf_type(**options)

        return wtfields


def model_fields(model, only=None, exclude=None) -> dict:
    if not bool(only) ^ bool(exclude):
        raise RuntimeError(
            'You need to specify either `only` or `exclude`')

    if only:
        return {
            name: field for name, field in model.__fields__.items()
            if name in only
        }

    return {
        name: field for name, field in model.__fields__.items()
        if name not in exclude
    }
