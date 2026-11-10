# Đã hiểu và chỉnh sửa – Nguyễn Văn Quân
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length

from models import Category, db


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


class DeleteForm(FlaskForm):
    # Form rỗng, chỉ để sinh CSRF token cho nút Xoá
    pass
