from flask_wtf import FlaskForm
from wtforms import EmailField, RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp

from models import PAYMENT_METHODS


class ActionForm(FlaskForm):
    pass


class CheckoutForm(FlaskForm):
    customer_name = StringField("Họ tên *", validators=[
        DataRequired(message="Vui lòng nhập họ tên."),
        Length(max=100, message="Họ tên tối đa 100 ký tự."),
    ])
    phone = StringField("Số điện thoại *", validators=[
        DataRequired(message="Vui lòng nhập số điện thoại."),
        Regexp(r"^0\d{9}$",
               message="Số điện thoại gồm 10 chữ số, bắt đầu bằng 0."),
    ])
    email = EmailField("Email", validators=[
        Optional(),
        Email(message="Email không đúng định dạng."),
        Length(max=120, message="Email tối đa 120 ký tự."),
    ])
    address = TextAreaField("Địa chỉ giao hàng *", validators=[
        DataRequired(message="Vui lòng nhập địa chỉ giao hàng."),
        Length(max=255, message="Địa chỉ tối đa 255 ký tự."),
    ])
    note = StringField("Ghi chú")
    payment = RadioField("Thanh toán *",
                         choices=list(PAYMENT_METHODS.items()),
                         default="cod",
                         invalid_choice_message="Hình thức thanh toán không hợp lệ.")
    submit = SubmitField("Xác nhận đặt hàng")
