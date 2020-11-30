"""Tests for `wtforms_pydantic` package.
"""

import hamcrest
import pytest
import pydantic
import typing
import wtforms.fields
import wtforms.validators
from wtforms_pydantic.converter import model_fields
from wtforms_pydantic.converter import Converter, Field, EnumField


def factory():
    return 18


class Person(pydantic.BaseModel):
    identifier: str
    name: str = "Klaus"
    age: int = pydantic.Field(default_factory=factory)


class UserInfo(pydantic.BaseModel):
    email: typing.Optional[str]


def test_fields():
    assert model_fields(Person) == {
        'age': Person.__fields__['age'],
        'identifier': Person.__fields__['identifier'],
        'name': Person.__fields__['name']
    }

    assert model_fields(Person, only=('age')) == {
        'age': Person.__fields__['age']
    }

    assert model_fields(Person, exclude=('name')) == {
        'age': Person.__fields__['age'],
        'identifier': Person.__fields__['identifier'],
    }

    assert model_fields(Person, exclude=('test')) == {
        'age': Person.__fields__['age'],
        'identifier': Person.__fields__['identifier'],
        'name': Person.__fields__['name']
    }

    assert model_fields(Person, only=('test')) == {
    }

    with pytest.raises(AssertionError):
        model_fields(Person, only=('test'), exclude=('test'))


def test_field_options():

    options = Field.field_options(Person.__fields__['name'])
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'name'
        })
    )

    options = Field.field_options(
        Person.__fields__['name'], required=True)
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.DataRequired)),
            'label': 'name'
        })
    )

    options = Field.field_options(
        Person.__fields__['name'], label="This is a name")
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'This is a name'
        })
    )

    options = Field.field_options(Person.__fields__['identifier'])
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': None,
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.DataRequired)),
            'label': 'identifier'
        })
    )


def test_complex_field_options():

    options = Field.field_options(Person.__fields__['age'])
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': factory,
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'age'
        })
    )


def test_typing_rich_field_options():

    options = Field.field_options(UserInfo.__fields__['email'])
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': None,
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'email'
        })
    )
