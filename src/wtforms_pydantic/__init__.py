"""Top-level package for wtforms_pydantic."""

__author__ = """Christian Klinger"""
__email__ = 'ck@novareto.de'
__version__ = '0.1.0'


import pydantic
import wtforms.form
from typing import Iterable
from wtforms_components import read_only
from .converter import model_fields, Field


class Form(wtforms.form.BaseForm):

    @classmethod
    def from_fields(cls, fields: Iterable[Field]):
        fields = {name: field() for name, field in fields.items()}
        return cls(fields)

    @classmethod
    def from_model(cls, model: pydantic.BaseModel, **kwargs):
        return cls.from_fields(model_fields(model, **kwargs))

    def readonly(self, names):
        if names is ...:
            self._fields = {name: read_only(field)
                            for name, field in self._fields.items()}
        else:
            for key in names:
                self._fields[key] = read_only(self._fields[key])
