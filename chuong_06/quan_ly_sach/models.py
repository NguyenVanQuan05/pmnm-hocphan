# Đã hiểu và chỉnh sửa – Nguyễn Văn Quân
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Lớp gốc cho mọi model (kiểu SQLAlchemy 2.x)
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Category(db.Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Mapped[str] => NOT NULL; unique => không trùng tên ở mức CSDL
    name: Mapped[str] = mapped_column(String(100), unique=True)
    # Mapped[str | None] => cho phép rỗng (NULL)
    description: Mapped[str | None] = mapped_column(Text)

    # Một danh mục có nhiều sách (quan hệ 1-n)
    books: Mapped[list["Book"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Book(db.Model):
    __tablename__ = "book"
    # Ràng buộc ở mức CSDL: số lượng không được âm
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_book_quantity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    year: Mapped[int | None]
    quantity: Mapped[int] = mapped_column(default=1)
    description: Mapped[str | None] = mapped_column(Text)
    # Khoá ngoại trỏ tới bảng category, bắt buộc phải có
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    # Truyền hàm datetime.now (không có ngoặc) để mỗi lần INSERT mới gọi
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    # Mỗi sách thuộc về đúng một danh mục
    category: Mapped["Category"] = relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"
