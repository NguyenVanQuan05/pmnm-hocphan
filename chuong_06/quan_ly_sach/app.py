# Đã hiểu và chỉnh sửa – Nguyễn Văn Quân
import os

import click
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from forms import CategoryForm, DeleteForm
from models import Book, Category, db

app = Flask(__name__)
# Đọc SECRET_KEY từ biến môi trường; giá trị dự phòng chỉ dùng khi phát triển
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-chi-dung-khi-phat-trien")
# File CSDL nằm trong thư mục instance/
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
db.init_app(app)

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


def clean_text(value):
    # Bỏ khoảng trắng đầu/cuối; chuỗi rỗng hoặc None thì trả None (lưu NULL)
    if value is None:
        return None
    return value.strip() or None


@app.context_processor
def inject_helpers():
    # Trả "active" nếu đang ở đúng trang, dùng để tô màu menu
    def is_active(endpoint):
        if request.endpoint == endpoint:
            return "active"
        return ""
    return {"is_active": is_active}


@app.route("/")
def dashboard():
    # Tạm thời chỉ có tiêu đề, bước 5 mới thêm thống kê
    return render_template("dashboard.html")


# ===== CRUD danh mục =====

@app.route("/categories")
def category_list():
    categories = db.session.execute(
        db.select(Category).order_by(Category.name)).scalars().all()
    delete_form = DeleteForm()
    return render_template("categories/list.html",
                           categories=categories, delete_form=delete_form)


@app.route("/categories/<int:category_id>")
def category_detail(category_id):
    category = db.get_or_404(Category, category_id,
                             description=f"Không có danh mục với id = {category_id}.")
    books = db.session.execute(
        db.select(Book).filter_by(category_id=category.id)
        .order_by(Book.title)).scalars().all()
    delete_form = DeleteForm()
    return render_template("categories/detail.html", category=category,
                           books=books, delete_form=delete_form)


@app.route("/categories/new", methods=["GET", "POST"])
def category_create():
    form = CategoryForm()

    if form.validate_on_submit():
        category = Category(name=form.name.data.strip(),
                            description=clean_text(form.description.data))
        db.session.add(category)
        db.session.commit()
        flash(f"Đã thêm danh mục “{category.name}”.")
        return redirect(url_for("category_list"))

    return render_template("categories/form.html", form=form,
                           title="Thêm danh mục",
                           cancel_url=url_for("category_list"))


@app.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def category_edit(category_id):
    category = db.get_or_404(Category, category_id,
                             description=f"Không có danh mục với id = {category_id}.")
    # obj=category: điền sẵn dữ liệu cũ vào form khi mở trang (GET)
    form = CategoryForm(obj=category)
    form.editing_id = category.id

    if form.validate_on_submit():
        category.name = form.name.data.strip()
        category.description = clean_text(form.description.data)
        db.session.commit()
        flash(f"Đã cập nhật danh mục “{category.name}”.")
        return redirect(url_for("category_detail", category_id=category.id))

    return render_template("categories/form.html", form=form,
                           title=f"Sửa danh mục: {category.name}",
                           cancel_url=url_for("category_detail", category_id=category.id))


@app.route("/categories/<int:category_id>/delete", methods=["POST"])
def category_delete(category_id):
    category = db.get_or_404(Category, category_id,
                             description=f"Không có danh mục với id = {category_id}.")
    form = DeleteForm()

    # validate_on_submit ở đây chính là bước kiểm tra CSRF token
    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.")
        return redirect(url_for("category_list"))

    if category.books:
        flash(f"Không thể xoá “{category.name}” vì danh mục còn "
              f"{len(category.books)} sách.")
        return redirect(url_for("category_detail", category_id=category.id))

    db.session.delete(category)
    db.session.commit()
    flash(f"Đã xoá danh mục “{category.name}”.")
    return redirect(url_for("category_list"))


# Route giữ chỗ để menu gọi url_for được; bước 4 sẽ thay thế
@app.route("/books")
def book_list():
    abort(404, description="Trang sách sẽ làm ở bước 4.")


@app.errorhandler(404)
def page_not_found(error):
    # Trả template riêng kèm mã 404 (nếu không ghi, mặc định là 200)
    return render_template("404.html", error=error), 404


@app.cli.command("seed")
def seed_data():
    """Tạo dữ liệu mẫu: 3 danh mục, 8 sách."""
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
                        year=book_info["year"],
                        quantity=book_info["quantity"],
                        category=category)
            db.session.add(book)
            book_count += 1

    db.session.commit()
    click.echo(f"Đã thêm {len(SAMPLE_DATA)} danh mục và {book_count} sách.")
