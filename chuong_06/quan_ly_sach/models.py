from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    books: Mapped[list["Book"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Book(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column()
    quantity: Mapped[int] = mapped_column(default=1)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    category: Mapped["Category"] = relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"
