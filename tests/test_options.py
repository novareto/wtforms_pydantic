"""Tests for `wtforms_pydantic` package.
"""

import hamcrest
import pytest
import pydantic
import wtforms.fields
import wtforms.validators
from wtforms_pydantic.converter import model_fields, Field, FieldValidator


def test_fields(person_model):
    assert model_fields(person_model) == {
        'age': Field.from_modelfield(
            person_model.__fields__['age']
        ),
        'identifier': Field.from_modelfield(
            person_model.__fields__['identifier']
        ),
        'name': Field.from_modelfield(
            person_model.__fields__['name']
        )
    }


def test_validators(person_model, dummy_field):
    age = Field.from_modelfield(person_model.__fields__['age'])
    options = age.compute_options()
    dummy_field.data = 17
    with pytest.raises(wtforms.validators.ValidationError) as exc:
        options['validators'][0]({}, dummy_field)
    assert str(exc.value) == 'must be over 18 years old.'


def test_no_validators(person_model, dummy_field):
    name = Field.from_modelfield(person_model.__fields__['name'])
    options = name.compute_options()
    dummy_field.data = 'Christian'
    options['validators'][0]({}, dummy_field)


def test_field_options(person_model):

    options = Field.from_modelfield(
        person_model.__fields__['name']).compute_options()
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

    field = Field.from_modelfield(person_model.__fields__['name'])
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

    field = Field.from_modelfield(person_model.__fields__['name'])
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

    field = Field.from_modelfield(person_model.__fields__['identifier'])
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


def test_complex_field_options(person_model):

    field = Field.from_modelfield(person_model.__fields__['age'])
    options = field.compute_options()
    hamcrest.assert_that(options, hamcrest.has_entries({
            'default': person_model.__fields__['age'].default_factory,
            'description': '',
            'filters': [],
            'validators': hamcrest.contains_exactly(
                hamcrest.instance_of(FieldValidator),
                hamcrest.instance_of(wtforms.validators.Optional)),
            'label': 'age'
        })
    )


def test_typing_rich_field_options(userinfo_model):

    field = Field.from_modelfield(userinfo_model.__fields__['email'])
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
