from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

ORDER_STATUSES = ["Chờ xác nhận", "Đang giao", "Hoàn tất", "Đã huỷ"]

PAYMENT_METHODS = {
    "cod": "Tiền mặt khi nhận hàng",
    "bank": "Chuyển khoản",
}

NEXT_STATUSES = {
    "Chờ xác nhận": ["Đang giao", "Đã huỷ"],
    "Đang giao": ["Hoàn tất", "Đã huỷ"],
    "Hoàn tất": [],
    "Đã huỷ": [],
}


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
    publisher: Mapped[str | None] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column()
    price: Mapped[int] = mapped_column()
    stock: Mapped[int] = mapped_column(default=0)
    description: Mapped[str | None] = mapped_column(Text)
    cover: Mapped[str | None] = mapped_column(String(100))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    category: Mapped["Category"] = relationship(back_populates="books")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="book")

    def __repr__(self):
        return f"<Book {self.title}>"


class Order(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(String(255))
    note: Mapped[str | None] = mapped_column(Text)
    payment: Mapped[str] = mapped_column(String(10))
    subtotal: Mapped[int] = mapped_column()
    shipping_fee: Mapped[int] = mapped_column()
    total: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    history: Mapped[list["OrderHistory"]] = relationship(back_populates="order")

    def __repr__(self):
        return f"<Order #{self.id} {self.status}>"


class OrderItem(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[int] = mapped_column()

    order: Mapped["Order"] = relationship(back_populates="items")
    book: Mapped["Book"] = relationship(back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem order={self.order_id} book={self.book_id} x{self.quantity}>"


class OrderHistory(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    order: Mapped["Order"] = relationship(back_populates="history")

    def __repr__(self):
        return f"<OrderHistory order={self.order_id} {self.status}>"
