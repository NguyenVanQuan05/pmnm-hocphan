# Đã hiểu và chỉnh sửa – Nguyễn Văn Quân
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


# Flask-SQLAlchemy tự đặt tên bảng theo tên lớp: Category -> "category"
class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    # Mapped[str | None]: cột được phép rỗng (NULL)
    description: Mapped[str | None] = mapped_column(Text)

    # Một danh mục có nhiều sách
    books: Mapped[list["Book"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


# Tên bảng: Book -> "book"
class Book(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column()
    # Điều kiện quantity >= 0 kiểm tra trong form (bước 4)
    quantity: Mapped[int] = mapped_column(default=1)
    description: Mapped[str | None] = mapped_column(Text)
    # Khoá ngoại: mỗi sách phải thuộc một danh mục
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    # Truyền hàm datetime.now (không có ngoặc) để mỗi lần thêm mới gọi
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Mỗi sách thuộc về một danh mục
    category: Mapped["Category"] = relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"
