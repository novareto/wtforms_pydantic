"""Tests for `wtforms_pydantic` package.
"""

import hamcrest
import pytest
import pydantic
import typing
import wtforms.fields
import wtforms.validators
from wtforms_pydantic.converter import model_fields, FormField, FieldValidator


class DummyField:
    data = None

    def __init__(self, value):
        self.data = value


def factory():
    return 18


class Person(pydantic.BaseModel):
    identifier: str
    name: str = "Klaus"
    age: int = pydantic.Field(default_factory=factory)

    @pydantic.validator('age')
    def must_be_adult(cls, v):
        if v < 18:
            raise ValueError('must be over 18 years old.')
        return v


class UserInfo(pydantic.BaseModel):
    email: typing.Optional[str]


def test_fields():
    assert model_fields(Person) == {
        'age': FormField.from_modelfield(
            Person.__fields__['age']
        ),
        'identifier': FormField.from_modelfield(
            Person.__fields__['identifier']
        ),
        'name': FormField.from_modelfield(
            Person.__fields__['name']
        )
    }


def test_validators():
    age = FormField.from_modelfield(Person.__fields__['age'])
    options = age.compute_options()
    with pytest.raises(wtforms.validators.ValidationError) as exc:
        options['validators'][0]({}, DummyField(17))
    assert str(exc.value) == 'must be over 18 years old.'


def test_field_options():

    options = FormField.from_modelfield(
        Person.__fields__['name']).compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(FieldValidator),
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'name'
        })
    )

    field = FormField.from_modelfield(Person.__fields__['name'])
    field.required = True
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(FieldValidator),
                hamcrest.instance_of(wtforms.validators.DataRequired)),
            'label': 'name'
        })
    )

    field = FormField.from_modelfield(Person.__fields__['name'])
    field.options.label = "This is a name"
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(FieldValidator),
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'This is a name'
        })
    )

    field = FormField.from_modelfield(Person.__fields__['identifier'])
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': None,
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(FieldValidator),
                hamcrest.instance_of(wtforms.validators.DataRequired)),
            'label': 'identifier'
        })
    )


def test_complex_field_options():

    field = FormField.from_modelfield(Person.__fields__['age'])
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': factory,
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(FieldValidator),
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'age'
        })
    )


def test_typing_rich_field_options():

    field = FormField.from_modelfield(UserInfo.__fields__['email'])
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': None,
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(FieldValidator),
                hamcrest.instance_of(wtforms.validators.Optional)
            ),
            'label': 'email'
        })
    )
