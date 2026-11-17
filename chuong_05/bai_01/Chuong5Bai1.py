from flask import Flask, render_template, request

app = Flask(__name__)


def calculator():
    a = ""
    op = "+"
    b = ""
    errors = {}
    result = None

    if request.method == "POST":
        a = request.form.get("a", "")
        op = request.form.get("op", "")
        b = request.form.get("b", "")

        try:
            so_a = float(a.replace(",", "."))
        except ValueError:
            errors["a"] = "Vui lòng nhập một số."

        try:
            so_b = float(b.replace(",", "."))
        except ValueError:
            errors["b"] = "Vui lòng nhập một số."

        if op not in ["+", "-", "*", "/"]:
            errors["op"] = "Phép toán không hợp lệ."

        if op == "/" and "b" not in errors and so_b == 0:
            errors["b"] = "Không thể chia cho 0."

        if not errors:
            if op == "+":
                ket_qua = so_a + so_b
            elif op == "-":
                ket_qua = so_a - so_b
            elif op == "*":
                ket_qua = so_a * so_b
            else:
                ket_qua = so_a / so_b

            result = f"{so_a:g} {op} {so_b:g} = {ket_qua:g}"

    return render_template("calc.html", a=a, op=op, b=b,
                           errors=errors, result=result)
