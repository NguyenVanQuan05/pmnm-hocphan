from datetime import date

from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectField, StringField, SubmitField,
                     TextAreaField, ValidationError)
from wtforms.validators import (DataRequired, InputRequired, Length,
                                NumberRange, Optional)

from models import Category, db

CURRENT_YEAR = date.today().year


class CategoryForm(FlaskForm):
    name = StringField("Tên danh mục", validators=[
        DataRequired(message="Vui lòng nhập tên danh mục."),
        Length(max=100, message="Tên danh mục tối đa 100 ký tự."),
    ])
    description = TextAreaField("Mô tả")
    submit = SubmitField("Lưu")

    editing_id = None

    def validate_name(self, field):
        name = field.data.strip()
        existing = db.session.scalar(db.select(Category).filter_by(name=name))
        if existing is not None and existing.id != self.editing_id:
            raise ValidationError("Tên danh mục đã tồn tại.")


class BookForm(FlaskForm):
    title = StringField("Tên sách", validators=[
        DataRequired(message="Vui lòng nhập tên sách."),
        Length(max=200, message="Tên sách tối đa 200 ký tự."),
    ])
    author = StringField("Tác giả", validators=[
        DataRequired(message="Vui lòng nhập tên tác giả."),
        Length(max=100, message="Tên tác giả tối đa 100 ký tự."),
    ])
    year = IntegerField("Năm xuất bản", validators=[
        Optional(),
        NumberRange(min=1000, max=CURRENT_YEAR,
                    message=f"Năm xuất bản phải từ 1000 đến {CURRENT_YEAR}."),
    ], invalid_value_message="Năm xuất bản phải là số nguyên.")
    quantity = IntegerField("Số lượng", default=1, validators=[
        InputRequired(message="Vui lòng nhập số lượng."),
        NumberRange(min=0, message="Số lượng không được âm."),
    ], invalid_value_message="Số lượng phải là số nguyên.")
    category_id = SelectField("Danh mục", coerce=int, validators=[
        DataRequired(message="Vui lòng chọn danh mục."),
    ], invalid_value_message="Danh mục không hợp lệ.",
       invalid_choice_message="Danh mục không tồn tại.")
    description = TextAreaField("Mô tả")
    submit = SubmitField("Lưu")


class DeleteForm(FlaskForm):
    pass
