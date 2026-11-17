from flask import Flask, render_template, request
from jinja2 import ChoiceLoader

from bai_01 import Chuong5Bai1
from bai_02 import Chuong5Bai2
from bai_03 import Chuong5Bai3
from bai_04 import Chuong5Bai4
from bai_05 import Chuong5Bai5

app = Flask(__name__)
app.config["SECRET_KEY"] = "chuoi-bi-mat"

app.jinja_loader = ChoiceLoader([
    app.jinja_loader,
    Chuong5Bai1.app.jinja_loader,
    Chuong5Bai2.app.jinja_loader,
    Chuong5Bai3.app.jinja_loader,
    Chuong5Bai4.app.jinja_loader,
    Chuong5Bai5.app.jinja_loader,
])


@app.context_processor
def inject_helpers():
    def is_active(endpoint):
        if request.endpoint == endpoint:
            return "active"
        return ""
    return {"is_active": is_active}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/bai-1", methods=["GET", "POST"])
def calculator():
    return Chuong5Bai1.calculator()


@app.route("/bai-2", methods=["GET", "POST"])
def grade_calculator():
    return Chuong5Bai2.grade_calculator()


@app.route("/bai-3", methods=["GET", "POST"])
def bmi_calculator():
    return Chuong5Bai3.bmi_calculator()


@app.route("/login", methods=["GET", "POST"])
def login():
    return Chuong5Bai4.login()


@app.route("/profile")
def profile():
    return Chuong5Bai4.profile()


@app.route("/logout", methods=["POST"])
def logout():
    return Chuong5Bai4.logout()


@app.route("/register", methods=["GET", "POST"])
def register():
    return Chuong5Bai5.register()


if __name__ == "__main__":
    app.run(debug=True)
