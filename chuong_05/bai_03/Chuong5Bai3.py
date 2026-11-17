from flask import Flask, render_template, request

app = Flask(__name__)


def bmi_calculator():
    height = ""
    weight = ""
    errors = {}
    result = None

    if request.method == "POST":
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")

        try:
            chieu_cao = float(height.replace(",", "."))
            if chieu_cao < 50 or chieu_cao > 250:
                errors["height"] = "Giá trị phải từ 50 đến 250."
        except ValueError:
            errors["height"] = "Vui lòng nhập một số."

        try:
            can_nang = float(weight.replace(",", "."))
            if can_nang < 10 or can_nang > 300:
                errors["weight"] = "Giá trị phải từ 10 đến 300."
        except ValueError:
            errors["weight"] = "Vui lòng nhập một số."

        if not errors:
            chieu_cao_m = chieu_cao / 100
            bmi = round(can_nang / (chieu_cao_m * chieu_cao_m), 1)

            if bmi < 18.5:
                phan_loai = "Thiếu cân"
                mau = "yellow"
            elif bmi < 23:
                phan_loai = "Bình thường"
                mau = "green"
            elif bmi < 25:
                phan_loai = "Thừa cân"
                mau = "yellow"
            else:
                phan_loai = "Béo phì"
                mau = "red"

            can_nang_min = round(18.5 * chieu_cao_m * chieu_cao_m, 1)
            can_nang_max = round(22.9 * chieu_cao_m * chieu_cao_m, 1)

            result = {
                "bmi": bmi,
                "phan_loai": phan_loai,
                "mau": mau,
                "can_nang_nen_co": f"{can_nang_min:g} – {can_nang_max:g} kg",
            }

    return render_template("bmi.html", height=height, weight=weight,
                           errors=errors, result=result)
