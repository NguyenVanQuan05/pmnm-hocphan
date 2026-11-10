# Có tham khảo AI (Claude Code), đã hiểu và chỉnh sửa – Nguyễn Văn Quân
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectField, StringField, SubmitField,
                     TextAreaField, ValidationError)
from wtforms.validators import (DataRequired, InputRequired, Length,
                                NumberRange, Optional)

from models import Category, db

# Năm hiện tại, tính một lần khi chạy server
CURRENT_YEAR = date.today().year


class CategoryForm(FlaskForm):
    name = StringField("Tên danh mục", validators=[
        DataRequired(message="Vui lòng nhập tên danh mục."),
        Length(max=100, message="Tên danh mục tối đa 100 ký tự."),
    ])
    description = TextAreaField("Mô tả")
    submit = SubmitField("Lưu")

    # id của danh mục đang sửa; None khi thêm mới (view sẽ gán khi sửa)
    editing_id = None

    def validate_name(self, field):
        name = field.data.strip()
        existing = db.session.scalar(db.select(Category).filter_by(name=name))
        # Trùng với danh mục KHÁC thì báo lỗi; trùng với chính nó (đang sửa) thì bỏ qua
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
    # Optional: để trống thì bỏ qua các kiểm tra phía sau
    year = IntegerField("Năm xuất bản", validators=[
        Optional(),
        NumberRange(min=1000, max=CURRENT_YEAR,
                    message=f"Năm xuất bản phải từ 1000 đến {CURRENT_YEAR}."),
    ], invalid_value_message="Năm xuất bản phải là số nguyên.")
    # InputRequired (không dùng DataRequired) vì số 0 vẫn là giá trị hợp lệ
    quantity = IntegerField("Số lượng", default=1, validators=[
        InputRequired(message="Vui lòng nhập số lượng."),
        NumberRange(min=0, message="Số lượng không được âm."),
    ], invalid_value_message="Số lượng phải là số nguyên.")
    # choices được nạp từ CSDL trong view; coerce=int đổi "3" thành 3
    category_id = SelectField("Danh mục", coerce=int, validators=[
        DataRequired(message="Vui lòng chọn danh mục."),
    ], invalid_value_message="Danh mục không hợp lệ.",
       invalid_choice_message="Danh mục không tồn tại.")
    description = TextAreaField("Mô tả")
    submit = SubmitField("Lưu")


class DeleteForm(FlaskForm):
    # Form rỗng, chỉ để sinh CSRF token cho nút Xoá
    pass
