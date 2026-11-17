import os
import secrets
from datetime import datetime

import click
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_migrate import Migrate
from sqlalchemy import func, or_

from forms import ActionForm, BookForm, CheckoutForm
from models import (
    ORDER_STATUSES,
    PAYMENT_METHODS,
    STATUS_COLORS,
    Book,
    Category,
    Order,
    OrderHistory,
    OrderItem,
    db,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-chi-dung-khi-phat-trien")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nha_sach.db"
app.config["MAX_CONTENT_LENGTH"] = 3 * 1024 * 1024
db.init_app(app)
migrate = Migrate(app, db)

SHIPPING_FEE = 20000
FREE_SHIPPING_FROM = 200000
LOW_STOCK_LIMIT = 5
ADMIN_BOOKS_PER_PAGE = 5
COVER_FOLDER = os.path.join(app.static_folder, "uploads", "covers")

STOCK_FILTERS = {
    "con_hang": "Còn hàng",
    "sap_het": f"Sắp hết (≤ {LOW_STOCK_LIMIT})",
    "het_hang": "Hết hàng",
}

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


def clean_text(value):
    if value is None:
        return None
    return value.strip() or None


def calculate_shipping_fee(subtotal):
    if subtotal >= FREE_SHIPPING_FROM:
        return 0
    return SHIPPING_FEE


def month_range(day):
    start = datetime(day.year, day.month, 1)
    if day.month == 12:
        return start, datetime(day.year + 1, 1, 1)
    return start, datetime(day.year, day.month + 1, 1)


def get_cart():
    return session.get("cart", {})


def save_cart(cart):
    session["cart"] = cart


def cart_items():
    cart = get_cart()
    if not cart:
        return [], 0

    book_ids = [int(book_id) for book_id in cart]
    books = db.session.execute(
        db.select(Book).where(Book.id.in_(book_ids))).scalars().all()
    books_by_id = {str(book.id): book for book in books}

    items = []
    total = 0
    removed_count = 0
    for book_id, quantity in list(cart.items()):
        book = books_by_id.get(book_id)
        if book is None:
            del cart[book_id]
            removed_count += 1
            continue
        line_total = book.price * quantity
        items.append({"book": book, "quantity": quantity,
                      "line_total": line_total})
        total += line_total

    if removed_count > 0:
        save_cart(cart)
        flash(f"Đã bỏ {removed_count} sách khỏi giỏ vì sách không còn bán.",
              "warning")
    return items, total


def parse_quantity(value):
    try:
        return int(value)
    except ValueError:
        return None


def safe_next_url(target, fallback="book_list"):
    if (target and target.startswith("/")
            and not target.startswith("//")
            and not target.startswith("/\\")):
        return target
    return url_for(fallback)


def load_category_choices(form):
    categories = db.session.execute(
        db.select(Category).order_by(Category.name)).scalars().all()
    form.category_id.choices = [(0, "-- Chọn danh mục --")]
    for category in categories:
        form.category_id.choices.append((category.id, category.name))
    return categories


def save_cover_file(file):
    extension = os.path.splitext(file.filename)[1].lower()
    filename = secrets.token_hex(8) + extension
    os.makedirs(COVER_FOLDER, exist_ok=True)
    file.save(os.path.join(COVER_FOLDER, filename))
    return filename


def delete_cover_file(filename):
    if not filename:
        return
    path = os.path.join(COVER_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)


@app.context_processor
def inject_helpers():
    def is_active(endpoint):
        if request.endpoint == endpoint:
            return "active"
        return ""
    cart_count = sum(get_cart().values())

    pending_count = 0
    if request.path.startswith("/admin"):
        pending_count = db.session.scalar(
            db.select(func.count(Order.id)).filter_by(status=ORDER_STATUSES[0]))

    return {"is_active": is_active, "cart_count": cart_count,
            "pending_count": pending_count,
            "status_colors": STATUS_COLORS}


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


@app.route("/cart")
def cart_view():
    items, total = cart_items()
    action_form = ActionForm()
    return render_template("shop/cart.html", items=items, total=total,
                           action_form=action_form)


@app.route("/cart/increase/<int:book_id>", methods=["POST"])
def cart_increase(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = ActionForm()

    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(url_for("cart_view"))

    cart = get_cart()
    key = str(book.id)
    if key not in cart:
        flash(f"“{book.title}” không có trong giỏ hàng.", "warning")
        return redirect(url_for("cart_view"))

    if cart[key] >= book.stock:
        flash(f"Không thể tăng “{book.title}”: tồn kho chỉ còn "
              f"{book.stock} cuốn.", "warning")
        return redirect(url_for("cart_view"))

    cart[key] += 1
    save_cart(cart)
    flash(f"Đã tăng “{book.title}” lên {cart[key]} cuốn.", "success")
    return redirect(url_for("cart_view"))


@app.route("/cart/decrease/<int:book_id>", methods=["POST"])
def cart_decrease(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = ActionForm()

    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(url_for("cart_view"))

    cart = get_cart()
    key = str(book.id)
    if key not in cart:
        flash(f"“{book.title}” không có trong giỏ hàng.", "warning")
        return redirect(url_for("cart_view"))

    cart[key] -= 1
    if cart[key] == 0:
        del cart[key]
        flash(f"Đã bỏ “{book.title}” khỏi giỏ hàng.", "success")
    else:
        flash(f"Đã giảm “{book.title}” còn {cart[key]} cuốn.", "success")
    save_cart(cart)
    return redirect(url_for("cart_view"))


@app.route("/cart/remove/<int:book_id>", methods=["POST"])
def cart_remove(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = ActionForm()

    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(url_for("cart_view"))

    cart = get_cart()
    key = str(book.id)
    if key not in cart:
        flash(f"“{book.title}” không có trong giỏ hàng.", "warning")
        return redirect(url_for("cart_view"))

    del cart[key]
    save_cart(cart)
    flash(f"Đã bỏ “{book.title}” khỏi giỏ hàng.", "success")
    return redirect(url_for("cart_view"))


@app.route("/cart/clear", methods=["POST"])
def cart_clear():
    form = ActionForm()

    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(url_for("cart_view"))

    save_cart({})
    flash("Đã xoá toàn bộ giỏ hàng.", "success")
    return redirect(url_for("cart_view"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, subtotal = cart_items()
    if not items:
        flash("Giỏ hàng trống, hãy chọn sách trước khi đặt hàng.", "warning")
        return redirect(url_for("cart_view"))

    shipping_fee = calculate_shipping_fee(subtotal)
    form = CheckoutForm()

    if form.validate_on_submit():
        shortages = []
        for item in items:
            book = item["book"]
            if item["quantity"] > book.stock:
                shortages.append(f"“{book.title}” chỉ còn {book.stock} cuốn")
        if shortages:
            flash("Không đủ hàng: " + "; ".join(shortages)
                  + ". Đơn hàng chưa được tạo, vui lòng sửa lại giỏ hàng.",
                  "danger")
            return redirect(url_for("cart_view"))

        order = Order(customer_name=form.customer_name.data.strip(),
                      phone=form.phone.data.strip(),
                      email=clean_text(form.email.data),
                      address=form.address.data.strip(),
                      note=clean_text(form.note.data),
                      payment=form.payment.data,
                      subtotal=subtotal,
                      shipping_fee=shipping_fee,
                      total=subtotal + shipping_fee,
                      status=ORDER_STATUSES[0])
        db.session.add(order)

        for item in items:
            book = item["book"]
            db.session.add(OrderItem(order=order, book=book,
                                     quantity=item["quantity"],
                                     unit_price=book.price))
            book.stock -= item["quantity"]

        db.session.add(OrderHistory(order=order, status=ORDER_STATUSES[0]))
        db.session.commit()

        save_cart({})
        my_orders = session.get("my_orders", [])
        my_orders.append(order.id)
        session["my_orders"] = my_orders
        flash(f"Đặt hàng thành công. Mã đơn của bạn là #{order.id}.", "success")
        return redirect(url_for("order_done", order_id=order.id))

    return render_template("shop/checkout.html", form=form, items=items,
                           subtotal=subtotal,
                           shipping_fee=shipping_fee,
                           total=subtotal + shipping_fee,
                           free_shipping_from=FREE_SHIPPING_FROM)


@app.route("/orders/<int:order_id>")
def order_done(order_id):
    if order_id not in session.get("my_orders", []):
        abort(404, description=f"Không có đơn hàng với mã #{order_id}.")

    order = db.get_or_404(Order, order_id,
                          description=f"Không có đơn hàng với mã #{order_id}.")
    return render_template("shop/order_done.html", order=order,
                           payment_methods=PAYMENT_METHODS)


@app.route("/admin")
def admin_dashboard():
    total_books = db.session.scalar(db.select(func.count(Book.id)))
    pending_orders = db.session.scalar(
        db.select(func.count(Order.id)).filter_by(status=ORDER_STATUSES[0]))

    now = datetime.now()
    month_start, next_month_start = month_range(now)
    month_revenue = db.session.scalar(
        db.select(func.coalesce(func.sum(Order.total), 0))
        .join(OrderHistory, OrderHistory.order_id == Order.id)
        .where(OrderHistory.status == ORDER_STATUSES[2],
               OrderHistory.created_at >= month_start,
               OrderHistory.created_at < next_month_start))
    low_stock_count = db.session.scalar(
        db.select(func.count(Book.id)).where(Book.stock <= LOW_STOCK_LIMIT))

    recent_orders = db.session.execute(
        db.select(Order)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .limit(5)).scalars().all()
    low_stock_books = db.session.execute(
        db.select(Book)
        .where(Book.stock <= LOW_STOCK_LIMIT)
        .order_by(Book.stock, Book.title)).scalars().all()

    return render_template("admin/dashboard.html",
                           total_books=total_books,
                           pending_orders=pending_orders,
                           month=now.month,
                           month_revenue=month_revenue,
                           low_stock_count=low_stock_count,
                           low_stock_limit=LOW_STOCK_LIMIT,
                           recent_orders=recent_orders,
                           low_stock_books=low_stock_books)


@app.route("/admin/books")
def admin_books():
    keyword = request.args.get("q", "").strip()
    selected_category_id = request.args.get("category_id", type=int)
    stock = request.args.get("stock", "")
    if stock not in STOCK_FILTERS:
        stock = ""

    stmt = db.select(Book).order_by(Book.created_at.desc(), Book.id.desc())
    if keyword:
        pattern = f"%{keyword}%"
        stmt = stmt.where(or_(Book.title.ilike(pattern),
                              Book.author.ilike(pattern)))
    if selected_category_id:
        stmt = stmt.filter_by(category_id=selected_category_id)
    if stock == "con_hang":
        stmt = stmt.where(Book.stock > 0)
    elif stock == "sap_het":
        stmt = stmt.where(Book.stock <= LOW_STOCK_LIMIT)
    elif stock == "het_hang":
        stmt = stmt.where(Book.stock == 0)

    filter_args = {}
    if keyword:
        filter_args["q"] = keyword
    if selected_category_id:
        filter_args["category_id"] = selected_category_id
    if stock:
        filter_args["stock"] = stock

    page = request.args.get("page", 1, type=int)
    books_page = db.paginate(stmt, page=page, per_page=ADMIN_BOOKS_PER_PAGE,
                             error_out=False)
    if books_page.pages and books_page.page > books_page.pages:
        return redirect(url_for("admin_books", page=books_page.pages,
                                **filter_args))

    book_ids = [book.id for book in books_page.items]
    ordered_ids = set(db.session.execute(
        db.select(OrderItem.book_id)
        .where(OrderItem.book_id.in_(book_ids))
        .distinct()).scalars().all())

    categories = db.session.execute(
        db.select(Category).order_by(Category.name)).scalars().all()
    action_form = ActionForm()
    return render_template("admin/books.html", books_page=books_page,
                           ordered_ids=ordered_ids,
                           filter_args=filter_args,
                           keyword=keyword,
                           selected_category_id=selected_category_id,
                           stock=stock,
                           stock_filters=STOCK_FILTERS,
                           categories=categories,
                           action_form=action_form)


@app.route("/admin/books/new", methods=["GET", "POST"])
def admin_book_create():
    form = BookForm()
    categories = load_category_choices(form)

    if not categories:
        flash("Chưa có danh mục nào, hãy thêm danh mục trước.", "warning")
        return redirect(url_for("admin_books"))

    if form.validate_on_submit():
        cover = None
        if form.cover_file.data:
            cover = save_cover_file(form.cover_file.data)
        book = Book(title=form.title.data.strip(),
                    author=form.author.data.strip(),
                    publisher=clean_text(form.publisher.data),
                    year=form.year.data,
                    price=form.price.data,
                    stock=form.stock.data,
                    description=clean_text(form.description.data),
                    cover=cover,
                    category_id=form.category_id.data)
        db.session.add(book)
        db.session.commit()
        flash(f"Đã thêm sách “{book.title}”.", "success")
        return redirect(url_for("admin_books"))

    return render_template("admin/book_form.html", form=form, book=None,
                           title="Thêm sách",
                           breadcrumb="Thêm",
                           cancel_url=url_for("admin_books"))


@app.route("/admin/books/<int:book_id>/edit", methods=["GET", "POST"])
def admin_book_edit(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = BookForm(obj=book)
    form.editing_id = book.id
    load_category_choices(form)

    if form.validate_on_submit():
        old_cover = None
        if form.cover_file.data:
            old_cover = book.cover
            book.cover = save_cover_file(form.cover_file.data)
        book.title = form.title.data.strip()
        book.author = form.author.data.strip()
        book.publisher = clean_text(form.publisher.data)
        book.year = form.year.data
        book.price = form.price.data
        book.stock = form.stock.data
        book.description = clean_text(form.description.data)
        book.category_id = form.category_id.data
        db.session.commit()
        delete_cover_file(old_cover)
        flash(f"Đã cập nhật sách “{book.title}”.", "success")
        return redirect(url_for("admin_books"))

    return render_template("admin/book_form.html", form=form, book=book,
                           title=f"Sửa sách: {book.title}",
                           breadcrumb="Sửa",
                           cancel_url=url_for("admin_books"))


@app.route("/admin/books/<int:book_id>/delete", methods=["POST"])
def admin_book_delete(book_id):
    book = db.get_or_404(Book, book_id,
                         description=f"Không có sách với id = {book_id}.")
    form = ActionForm()
    next_url = safe_next_url(request.form.get("next"), "admin_books")

    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(next_url)

    order_count = db.session.scalar(
        db.select(func.count(OrderItem.id)).filter_by(book_id=book.id))
    if order_count > 0:
        flash(f"Không thể xoá “{book.title}” vì sách đã có trong "
              f"{order_count} đơn hàng.", "danger")
        return redirect(next_url)

    cover = book.cover
    db.session.delete(book)
    db.session.commit()
    delete_cover_file(cover)
    flash(f"Đã xoá sách “{book.title}”.", "success")
    return redirect(next_url)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


@app.errorhandler(413)
def request_too_large(error):
    flash("Dữ liệu gửi lên quá lớn (tối đa 3 MB). Ảnh bìa chỉ được tối đa 2 MB.",
          "danger")
    return redirect(request.url)


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
