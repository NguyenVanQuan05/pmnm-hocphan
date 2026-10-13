from flask import Flask, url_for, request, abort, redirect, make_response
from markupsafe import escape

app = Flask(__name__)
app.json.ensure_ascii = False


STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0},
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0},
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0},
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0},
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {},
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0},
    },
}

def calculate_result(student):
    scores = student["scores"]

    if not scores:
        return None, "Chưa có điểm"

    average = sum(scores.values()) / len(scores)

    if average >= 8:
        classification = "Giỏi"
    elif average >= 6.5:
        classification = "Khá"
    elif average >= 5:
        classification = "Trung bình"
    else:
        classification = "Yếu"

    return average, classification

@app.route("/students")
def student_list():
    classes = set()
    for student in STUDENTS.values():
        classes.add(student["lop"])

    all_url = url_for("student_list")
    filter_bar = f'<a href="{all_url}">Tất cả</a>'

    for class_name in sorted(classes):
        class_url = url_for("student_list", lop=class_name)
        filter_bar += (
            f' | <a href="{escape(class_url)}">'
            f'{escape(class_name)}</a>'
        )

    selected_class = request.args.get("lop", "").strip().upper()
    rows = ""

    for student_id, student in STUDENTS.items():
        if selected_class and student["lop"].upper() != selected_class:
            continue

        average, classification = calculate_result(student)
        average_text = "–" if average is None else f"{average:.2f}"
        detail_url = url_for("student_detail", student_id=student_id)

        rows += (
            "<tr>"
            f'<td><a href="{escape(detail_url)}">'
            f"{escape(student_id)}</a></td>"
            f"<td>{escape(student['name'])}</td>"
            f"<td>{escape(student['lop'])}</td>"
            f"<td>{average_text}</td>"
            f"<td>{escape(classification)}</td>"
            "</tr>"
        )

    if not rows:
        return filter_bar + "<p>Không có sinh viên phù hợp.</p>"

    return (
        filter_bar
        + "<table border='1'>"
        + "<tr>"
        + "<th>MSSV</th><th>Họ tên</th><th>Lớp</th>"
        + "<th>Điểm TB</th><th>Xếp loại</th>"
        + "</tr>"
        + rows
        + "</table>"
    )


@app.route("/students/<student_id>")
def student_detail(student_id):
    student = STUDENTS.get(student_id)

    if student is None:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {student_id}.",
        )

    average, classification = calculate_result(student)
    average_text = "–" if average is None else f"{average:.2f}"

    class_url = url_for("student_list", lop=student["lop"])
    export_url = url_for("export_scores", student_id=student_id)
    short_url = url_for("student_short_link", student_id=student_id)

    score_rows = ""
    for subject, score in student["scores"].items():
        score_rows += (
            "<tr>"
            f"<td>{escape(subject)}</td>"
            f"<td>{score}</td>"
            "</tr>"
        )

    if not score_rows:
        score_rows = '<tr><td colspan="2">Chưa có điểm</td></tr>'

    return f"""
    <h1>Chi tiết sinh viên</h1>
    <p>Họ tên: {escape(student["name"])}</p>
    <p>MSSV: {escape(student_id)}</p>
    <p>Lớp:
        <a href="{escape(class_url)}">{escape(student["lop"])}</a>
    </p>
    <p>Điểm TB: {average_text}</p>
    <p>Xếp loại: {escape(classification)}</p>
    <table border="1">
        <tr><th>Học phần</th><th>Điểm</th></tr>
        {score_rows}
    </table>
    <p><a href="{escape(export_url)}">Tải bảng điểm (CSV)</a></p>
    <p>Link rút gọn:
        <a href="{escape(short_url)}">{escape(short_url)}</a>
    </p>
    """


@app.route("/")
def index():
    classes = set()
    for student in STUDENTS.values():
        classes.add(student["lop"])

    students_url = url_for("student_list")

    return f"""
    <h1>Sổ điểm sinh viên</h1>
    <p>Tổng số sinh viên: {len(STUDENTS)}</p>
    <p>Số lớp: {len(classes)}</p>
    <a href="{students_url}">Danh sách sinh viên</a>
    |
    <a href="/api/students">Dữ liệu JSON sinh viên</a>
    """


@app.route("/sv/<student_id>")
def student_short_link(student_id):
    return redirect(
        url_for("student_detail", student_id=student_id),
        code=301,
    )


@app.route("/students/<student_id>/export")
def export_scores(student_id):
    student = STUDENTS.get(student_id)

    if student is None:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {student_id}.",
        )

    csv_content = "hoc_phan,diem\n"
    for subject, score in student["scores"].items():
        csv_content += f"{subject},{score}\n"

    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=diem_{student_id}.csv"
    )
    return response


@app.route("/search")
def search_students():
    keyword = request.args.get("q", "")
    search_url = url_for("search_students")

    form = f"""
    <form method="get" action="{escape(search_url)}">
        <input type="text" name="q" value="{escape(keyword)}">
        <button type="submit">Tìm kiếm</button>
    </form>
    """

    if not keyword:
        return form

    items = ""
    count = 0
    keyword_lower = keyword.lower()

    for student_id, student in STUDENTS.items():
        name_matches = keyword_lower in student["name"].lower()
        id_matches = keyword_lower in student_id.lower()

        if name_matches or id_matches:
            count += 1
            detail_url = url_for(
                "student_detail",
                student_id=student_id,
            )
            items += (
                f'<li><a href="{escape(detail_url)}">'
                f'{escape(student_id)} - {escape(student["name"])}'
                "</a></li>"
            )

    return (
        form
        + f'<p>Tìm thấy {count} kết quả cho "{escape(keyword)}".</p>'
        + f"<ul>{items}</ul>"
    )
