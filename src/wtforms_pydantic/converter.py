from dataclasses import dataclass, asdict
from typing import Optional, Sequence, Type, Any, Callable, Literal
from enum import EnumMeta

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

    choices = [(v.value, _escape(v.value)) for v in enum]
    return choices, coerce


needs_choices = {
    EnumMeta: enum_choices,
    Literal: None  # implement me
}

simple_converters = {
    str: wtforms.fields.StringField,
    int: wtforms.fields.IntegerField,
    float: wtforms.fields.FloatField,
    bool: wtforms.fields.BooleanField,
    EnumMeta: wtforms.fields.SelectField,
    decimal.Decimal: wtforms.fields.DecimalField,
    datetime.date: wtforms.fields.html5.DateField,
    datetime.datetime: wtforms.fields.html5.DateTimeField,
    datetime.time: wtforms.fields.html5.TimeField,
    pydantic.SecretStr: wtforms.fields.PasswordField,
    pydantic.networks.EmailStr: wtforms.fields.html5.EmailField,
}

multiple_converters = {
    EnumMeta: MultiCheckboxField
}


@dataclass
class FieldOptions:
    label: str
    description: str
    default: Any
    validators: list


@dataclass
class FieldRepresentation:
    type: Any
    multiple: bool
    options: FieldOptions
    required: bool
    field_factory: wtforms.fields.Field = None
    choices_factory: Callable = None

    def matching_key(self):
        if type(self.type) is EnumMeta:
            return EnumMeta
        return self.type

    @classmethod
    def from_modelfield(cls, field, validators=None):
        options = FieldOptions(
            default=field.default or field.field_info.default_factory,
            description=field.field_info.description or '',
            label=field.field_info.title or field.name,
            validators=validators or []
        )
        if field.is_complex():
            if issubclass(field.outer_type_.__origin__, Sequence):
                return cls(
                    multiple=True,
                    type=field.type_,
                    required=field.required,
                    options=options
                )
        return cls(
            multiple=False,
            type=field.outer_type_,
            required=field.required,
            options=options
        )

    def wtforms_cast(self):
        key = self.matching_key()
        options = asdict(self.options)
        if self.required:
            options["validators"].append(
                wtforms.validators.DataRequired()
            )
        else:
            options["validators"].append(
                wtforms.validators.Optional()
            )
        if (choice_maker := needs_choices.get(key)) is not None:
            options['choices'], options['coerce'] = choice_maker(self.type)

        factory = self.field_factory
        if factory is None:
            if not self.multiple:
                factory = simple_converters.get(key)
            else:
                factory = multiple_converters.get(key)
            if factory is None:
                raise TypeError(
                    f'{self.type} cannot be converted to a WTForms field')

        return factory(**options)


def model_fields(model, include=None, exclude=None) -> dict:
    if not include:
        include = frozenset(model.__fields__.keys())
    if not exclude:
        exclude = set()

    return {
        name: FieldRepresentation.from_modelfield(
            field, validators=model.__validators__.get('name')
        )
        for name, field in model.__fields__.items()
        if name in include and not name in exclude
    }
