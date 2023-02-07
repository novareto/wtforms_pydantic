"""Tests for `wtforms_pydantic` package.
"""

import enum
import datetime
import pytest
import typing
import pydantic
import wtforms.fields
import wtforms.validators
from wtforms_pydantic.field import Field
from wtforms_pydantic._fields import MultiCheckboxField


def test_int_casting():

    class Model(pydantic.BaseModel):
        field: int

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.IntegerField


def test_str_casting():

    class Model(pydantic.BaseModel):
        field: str

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.StringField


def test_float_casting():

    class Model(pydantic.BaseModel):
        field: float

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.FloatField


def test_bool_casting():

    class Model(pydantic.BaseModel):
        field: bool

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.BooleanField


def test_date_casting():

    class Model(pydantic.BaseModel):
        field: datetime.date

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.DateField


def test_datetime_casting():

    class Model(pydantic.BaseModel):
        field: datetime.datetime

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.DateTimeField


def test_time_casting():

    class Model(pydantic.BaseModel):
        field: datetime.time

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.TimeField


def test_password_casting():

    class Model(pydantic.BaseModel):
        field: pydantic.SecretStr

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.PasswordField


def test_email_casting():

    class Model(pydantic.BaseModel):
        field: pydantic.networks.EmailStr

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.EmailField


def test_enum_casting():

    class MyChoices(enum.Enum):
        foo = 'Foo'
        bar = 'Bar'

    class Model(pydantic.BaseModel):
        field: MyChoices

    field = Field(Model.__fields__['field'])
    factory, options = field.cast()
    assert factory == wtforms.fields.SelectField
    assert options['choices'] == [('foo', 'Foo'), ('bar', 'Bar')]
    assert options['coerce']('foo')
    with pytest.raises(ValueError):
        assert options['coerce']('test')


def test_multiple_enum_casting():

    class MyChoices(enum.Enum):
        foo = 'Foo'
        bar = 'Bar'

    class Model(pydantic.BaseModel):
        field1: typing.List[MyChoices]
        field2: typing.Set[MyChoices]
        field3: typing.Tuple[MyChoices]

    for fname in ('field1', 'field2', 'field3'):
        field = Field(Model.__fields__[fname])
        factory, options = field.cast()
        assert factory == MultiCheckboxField
        assert options['choices'] == [('foo', 'Foo'), ('bar', 'Bar')]
        assert options['coerce']('foo')
        with pytest.raises(ValueError):
            assert options['coerce']('test')


def test_literal_casting():

    class Model(pydantic.BaseModel):
        unique: typing.Literal['singleton']
        multiple: typing.Literal['complex', 'complicated']

    field = Field(Model.__fields__['unique'])
    factory, options = field.cast()
    assert factory == wtforms.fields.SelectField
    assert options['choices'] == [('singleton', 'singleton')]
    assert options['coerce']('singleton')
    with pytest.raises(ValueError):
        assert options['coerce']('other value')

    field = Field(Model.__fields__['multiple'])
    factory, options = field.cast()
    assert factory == wtforms.fields.SelectField
    assert options['choices'] == [
        ('complex', 'complex'), ('complicated', 'complicated')]
    assert options['coerce']('complex')
    with pytest.raises(ValueError):
        assert options['coerce']('other value')


def test_multiple_literal_casting():

    class Model(pydantic.BaseModel):
        multiple: typing.List[typing.Literal['complex', 'complicated']]

    field = Field(Model.__fields__['multiple'])
    factory, options = field.cast()
    assert factory == MultiCheckboxField
    assert options['choices'] == [
        ('complex', 'complex'), ('complicated', 'complicated')]
    assert options['coerce']('complex')
    with pytest.raises(ValueError):
        assert options['coerce']('other value')
