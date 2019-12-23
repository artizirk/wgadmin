from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class InterfaceSearchForm(FlaskForm):
    class Meta:
        csrf = False
    query = StringField("Search")
