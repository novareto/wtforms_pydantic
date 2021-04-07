from typing import Optional, Iterable, Any, Literal, TypedDict
from enum import Enum, EnumMeta

import datetime
import decimal
import pydantic
import wtforms.fields
import wtforms.fields.html5
import wtforms.validators
from xml.sax.saxutils import escape
from wtforms_pydantic._fields import MultiCheckboxField


def _escape(data):
    return escape(data, entities={
        "'": "&apos;",
        "\"": "&quot;"
    })


def enum_choices(enum):

    def coerce(name):
        if isinstance(name, enum):
            # already coerced to instance of this enum
            return name
        try:
            return enum[name]
        except KeyError:
            raise ValueError(name)

    choices = [(v.name, _escape(v.value)) for v in enum]
    return choices, coerce


class FieldValidator:

    def __init__(self, field):
        self.field = field

    def __eq__(self, v):
        if isinstance(v, FieldValidator):
            return self.field is v.field
        return False

    def __call__(self, form, field):
        value, error = self.field.validate(
            field.data, form.data, loc=self.field.name)

        if error is not None:
            raise wtforms.validators.ValidationError(str(error.exc))


simple_converters = {
    str: wtforms.fields.StringField,
    int: wtforms.fields.IntegerField,
    float: wtforms.fields.FloatField,
    bool: wtforms.fields.BooleanField,
    Enum: wtforms.fields.SelectField,
    decimal.Decimal: wtforms.fields.DecimalField,
    datetime.date: wtforms.fields.html5.DateField,
    datetime.datetime: wtforms.fields.html5.DateTimeField,
    datetime.time: wtforms.fields.html5.TimeField,
    pydantic.SecretStr: wtforms.fields.PasswordField,
    pydantic.networks.EmailStr: wtforms.fields.html5.EmailField,
    Literal: wtforms.fields.SelectField,
}


multiple_converters = {
    Enum: MultiCheckboxField
}


def field_type_decomposer(type_):
    if pydantic.utils.lenient_issubclass(type_, Enum):
        return Enum, type_
    if pydantic.typing.is_literal_type(type_):
        values = pydantic.typing.all_literal_values(type_)
        choices = Enum('Choices', {value: value for value in values})
        return Enum, choices
    return type_, None


class Metadata(TypedDict):
    default: Any
    description: str
    label: str


class Field:
    type_: Any
    canon: Any
    multiple: bool
    metadata: Metadata
    required: bool
    validator: FieldValidator
    readonly: bool = False
    choices: Optional[EnumMeta] = None
    factory: Optional[wtforms.fields.Field] = None

    def __init__(self, field: pydantic.fields.ModelField):
        if field.is_complex() and issubclass(
                field.outer_type_.__origin__, Iterable):
            self.multiple = True
            self.type_ = field.sub_fields[0].type_
        else:
            self.multiple = False
            self.type_ = field.outer_type_

        self.validator = FieldValidator(field)
        self.canon, self.choices = field_type_decomposer(self.type_)
        self.required = field.required
        self.metadata = {
            'default': field.default or field.field_info.default_factory,
            'description': field.field_info.description or '',
            'label': field.field_info.title or field.name,
        }

    def compute_options(self):
        options = {}
        if self.required:
            options['validators'] = (
                wtforms.validators.DataRequired(), self.validator)
        else:
            options['validators'] = (
                wtforms.validators.Optional(), self.validator)
        if self.choices is not None:
            options['choices'], options['coerce'] = \
                enum_choices(self.choices)
        return {**self.metadata, **options}

    def cast(self):
        factory = self.factory
        if factory is None:
            if not self.multiple:
                factory = simple_converters.get(self.canon)
            else:
                factory = multiple_converters.get(self.canon)
            if factory is None:
                raise TypeError(
                    f'{self.type} cannot be converted to a WTForms field')

        options = self.compute_options()
        return factory, options

    def __call__(self):
        factory, options = self.cast()
        return factory(**options)
