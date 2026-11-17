import os

import click
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_migrate import Migrate
from sqlalchemy import func, or_

from forms import ActionForm
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


def get_cart():
    return session.get("cart", {})


def save_cart(cart):
    session["cart"] = cart


def parse_quantity(value):
    try:
        return int(value)
    except ValueError:
        return None


def safe_next_url(target):
    if (target and target.startswith("/")
            and not target.startswith("//")
            and not target.startswith("/\\")):
        return target
    return url_for("book_list")


@app.context_processor
def inject_helpers():
    def is_active(endpoint):
        if request.endpoint == endpoint:
            return "active"
        return ""
    cart_count = sum(get_cart().values())
    return {"is_active": is_active, "cart_count": cart_count}


@app.template_filter("vnd")
def format_vnd(value):
    return f"{value:,.0f} đ".replace(",", ".")


@app.route("/")
def index():
    return redirect(url_for("book_list"))


@app.route("/books")
def book_list():
    keyword = request.args.get("q", "").strip()
    selected_category_id = request.args.get("category_id", type=int)

    stmt = db.select(Book).order_by(Book.id)
    if keyword:
        pattern = f"%{keyword}%"
        stmt = stmt.where(or_(Book.title.ilike(pattern),
                              Book.author.ilike(pattern)))
    if selected_category_id:
        stmt = stmt.filter_by(category_id=selected_category_id)
    books = db.session.execute(stmt).scalars().all()

    categories = db.session.execute(
        db.select(Category).order_by(Category.name)).scalars().all()
    action_form = ActionForm()
    return render_template("shop/books.html", books=books,
                           categories=categories,
                           keyword=keyword,
                           selected_category_id=selected_category_id,
                           action_form=action_form)


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    in_cart = get_cart().get(str(book.id), 0)
    max_quantity = max(book.stock - in_cart, 0)
    action_form = ActionForm()
    return render_template("shop/book_detail.html", book=book,
                           in_cart=in_cart,
                           max_quantity=max_quantity,
                           action_form=action_form)


@app.route("/cart/add/<int:book_id>", methods=["POST"])
def cart_add(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = ActionForm()
    next_url = safe_next_url(request.form.get("next"))

    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(next_url)

    if book.stock == 0:
        flash(f"Sách “{book.title}” đã hết hàng.", "danger")
        return redirect(next_url)

    cart = get_cart()
    in_cart = cart.get(str(book.id), 0)
    max_quantity = book.stock - in_cart
    if max_quantity <= 0:
        flash(f"Không thể thêm “{book.title}”: giỏ đã có {in_cart} cuốn, "
              f"tồn kho chỉ còn {book.stock}.", "warning")
        return redirect(next_url)

    quantity = parse_quantity(request.form.get("quantity", "1"))
    if quantity is None or quantity < 1 or quantity > max_quantity:
        flash(f"Số lượng không hợp lệ: chỉ được thêm từ 1 đến {max_quantity} "
              f"cuốn “{book.title}”.", "danger")
        return redirect(next_url)

    cart[str(book.id)] = in_cart + quantity
    save_cart(cart)
    flash(f"Đã thêm {quantity} × “{book.title}” vào giỏ hàng.", "success")
    return redirect(next_url)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


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
