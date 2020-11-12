from wtforms.fields.simple import SubmitField
from .converter import ModelConverter
from wtforms.form import BaseForm
from pydantic import BaseModel


def model_fields(
    entity: BaseModel, only=None, exclude=None, field_args=None, converter=None
):
    converter = converter or ModelConverter()
    field_args = field_args or {}
    attrs = entity.__fields__.values()
    # attrs = entity.fields.values()

    if only:
        attrs = [x for x in attrs if x.name in only]
    elif exclude:
        attrs = [x for x in attrs if x.name not in exclude]
    field_dict = {}
    for attr in attrs:
        name, field = converter.convert(entity, attr, field_args.get(attr.name))
        field_dict[name] = field

    return field_dict


def model_form(
    entity: BaseModel,
    base_class=BaseForm,
    only=None,
    exclude=None,
    field_args=None,
    converter=None,
    submit_kwargs={},
):
    field_dict = model_fields(
        entity, only=only, exclude=exclude, field_args=field_args, converter=converter
    )
    if submit_kwargs.pop("submit", False):
        name = submit_kwargs.get("name", "Submit")
        field_dict[name] = SubmitField(**submit_kwargs)
    return type(entity.__name__ + "Form", (base_class,), field_dict)
