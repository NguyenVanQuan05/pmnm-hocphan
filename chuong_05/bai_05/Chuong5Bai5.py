from flask import Flask, flash, redirect, render_template, url_for

from bai_04.Chuong5Bai4 import USERS
from bai_05.forms import RegisterForm

app = Flask(__name__)


def register():
    form = RegisterForm()

    if form.validate_on_submit():
        USERS[form.username.data] = form.password.data
        flash("Đăng ký thành công.")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)
