from datetime import date

from flask import Flask, render_template, request

app = Flask(__name__)

# Hai mẫu dữ liệu để cùng một macro tạo ra nhiều thẻ HTML.
TOPICS = [
    {
        "title": "include",
        "description": "Chèn một mảnh template vào trang đang hiển thị.",
        "tags": ["Chèn template", "Dùng chung context"],
    },
    {
        "title": "macro",
        "description": "Tạo lại cùng một mẫu HTML với dữ liệu khác nhau.",
        "tags": ["Tham số", "Tái sử dụng HTML"],
    },
]


# Danh sách bài viết; hiện chưa có bài viết nên post_count bằng 0.
POSTS = []


@app.context_processor
def inject_globals():
    return {
        "site_name": "MiniBlog",
        "current_year": date.today().year,
        "post_count": len(POSTS),
    }


@app.context_processor
def inject_helpers():
    def is_active(endpoint):
        return ("active" if request.endpoint == endpoint
                else "")
    return {"is_active": is_active}


@app.route("/")
def index():
    # Các tên bên trái dấu = trở thành biến trong context của template.
    return render_template(
        "about.html",
        course_name="Phần mềm mã nguồn mở",
        topics=TOPICS,
    )


@app.route("/about")
def about():
    return render_template("builtin_variables.html")
