"""Top-level package for wtforms_pydantic."""

__author__ = """Christian Klinger"""
__email__ = 'ck@novareto.de'
__version__ = '0.1.0'


import pydantic
import wtforms.form
from .converter import Converter, model_fields
from wtforms_components import read_only


class Form(wtforms.form.BaseForm):

    _readonly: bool = False

    @classmethod
    def from_model(cls, model: pydantic.BaseModel,
                   only=(), exclude=(), **overrides):
        return cls(Converter.convert(
            model_fields(model, only=only, exclude=exclude), **overrides
        ))

    def readonly(self):
        if self._readonly:
            return
        for key, field in self._fields.items():
            self._fields[key] = read_only(field)
        self._readonly = True
