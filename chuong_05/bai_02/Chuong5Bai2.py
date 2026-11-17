from flask import Flask, render_template, request

app = Flask(__name__)


def kiem_tra_diem(gia_tri, ten, errors):
    try:
        diem = float(gia_tri.replace(",", "."))
    except ValueError:
        errors[ten] = "Vui lòng nhập một số."
        return None

    if diem < 0 or diem > 10:
        errors[ten] = "Điểm phải từ 0 đến 10."
        return None 

    return diem


def grade_calculator():
    values = {"cc": "", "gk": "", "ck": ""}
    errors = {}
    result = None

    if request.method == "POST":
        values["cc"] = request.form.get("cc", "")
        values["gk"] = request.form.get("gk", "")
        values["ck"] = request.form.get("ck", "")

        cc = kiem_tra_diem(values["cc"], "cc", errors)
        gk = kiem_tra_diem(values["gk"], "gk", errors)
        ck = kiem_tra_diem(values["ck"], "ck", errors)

        if not errors:
            tong_ket = round(cc * 0.1 + gk * 0.3 + ck * 0.6, 1)

            if ck < 1:
                diem_chu = "F"
            elif tong_ket >= 8.5:
                diem_chu = "A"
            elif tong_ket >= 7.0:
                diem_chu = "B"
            elif tong_ket >= 5.5:
                diem_chu = "C"
            elif tong_ket >= 4.0:
                diem_chu = "D"
            else:
                diem_chu = "F"

            result = f"{tong_ket} · {diem_chu}"
            if ck < 1:
                result = result + " (điểm thi dưới 1)"

    return render_template("diem_hoc_phan.html", values=values,
                           errors=errors, result=result)
