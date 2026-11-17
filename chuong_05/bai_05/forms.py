from flask_wtf import FlaskForm
from wtforms import (BooleanField, EmailField, PasswordField,
                     StringField, SubmitField, ValidationError)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from bai_04.Chuong5Bai4 import USERS


class RegisterForm(FlaskForm):
    username = StringField("Tên đăng nhập", validators=[
        DataRequired(message="Vui lòng nhập tên đăng nhập."),
        Length(4, 20, message="Tên đăng nhập phải từ 4 đến 20 ký tự."),
        Regexp(r"^[a-z0-9_]+$",
               message="Tên đăng nhập chỉ gồm chữ thường không dấu, số và dấu _."),
    ])
    email = EmailField("Email", validators=[
        DataRequired(message="Vui lòng nhập email."),
        Email(message="Email không đúng định dạng."),
    ])
    password = PasswordField("Mật khẩu", validators=[
        DataRequired(message="Vui lòng nhập mật khẩu."),
        Length(min=8, message="Mật khẩu tối thiểu 8 ký tự."),
    ])
    confirm = PasswordField("Nhập lại mật khẩu", validators=[
        EqualTo("password", message="Mật khẩu nhập lại không khớp."),
    ])
    accept = BooleanField("Tôi đồng ý với điều khoản", validators=[
        DataRequired(message="Bạn phải đồng ý với điều khoản."),
    ])
    submit = SubmitField("Đăng ký")

    def validate_username(self, field):
        if field.data in USERS:
            raise ValidationError("Tên đăng nhập đã được sử dụng.")
