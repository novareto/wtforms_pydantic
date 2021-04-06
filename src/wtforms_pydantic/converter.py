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
    default: Any
    description: str
    label: str
    validators: list
    filters: list


@dataclass
class FormField:
    canon: Any
    multiple: bool
    options: FieldOptions
    required: bool
    type: Any
    field_factory: wtforms.fields.Field = None

    @classmethod
    def from_modelfield(cls, field):
        options = FieldOptions(
            default=field.default or field.field_info.default_factory,
            description=field.field_info.description or '',
            label=field.field_info.title or field.name,
            validators=[FieldValidator(field)],
            filters=[]
        )
        if field.is_complex():
            if issubclass(field.outer_type_.__origin__, Sequence):
                return cls(
                    multiple=True,
                    options=options,
                    required=field.required,
                    type=field.type_,
                    canon=(
                        EnumMeta if type(field.type_) is EnumMeta
                        else field.type_
                    )
                )
        return cls(
            multiple=False,
            options=options,
            required=field.required,
            type=field.outer_type_,
            canon=(
                EnumMeta if type(field.outer_type_) is EnumMeta
                else field.outer_type_
            )
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
        if (choice_maker := needs_choices.get(self.canon)) is not None:
            options['choices'], options['coerce'] = choice_maker(self.type)
        return options

    def wtforms_cast(self):
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
        return factory(**options)


def model_fields(model, include=None, exclude=None) -> dict:
    if not include:
        include = frozenset(model.__fields__.keys())
    if not exclude:
        exclude = set()

    return {
        name: FormField.from_modelfield(field)
        for name, field in model.__fields__.items()
        if name in include and not name in exclude
    }
