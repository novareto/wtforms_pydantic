#!/usr/bin/env python

"""Tests for `wtforms_pydantic` package."""

import pytest


from wtforms_pydantic import wtforms_pydantic
from pydantic import BaseModel


def test_base():
    class Person(BaseModel):
        name: str = "Klaus"
        age: int = 0

    ff = wtforms_pydantic.model_fields(Person())
    assert(ff == None)
