import pytest
import pydantic
import typing


class DummyField:
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


class UserInfo(pydantic.BaseModel):
    email: typing.Optional[str]


@pytest.fixture
def dummy_field():
    return DummyField()


@pytest.fixture
def person_model():
    return Person


@pytest.fixture
def userinfo_model():
    return UserInfo
