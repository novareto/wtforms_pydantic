"""Top-level package for wtforms_pydantic."""

__author__ = """Christian Klinger"""
__email__ = 'ck@novareto.de'
__version__ = '0.1.0'


import pydantic
import wtforms.form
from typing import Type, Iterable, Optional
from wtforms_pydantic.field import Field


def model_fields(model, include=None, exclude=None) -> dict:
    if not include:
        include = frozenset(model.__fields__.keys())
    if not exclude:
        exclude = set()

    return {
        name: Field(field) for name, field in model.__fields__.items()
        if name in include and name not in exclude
    }


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
    def from_model(cls, model: Type[pydantic.BaseModel], **kwargs):
        form = cls.from_fields(model_fields(model, **kwargs))
        form.model = model
        return form

    def validate(self):
        if not super().validate():
            return False

        if self.model is not None:
            data = self.data
            for validator in self.model.__pre_root_validators__:
                try:
                    validator(self.model, data)
                except (ValueError, TypeError, AssertionError) as exc:
                    self.form_errors.append(str(exc))

            for skip, validator in self.model.__post_root_validators__:
                try:
                    validator(self.model, data)
                except (ValueError, TypeError, AssertionError) as exc:
                    self.form_errors.append(str(exc))

            return not len(self.form_errors)
        return True
