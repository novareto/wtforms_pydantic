import enum
import datetime
import decimal
import pydantic
import wtforms.fields
import wtforms.fields.html5
import wtforms.validators
from xml.sax.saxutils import escape


class Field:

    def __init__(self, wtforms_field):
        self.wtforms_field = wtforms_field

    @staticmethod
    def field_options(field, **override):
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

    def __call__(self, field, **override):
        options = self.field_options(field, **override)
        return self.wtforms_field(**options)


class EnumField(Field):

    @staticmethod
    def _escape(data):
        return escape(data, entities={
            "'": "&apos;",
            "\"": "&quot;"
        })

    def __call__(self, field, **override):

        enum = field.outer_type_

        def coerce(name):
            if isinstance(name, enum):
                # already coerced to instance of this enum
                return name
            try:
                return enum[name]
            except KeyError:
                raise ValueError(name)

        options = self.field_options(field, **override)
        options['choices'] = [(v.value, self._escape(v.value)) for v in enum]
        options['coerce'] = coerce
        return self.wtforms_field(**options)


class Converter:
    """convert pydantic fields into wtforms fields.
    """

    class_converters = {
        str: Field(wtforms.fields.StringField),
        int: Field(wtforms.fields.IntegerField),
        float: Field(wtforms.fields.FloatField),
        decimal.Decimal: Field(wtforms.fields.DecimalField),
        datetime.date: Field(wtforms.fields.html5.DateField),
        datetime.datetime: Field(wtforms.fields.html5.DateTimeField),
        datetime.time: Field(wtforms.fields.html5.TimeField),
        pydantic.SecretStr: Field(wtforms.fields.PasswordField),
        pydantic.networks.EmailStr: Field(wtforms.fields.html5.EmailField),
    }

    type_converters = {
        enum.EnumMeta: EnumField(wtforms.fields.SelectField)
    }

    @classmethod
    def convert(cls, fields: dict, **overrides):
        wtfields = {}
        for name, field in fields.items():
            if wtf_field := cls.class_converters.get(field.outer_type_):
                wtfields[name] = wtf_field(field, **overrides.get(name, {}))
            elif wtf_field := cls.type_converters.get(
                    type(field.outer_type_)):
                wtfields[name] = wtf_field(field, **overrides.get(name, {}))
            else:
                raise TypeError(
                    f'{field} cannot be converted to a WTForms field')
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
