import os

import click
from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from forms import BookForm, CategoryForm, DeleteForm
from models import Book, Category, db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-chi-dung-khi-phat-trien")
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
    if value is None:
        return None
    return value.strip() or None


def load_category_choices(form):
    categories = db.session.execute(
        db.select(Category).order_by(Category.name)).scalars().all()
    form.category_id.choices = [(0, "-- Chọn danh mục --")]
    for category in categories:
        form.category_id.choices.append((category.id, category.name))
    return categories


@app.context_processor
def inject_helpers():
    def is_active(endpoint):
        if request.endpoint == endpoint:
            return "active"
        return ""
    return {"is_active": is_active}


@app.route("/")
def dashboard():
    total_categories = db.session.scalar(db.select(func.count(Category.id)))
    total_books = db.session.scalar(db.select(func.count(Book.id)))
    total_copies = db.session.scalar(
        db.select(func.coalesce(func.sum(Book.quantity), 0)))
    out_of_stock = db.session.scalar(
        db.select(func.count(Book.id)).where(Book.quantity == 0))

    stmt = (db.select(Category, func.count(Book.id))
            .outerjoin(Book, Book.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.name))
    rows = db.session.execute(stmt).all()

    category_stats = []
    for category, book_count in rows:
        if total_books > 0:
            percent = round(book_count * 100 / total_books)
        else:
            percent = 0
        category_stats.append({
            "category": category,
            "book_count": book_count,
            "percent": percent,
        })

    recent_books = db.session.execute(
        db.select(Book)
        .order_by(Book.created_at.desc(), Book.id.desc())
        .limit(5)).scalars().all()

    return render_template("dashboard.html",
                           total_categories=total_categories,
                           total_books=total_books,
                           total_copies=total_copies,
                           out_of_stock=out_of_stock,
                           category_stats=category_stats,
                           recent_books=recent_books)



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



@app.route("/books")
def book_list():
    selected_category_id = request.args.get("category_id", type=int)

    stmt = db.select(Book).order_by(Book.title)
    if selected_category_id:
        stmt = stmt.filter_by(category_id=selected_category_id)
    books = db.session.execute(stmt).scalars().all()

    categories = db.session.execute(
        db.select(Category).order_by(Category.name)).scalars().all()
    delete_form = DeleteForm()
    return render_template("books/list.html", books=books,
                           categories=categories,
                           selected_category_id=selected_category_id,
                           delete_form=delete_form)


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    delete_form = DeleteForm()
    return render_template("books/detail.html", book=book,
                           delete_form=delete_form)


@app.route("/books/new", methods=["GET", "POST"])
def book_create():
    form = BookForm(category_id=request.args.get("category_id", type=int))
    categories = load_category_choices(form)

    if not categories:
        flash("Chưa có danh mục nào, hãy thêm danh mục trước.")
        return redirect(url_for("category_create"))

    if form.validate_on_submit():
        book = Book(title=form.title.data.strip(),
                    author=form.author.data.strip(),
                    year=form.year.data,
                    quantity=form.quantity.data,
                    description=clean_text(form.description.data),
                    category_id=form.category_id.data)
        db.session.add(book)
        db.session.commit()
        flash(f"Đã thêm sách “{book.title}”.")
        return redirect(url_for("book_detail", book_id=book.id))

    return render_template("books/form.html", form=form,
                           title="Thêm sách",
                           cancel_url=url_for("book_list"))


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def book_edit(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = BookForm(obj=book)
    load_category_choices(form)

    if form.validate_on_submit():
        book.title = form.title.data.strip()
        book.author = form.author.data.strip()
        book.year = form.year.data
        book.quantity = form.quantity.data
        book.description = clean_text(form.description.data)
        book.category_id = form.category_id.data
        db.session.commit()
        flash(f"Đã cập nhật sách “{book.title}”.")
        return redirect(url_for("book_detail", book_id=book.id))

    return render_template("books/form.html", form=form,
                           title=f"Sửa sách: {book.title}",
                           cancel_url=url_for("book_detail", book_id=book.id))


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def book_delete(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = DeleteForm()

    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.")
        return redirect(url_for("book_list"))

    db.session.delete(book)
    db.session.commit()
    flash(f"Đã xoá sách “{book.title}”.")
    return redirect(url_for("book_list"))


@app.errorhandler(404)
def page_not_found(error):
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
