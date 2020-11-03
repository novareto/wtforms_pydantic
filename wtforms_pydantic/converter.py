from pydantic import BaseModel
from wtforms import validators
from wtforms.fields.core import DecimalField, FloatField, IntegerField, StringField
from wtforms.fields.html5 import DateField, DateTimeField, TimeField
from wtforms.fields.simple import TextAreaField
from collections import OrderedDict, namedtuple
import datetime
import decimal

FieldInfo = namedtuple('FieldInfo', ('name', 'field'))


default_converters = OrderedDict((
    #   Standard types
    (str, StringField),
    (int, IntegerField),
    (float, FloatField),
    (decimal.Decimal, DecimalField),
    #   Dates, times
    (datetime.date, DateField  # WPDateField
     ),
    (datetime.datetime, DateTimeField  # WPDateTimeField
     ),
    (datetime.time, TimeField  # WPTimeField
     )
)
)


class ModelConverter(object):
    """convert entity attribute to Wtf-Field
    """
    def __init__(self, additional=None, additional_coerce=None, overrides=None):
        self.converters = {}

        if additional:
            self.converters.update(additional)

        #self.coerce_settings = dict( coerce_defaults )
        #if additional_coerce:
        #    self.coerce_settings.update(additional_coerce)
        self.overrides = overrides or {}


    def build_kwargs(self, entity, attr, field_args):
        field_args = field_args or {}
        kwargs = {
            'label': attr.name,
            'validators': [],
            'filters': [],
            'default': attr.default,
            #'description': attr.help_text
        }
        if field_args:
            kwargs.update(field_args)
        #  {"validators": [Email], "only_validators": True }
        if not kwargs.pop("only_validators", False):
            self.set_required_validator(attr, kwargs)
            self.set_unique_validator(entity, attr , kwargs)
        self.add_null_filter(attr, kwargs)
        return kwargs

    def set_required_validator(self,  attr, kwargs):
        if attr.required:
            kwargs['validators'].append(validators.Required())
        else :
            kwargs['validators'].append(validators.Optional())
            # further 
            if attr.default is not None:
                kwargs['validators'].append(validators.Optional())
            else:
                kwargs['validators'].append(ValueRequired())

    def set_unique_validator(self, entity, attr, kwargs):
        return
        if attr.is_unique :
            kwargs['validators'].append(UniqueValidator(entity, attr.name))

    def add_null_filter(self, attr, kwargs):
        return
        if not attr.is_required and attr.nullable:
            # Treat empty string as None when converting.
            kwargs['filters'].append(handle_null_filter)

    def get_custom(self, entity, attr, kwargs):
        if attr.name in self.overrides:
            self.is_filter_allowed(self.overrides[attr.name], kwargs)
            return FieldInfo(attr.name, self.overrides[attr.name](**kwargs))


    def convert(self, entity: BaseModel, attr, field_args):
        kwargs = self.build_kwargs( entity, attr ,field_args)
        custom = self.get_custom(entity, attr, kwargs)
        if custom:
            return custom
        # converter : { attr_type: fieldInfo }

        for converter in self.converters:
            if isinstance(attr, converter):
                #self.is_filter_allowed( self.converters[converter], kwargs)
                return self.converters[converter](entity, attr, **kwargs)
        try: 
            converter = default_converters[attr.type_]
        except Exception:
            raise AttributeError("There is not possible conversion for '%s' " % type(attr.type_))

        #self.is_filter_allowed( converter, kwargs)
        return FieldInfo(attr.name, converter(**kwargs))
