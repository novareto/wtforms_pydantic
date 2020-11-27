#!/usr/bin/env python

"""Tests for `wtforms_pydantic` package."""

import pytest
import wtforms.validators
import typing
from wtforms_pydantic.converter import model_fields, Converter
from pydantic import BaseModel, Field


def factory():
    return 18


class Person(BaseModel):
    identifier: str
    name: str = "Klaus"
    age: int = Field(default_factory=factory)


class Group(BaseModel):
    members: typing.Optional[typing.List]


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

    options = Converter.field_options(Person.__fields__['name'])
    validators = options.pop('validators')
    assert options == {
        'default': 'Klaus',
        'description': '',
        'filters': [],
        'label': 'name'
        }
    assert len(validators) == 1
    assert validators[0].__class__ == wtforms.validators.Optional

    options = Converter.field_options(
        Person.__fields__['name'], required=True)
    validators = options.pop('validators')
    assert options == {
        'default': 'Klaus',
        'description': '',
        'filters': [],
        'label': 'name'
        }
    assert len(validators) == 1
    assert validators[0].__class__ == wtforms.validators.DataRequired

    options = Converter.field_options(
        Person.__fields__['name'], label="This is a name")
    validators = options.pop('validators')
    assert options == {
        'default': 'Klaus',
        'description': '',
        'filters': [],
        'label': 'This is a name'
        }

    options = Converter.field_options(Person.__fields__['identifier'])
    validators = options.pop('validators')
    assert options == {
        'default': None,
        'description': '',
        'filters': [],
        'label': 'identifier'
        }
    assert len(validators) == 1
    assert validators[0].__class__ == wtforms.validators.DataRequired


def test_complex_field_options():

    options = Converter.field_options(Person.__fields__['age'])
    validators = options.pop('validators')
    assert options == {
        'default': factory,
        'description': '',
        'filters': [],
        'label': 'age'
        }
    assert len(validators) == 1
    assert validators[0].__class__ == wtforms.validators.Optional


def test_typing_rich_field_options():

    options = Converter.field_options(Group.__fields__['members'])
    validators = options.pop('validators')
    assert options == {
        'default': None,
        'description': '',
        'filters': [],
        'label': 'members'
        }
    assert len(validators) == 1
    assert validators[0].__class__ == wtforms.validators.Optional
