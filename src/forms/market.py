"""Market-related forms."""
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField
from wtforms.validators import Optional, NumberRange

class MarketFilterForm(FlaskForm):
    """Form for filtering market data."""
    sort_by = SelectField('Sort By', choices=[
        ('price_asc', 'Price (Low to High)'),
        ('price_desc', 'Price (High to Low)'),
        ('name_asc', 'Name (A to Z)'),
        ('name_desc', 'Name (Z to A)'),
        ('last_updated', 'Last Updated')
    ])
    min_price = IntegerField('Minimum Price', validators=[
        Optional(),
        NumberRange(min=0, message="Minimum price must be positive")
    ])
    max_price = IntegerField('Maximum Price', validators=[
        Optional(),
        NumberRange(min=0, message="Maximum price must be positive")
    ])