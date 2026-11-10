# Đã hiểu và chỉnh sửa – Nguyễn Văn Quân
import os

import click
from flask import Flask

from models import Book, Category, db

app = Flask(__name__)

# SECRET_KEY đọc từ biến môi trường; giá trị dự phòng chỉ dùng khi phát triển
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-chi-dung-khi-phat-trien")
# Đường dẫn tương đối => Flask-SQLAlchemy đặt file trong thư mục instance/
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"

db.init_app(app)

# Tạo các bảng nếu chưa có (không xoá dữ liệu cũ)
with app.app_context():
    db.create_all()


SAMPLE_DATA = {
    "Lập trình": {
        "description": "Sách về lập trình và phát triển phần mềm.",
        "books": [
            {"title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "quantity": 3},
            {"title": "Python Crash Course", "author": "Eric Matthes", "year": 2019, "quantity": 2},
            {"title": "Flask Web Development", "author": "Miguel Grinberg", "year": 2018, "quantity": 1},
        ],
    },
    "Văn học Việt Nam": {
        "description": "Tác phẩm văn học Việt Nam tiêu biểu.",
        "books": [
            {"title": "Dế Mèn phiêu lưu ký", "author": "Tô Hoài", "year": 1941, "quantity": 5},
            {"title": "Số đỏ", "author": "Vũ Trọng Phụng", "year": 1936, "quantity": 2},
            {"title": "Tắt đèn", "author": "Ngô Tất Tố", "year": 1939, "quantity": 4},
        ],
    },
    "Kỹ năng sống": {
        "description": "Sách phát triển bản thân.",
        "books": [
            {"title": "Đắc nhân tâm", "author": "Dale Carnegie", "year": 1936, "quantity": 6},
            {"title": "Atomic Habits", "author": "James Clear", "year": 2018, "quantity": 0},
        ],
    },
}


@app.cli.command("seed")
def seed_data():
    """Tạo dữ liệu mẫu: 3 danh mục, 8 sách."""
    existing_category = db.session.scalar(db.select(Category))
    if existing_category is not None:
        click.echo("CSDL đã có dữ liệu, bỏ qua seed.")
        return

    book_count = 0
    for category_name, category_info in SAMPLE_DATA.items():
        category = Category(
            name=category_name,
            description=category_info["description"],
        )
        db.session.add(category)

        for book_info in category_info["books"]:
            book = Book(
                title=book_info["title"],
                author=book_info["author"],
                year=book_info["year"],
                quantity=book_info["quantity"],
                category=category,
            )
            db.session.add(book)
            book_count += 1

    db.session.commit()
    click.echo(f"Đã tạo {len(SAMPLE_DATA)} danh mục và {book_count} sách.")
