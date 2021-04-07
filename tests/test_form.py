"""Tests for `wtforms_pydantic` package.
"""

from wtforms_pydantic import Form


def test_fields(person_model):
    form = Form.from_model(person_model)
    assert form.model is person_model
    form.process(data={'age': 18, 'identifier': 'admin'})
    form.validate()
    assert form.errors == {
        'identifier': ['The identifier must contain the name in lowercase.']
    }
    assert form.form_errors == []

    form.process(data={'age': 18, 'identifier': 'admin', 'name': 'Admin'})
    form.validate()
    assert form.errors == {}
    assert form.form_errors == ['You must be over 21 to be an admin.']
