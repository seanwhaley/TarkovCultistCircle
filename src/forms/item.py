"""Item-related forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional

class ItemForm(FlaskForm):
    """Base item form."""
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[
        DataRequired(),
        NumberRange(min=0, message="Price must be positive")
    ])
    duration = IntegerField('Duration (hours)', validators=[Optional()])

class PriceOverrideForm(FlaskForm):
    """Form for overriding item prices."""
    price = DecimalField('Override Price', validators=[
        DataRequired(),
        NumberRange(min=0, message="Price must be positive")
    ])
    duration = IntegerField('Duration (hours)', validators=[
        Optional(),
        NumberRange(min=1, max=168, message="Duration must be between 1 and 168 hours")
    ])