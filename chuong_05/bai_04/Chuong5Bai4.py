from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__)

USERS = {"admin": "admin123",
         "an": "an123456"}


def login():
    if session.get("user"):
        return redirect(url_for("index"))

    username = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember")

        if username in USERS and USERS[username] == password:
            session["user"] = username

            if remember:
                session.permanent = True
            else:
                session.permanent = False

            flash(f"Đăng nhập thành công. Xin chào {username}!")
            return redirect(url_for("index"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu.")

    return render_template("login.html", username=username)


def profile():
    if not session.get("user"):
        flash("Vui lòng đăng nhập để xem trang cá nhân.")
        return redirect(url_for("login"))

    return render_template("profile.html")


def logout():
    session.pop("user", None)
    flash("Bạn đã đăng xuất.")
    return redirect(url_for("index"))
