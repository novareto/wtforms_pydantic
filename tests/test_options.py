"""Tests for `wtforms_pydantic` package.
"""

import hamcrest
import pytest
import wtforms.fields
import wtforms.validators
from wtforms_pydantic import model_fields
from wtforms_pydantic.field import Field, FieldValidator


class Form:

    def __init__(self, data=None):
        self.data = data is not None and data or {}


def test_fields(person_model):
    hamcrest.assert_that(
        model_fields(person_model), hamcrest.has_entries({
            'age': person_model.__fields__['age'],
            'identifier': person_model.__fields__['identifier'],
            'name': person_model.__fields__['name']
        })
    )


def test_validators(person_model, dummy_field):
    age = Field(person_model.__fields__['age'])
    options = age.compute_options()
    dummy_field.data = 17
    with pytest.raises(wtforms.validators.ValidationError) as exc:
        for validator in options['validators']:
            validator(Form(), dummy_field)
    assert str(exc.value) == 'must be over 18 years old.'


def test_cross_validation(person_model, dummy_field):
    identifier = Field(
        person_model.__fields__['identifier'])
    options = identifier.compute_options()
    dummy_field.data = 'klaus_kinski'

    for validator in options['validators']:
        validator(Form({'name': 'Klaus'}), dummy_field)

    with pytest.raises(wtforms.validators.ValidationError) as exc:
        for validator in options['validators']:
            validator(Form({'name': 'Christian'}), dummy_field)

    assert str(exc.value) == (
        'The identifier must contain the name in lowercase.')


def test_no_validators(person_model, dummy_field):
    name = Field(person_model.__fields__['name'])
    options = name.compute_options()
    dummy_field.data = 'Christian'
    options['validators'][0](Form(), dummy_field)


def test_field_options(person_model):

    options = Field(
        person_model.__fields__['name']).compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional),
                hamcrest.instance_of(FieldValidator)
            ),
            'label': 'name'
        })
    )

    field = Field(person_model.__fields__['name'])
    field.required = True
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.DataRequired),
                hamcrest.instance_of(FieldValidator)
            ),
            'label': 'name'
        })
    )

    field = Field(person_model.__fields__['name'])
    field.metadata['label'] = "This is a name"
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': 'Klaus',
            'description': '',
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional),
                hamcrest.instance_of(FieldValidator),
            ),
            'label': 'This is a name'
        })
    )

    field = Field(person_model.__fields__['identifier'])
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': None,
            'description': '',
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.DataRequired),
                hamcrest.instance_of(FieldValidator)
            ),
            'label': 'identifier'
        })
    )


def test_complex_field_options(person_model):

    field = Field(person_model.__fields__['age'])
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': person_model.__fields__['age'].default_factory,
            'description': '',
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional),
                hamcrest.instance_of(FieldValidator)
            ),
            'label': 'age'
        })
    )


def test_typing_rich_field_options(userinfo_model):

    field = Field(userinfo_model.__fields__['email'])
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': None,
            'description': '',
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(wtforms.validators.Optional),
                hamcrest.instance_of(FieldValidator)
            ),
            'label': 'email'
        })
    )
