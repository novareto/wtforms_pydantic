import pytest
import pydantic
import typing


class DummyField:
    data = None


class DummyForm:
    data = None


def factory():
    return 18


class Person(pydantic.BaseModel):
    identifier: str
    name: str = "Klaus"
    age: int = pydantic.Field(default_factory=factory)

    @pydantic.validator('age')
    def must_be_adult(cls, v):
        if v < 18:
            raise ValueError('must be over 18 years old.')
        return v

    @pydantic.validator('identifier')
    def must_have_valid_id(cls, v, values, **kwargs):
        if 'name' in values and values['name'].lower() not in v:
            raise ValueError(
                'The identifier must contain the name in lowercase.')
        return v

    @pydantic.root_validator
    def check_identifier_for_admin(cls, values):
        if values['identifier'] == 'admin':
            if (name := values.get('age')) < 21:
                raise ValueError('You must be over 21 to be an admin.')
        return values


class UserInfo(pydantic.BaseModel):
    email: typing.Optional[str]


@pytest.fixture
def dummy_field():
    return DummyField()


@pytest.fixture
def dummy_form():
    return DummyForm()


@pytest.fixture
def person_model():
    return Person


@pytest.fixture
def userinfo_model():
    return UserInfo
