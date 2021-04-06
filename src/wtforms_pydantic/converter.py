from dataclasses import dataclass, asdict
from typing import Optional, Iterable, Type, Any, Callable, Literal
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
            field.data, form, loc=self.field.name)
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


@dataclass
class FieldOptions:
    default: Any
    description: str
    label: str
    validators: list
    filters: list


@dataclass
class Field:
    canon: Any
    multiple: bool
    options: FieldOptions
    required: bool
    type_: Any
    choices: Optional[EnumMeta] = None
    field_factory: Optional[wtforms.fields.Field] = None

    @classmethod
    def get_canon(self, type_):
        if pydantic.utils.lenient_issubclass(type_, Enum):
            return type_, Enum, type_
        if pydantic.typing.is_literal_type(type_):
            values = pydantic.typing.all_literal_values(type_)
            choices = Enum('Choices', {value: value for value in values})
            return type_, Enum, choices
        return type_, type_, None

    @classmethod
    def from_modelfield(cls, field):
        options = FieldOptions(
            default=field.default or field.field_info.default_factory,
            description=field.field_info.description or '',
            label=field.field_info.title or field.name,
            validators=[FieldValidator(field)],
            filters=[]
        )

        if field.is_complex() and issubclass(
                field.outer_type_.__origin__, Iterable):
            multiple = True
            type_, canon, choices = cls.get_canon(
                field.sub_fields[0].type_)
        else:
            multiple = False
            type_, canon, choices = cls.get_canon(field.outer_type_)

        return cls(
            multiple=multiple,
            options=options,
            required=field.required,
            type_=type_,
            canon=canon,
            choices=choices,
        )

    def compute_options(self):
        options = asdict(self.options)
        if self.required:
            options["validators"].append(
                wtforms.validators.DataRequired()
            )
        else:
            options["validators"].append(
                wtforms.validators.Optional()
            )
        if self.choices is not None:
            options['choices'], options['coerce'] = \
                enum_choices(self.choices)
        return options

    def cast(self):
        factory = self.field_factory
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


def model_fields(model, include=None, exclude=None) -> dict:
    if not include:
        include = frozenset(model.__fields__.keys())
    if not exclude:
        exclude = set()

    return {
        name: Field.from_modelfield(field)
        for name, field in model.__fields__.items()
        if name in include and not name in exclude
    }
