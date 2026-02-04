from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms.widgets import HiddenInput
from wtforms.widgets.core import Input


class NumberInput(Input):
    input_type = "number"


class MyIntegerField(IntegerField):
    widget = NumberInput()


class StarRatingField(IntegerField):
    widget = HiddenInput()


class AddCartForm(FlaskForm):
    variant = RadioField("variant", validators=[DataRequired()], coerce=int)
    quantity = MyIntegerField(
        "quantity",
        validators=[DataRequired(), NumberRange(min=1)],
        default=1,
        render_kw={"min": "1"},
    )

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        if product:
            self.variant.choices = [(vari.id, vari) for vari in product.variant]

# Add customer feedback feature
# @author: Nebil Müren - cas3322
class ProductFeedbackForm(FlaskForm):
    nickname = StringField(
        "Nickname",
        validators=[DataRequired(), Length(max=64)],
        render_kw={"placeholder": "Your public nickname"},
    )
    packaging_rating = StarRatingField(
        "Packaging",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        default=5,
    )
    delivery_rating = StarRatingField(
        "Delivery",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        default=5,
    )
    item_rating = StarRatingField(
        "Item quality",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        default=5,
    )
    comment = TextAreaField(
        "Comments",
        validators=[Length(max=1024)],
        render_kw={"placeholder": "Share any additional context (optional)", "rows": 3},
    )
