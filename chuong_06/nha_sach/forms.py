from datetime import date

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import (
    EmailField,
    IntegerField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    ValidationError,
)
from wtforms.validators import (
    DataRequired,
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    Regexp,
)

from models import PAYMENT_METHODS, Book, Category, db

CURRENT_YEAR = date.today().year
MAX_COVER_SIZE = 2 * 1024 * 1024
COVER_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


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


class StatusForm(FlaskForm):
    status = SelectField("Chuyển sang", validate_choice=False, validators=[
        DataRequired(message="Vui lòng chọn trạng thái."),
    ])
    submit = SubmitField("Cập nhật")


class CategoryForm(FlaskForm):
    name = StringField("Tên danh mục *", validators=[
        DataRequired(message="Vui lòng nhập tên danh mục."),
        Length(max=100, message="Tên danh mục tối đa 100 ký tự."),
    ])
    description = TextAreaField("Mô tả")
    submit = SubmitField("+ Thêm")

    editing_id = None

    def validate_name(self, field):
        name = field.data.strip().lower()
        categories = db.session.execute(db.select(Category)).scalars().all()
        for category in categories:
            if category.name.lower() == name and category.id != self.editing_id:
                raise ValidationError("Danh mục đã tồn tại.")


class BookForm(FlaskForm):
    title = StringField("Tên sách *", validators=[
        DataRequired(message="Vui lòng nhập tên sách."),
        Length(max=200, message="Tên sách tối đa 200 ký tự."),
    ])
    author = StringField("Tác giả *", validators=[
        DataRequired(message="Vui lòng nhập tên tác giả."),
        Length(max=100, message="Tên tác giả tối đa 100 ký tự."),
    ])
    publisher = StringField("Nhà xuất bản", validators=[
        Length(max=100, message="Nhà xuất bản tối đa 100 ký tự."),
    ])
    category_id = SelectField("Danh mục *", coerce=int, validators=[
        DataRequired(message="Vui lòng chọn danh mục."),
    ], invalid_value_message="Danh mục không hợp lệ.",
       invalid_choice_message="Danh mục không tồn tại.")
    year = IntegerField("Năm xuất bản", validators=[
        Optional(),
        NumberRange(min=1900, max=CURRENT_YEAR,
                    message=f"Năm xuất bản phải từ 1900 đến {CURRENT_YEAR}."),
    ], invalid_value_message="Năm xuất bản phải là số nguyên.")
    price = IntegerField("Giá (đồng) *", validators=[
        InputRequired(message="Vui lòng nhập giá."),
        NumberRange(min=1000, message="Giá tối thiểu 1.000 đ."),
    ], invalid_value_message="Giá phải là số nguyên.")
    stock = IntegerField("Tồn kho *", default=0, validators=[
        InputRequired(message="Vui lòng nhập tồn kho."),
        NumberRange(min=0, message="Tồn kho không âm."),
    ], invalid_value_message="Tồn kho phải là số nguyên.")
    description = TextAreaField("Mô tả")
    cover_file = FileField("Ảnh bìa", validators=[
        FileAllowed(COVER_EXTENSIONS,
                    message="Chỉ nhận ảnh JPG, PNG hoặc WEBP."),
        FileSize(max_size=MAX_COVER_SIZE,
                 message="Ảnh bìa tối đa 2 MB."),
    ], render_kw={"accept": ".jpg,.jpeg,.png,.webp"})
    submit = SubmitField("Lưu")

    editing_id = None

    def validate_title(self, field):
        title = field.data.strip().lower()
        books = db.session.execute(db.select(Book)).scalars().all()
        for book in books:
            if book.title.lower() == title and book.id != self.editing_id:
                raise ValidationError("Tên sách đã tồn tại.")
