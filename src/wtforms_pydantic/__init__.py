"""Top-level package for wtforms_pydantic."""

__author__ = """Christian Klinger"""
__email__ = 'ck@novareto.de'
__version__ = '0.1.0'


import pydantic
import wtforms.form
from functools import partial
from typing import Type, Iterable, Optional, Callable
from wtforms_components import read_only
from .converter import model_fields, Field


class Form(wtforms.form.BaseForm):
    model: Optional[Type[pydantic.BaseModel]] = None

    def __init__(self, *args, **kwargs):
        self.form_errors = []  # this exists in 3.0a1
        super().__init__(*args, **kwargs)

    @classmethod
    def from_fields(cls, fields: Iterable[Field]):
        fields = {name: field() for name, field in fields.items()}
        return cls(fields)

    @classmethod
    def from_model(cls, model: Type[pydantic.BaseModel]):
        form = cls.from_fields(model_fields(model))
        form.model = model
        return form

    def readonly(self, names):
        if names is ...:
            self._fields = {name: read_only(field)
                            for name, field in self._fields.items()}
        else:
            for key in names:
                self._fields[key] = read_only(self._fields[key])

    def validate(self):
        if not super().validate():
            return False

        if self.model is not None:
            data = self.data
            for validator in self.model.__pre_root_validators__:
                try:
                    new_values = validator(self.model, data)
                except (ValueError, TypeError, AssertionError) as exc:
                    self.form_errors.append(str(exc))

            for skip, validator in self.model.__post_root_validators__:
                try:
                    new_values = validator(self.model, data)
                except (ValueError, TypeError, AssertionError) as exc:
                    self.form_errors.append(str(exc))

            return bool(self.form_errors)
        return True
