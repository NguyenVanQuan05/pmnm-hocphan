import os

import click
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import func

from models import Book, Category, db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-chi-dung-khi-phat-trien")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nha_sach.db"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
db.init_app(app)
migrate = Migrate(app, db)


SAMPLE_DATA = {
    "Lập trình": {
        "description": "Sách về ngôn ngữ và kỹ thuật lập trình.",
        "books": [
            {"title": "Lập trình Python cơ bản", "author": "Nguyễn Văn A",
             "publisher": "NXB Đại học Huế", "year": 2024,
             "price": 95000, "stock": 30,
             "description": "Nhập môn Python cho người mới bắt đầu."},
            {"title": "Giáo trình Flask", "author": "Miguel Grinberg",
             "price": 120000, "stock": 20,
             "description": "Xây dựng ứng dụng web với Flask."},
        ],
    },
    "Cơ sở dữ liệu": {
        "description": "Thiết kế và truy vấn cơ sở dữ liệu.",
        "books": [
            {"title": "Cơ sở dữ liệu", "author": "Trần Văn B",
             "price": 85000, "stock": 0,
             "description": "Mô hình quan hệ, SQL và chuẩn hoá."},
        ],
    },
    "Công cụ": {
        "description": "Công cụ hỗ trợ phát triển phần mềm.",
        "books": [
            {"title": "Pro Git", "author": "Scott Chacon",
             "price": 150000, "stock": 15,
             "description": "Quản lý mã nguồn với Git."},
        ],
    },
    "Mạng": {
        "description": "Mạng máy tính và truyền thông.",
        "books": [
            {"title": "Mạng máy tính", "author": "Lê Văn C",
             "price": 110000, "stock": 12,
             "description": "Mô hình TCP/IP và các giao thức cơ bản."},
        ],
    },
    "Kỹ năng lập trình": {
        "description": "Viết code sạch, dễ đọc, dễ bảo trì.",
        "books": [
            {"title": "Clean Code", "author": "Robert C. Martin",
             "year": 2008, "price": 180000, "stock": 5,
             "description": "Nguyên tắc viết code sạch."},
        ],
    },
    "Thiết kế": {
        "description": "Thiết kế giao diện và trải nghiệm người dùng.",
        "books": [],
    },
}


@app.cli.command("seed")
def seed_data():
    """Tạo dữ liệu mẫu: 6 danh mục, 6 sách."""
    total = db.session.scalar(db.select(func.count(Category.id)))
    if total > 0:
        click.echo(f"Đã có {total} danh mục, không thêm nữa.")
        return

    book_count = 0
    for category_name, category_info in SAMPLE_DATA.items():
        category = Category(name=category_name,
                            description=category_info["description"])
        db.session.add(category)

        for book_info in category_info["books"]:
            book = Book(title=book_info["title"],
                        author=book_info["author"],
                        publisher=book_info.get("publisher"),
                        year=book_info.get("year"),
                        price=book_info["price"],
                        stock=book_info["stock"],
                        description=book_info["description"],
                        category=category)
            db.session.add(book)
            book_count += 1

    db.session.commit()
    click.echo(f"Đã thêm {len(SAMPLE_DATA)} danh mục và {book_count} sách.")
