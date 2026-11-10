# Ứng dụng quản lý sách

Ứng dụng web Flask quản lý **danh mục sách** và **sách** theo từng danh mục, lưu bằng CSDL SQLite.
Trang Dashboard tổng hợp số liệu: số danh mục, số đầu sách, tổng số cuốn, sách đã hết và tỉ lệ sách theo danh mục.

- **Sinh viên:** Nguyễn Văn Quân
- **Học phần:** Phần mềm Mã nguồn mở – Trường Đại học Khoa học, Đại học Huế

## 1. Chức năng

- **CRUD danh mục:** thêm, xem, sửa, xoá. Tên danh mục không được trùng. Không xoá được danh mục còn sách.
- **CRUD sách theo danh mục:** thêm, xem, sửa, xoá. Lọc danh sách theo danh mục (`/books?category_id=…`). Thêm sách từ trang danh mục thì danh mục được chọn sẵn.
- **Dashboard:** 4 ô thống kê, bảng số sách theo từng danh mục (kể cả danh mục 0 sách) có thanh tỉ lệ, 5 sách mới thêm, các nút thêm nhanh.
- **CSDL SQLite** qua Flask-SQLAlchemy. Có lệnh CLI để tạo dữ liệu mẫu.

## 2. Công nghệ và giấy phép

Giấy phép lấy từ file `METADATA` và `LICENSE` của từng gói trong `.venv` (không ghi theo trí nhớ):

| Thư viện | Phiên bản | Vai trò | Giấy phép |
|---|---|---|---|
| Flask | 3.1.3 | Web framework | BSD-3-Clause |
| Flask-SQLAlchemy | 3.1.1 | Tích hợp SQLAlchemy vào Flask | BSD-3-Clause |
| SQLAlchemy | 2.1.8 | ORM, sinh câu SQL | MIT |
| Flask-WTF | 1.3.0 | Form và CSRF token | BSD-3-Clause |
| WTForms | 3.3.2 | Khai báo form, kiểm tra dữ liệu | BSD-3-Clause |
| Jinja2 | 3.1.6 | Template HTML | BSD-3-Clause |

Các gói phụ thuộc còn lại trong `requirements.txt` (Werkzeug, MarkupSafe, itsdangerous, click) dùng BSD-3-Clause, riêng blinker dùng MIT.

**Kết luận:** Toàn bộ thư viện dùng giấy phép dễ dãi (permissive: BSD-3-Clause, MIT). Các giấy phép này tương thích với giấy phép MIT của kho. Khi phân phối lại chỉ cần giữ thông báo bản quyền của từng thư viện.

Giao diện dùng CSS tự viết (`static/css/style.css`), không dùng thư viện CSS ngoài.

## 3. Cài đặt và chạy

Yêu cầu: Python 3.13 và Git.

### Windows (PowerShell)

```powershell
git clone https://github.com/NguyenVanQuan05/pmnm-hocphan.git
cd pmnm-hocphan\chuong_06\quan_ly_sach

python -m venv .venv
.\.venv\Scripts\Activate.ps1
# Nếu bị chặn chạy script, chạy dòng dưới rồi Activate lại:
# Set-ExecutionPolicy -Scope Process Bypass

python -m pip install -r requirements.txt
python -m flask --app app seed
python -m flask --app app run --debug
```

### macOS / Linux

```bash
git clone https://github.com/NguyenVanQuan05/pmnm-hocphan.git
cd pmnm-hocphan/chuong_06/quan_ly_sach

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
python -m flask --app app seed
python -m flask --app app run --debug
```

Mở trình duyệt tại <http://127.0.0.1:5000>.

- Lệnh `seed` tạo 3 danh mục và 8 sách. Chạy lại khi đã có dữ liệu thì lệnh tự bỏ qua.
- Muốn làm lại từ đầu: xoá file `instance/library.db` rồi chạy lại `seed`.
- Luôn dùng `python -m pip` và `python -m flask`, vì một số máy Windows chặn chạy trực tiếp `pip.exe` và `flask.exe`.
- Khi triển khai thật, đặt biến môi trường `SECRET_KEY`. Giá trị có sẵn trong code chỉ dùng khi phát triển.

## 4. Các route

| URL | Method | Chức năng |
|---|---|---|
| `/` | GET | Dashboard |
| `/categories` | GET | Danh sách danh mục |
| `/categories/new` | GET, POST | Thêm danh mục |
| `/categories/<id>` | GET | Chi tiết danh mục và sách thuộc danh mục |
| `/categories/<id>/edit` | GET, POST | Sửa danh mục |
| `/categories/<id>/delete` | POST | Xoá danh mục (chỉ khi không còn sách) |
| `/books` | GET | Danh sách sách, lọc bằng `?category_id=<id>` |
| `/books/new` | GET, POST | Thêm sách (`?category_id=<id>` để chọn sẵn danh mục) |
| `/books/<id>` | GET | Chi tiết sách |
| `/books/<id>/edit` | GET, POST | Sửa sách |
| `/books/<id>/delete` | POST | Xoá sách |

## 5. Cấu trúc thư mục

```
quan_ly_sach/
├── app.py              # Tạo app, cấu hình, các route, lệnh CLI seed
├── models.py           # db, model Category và Book
├── forms.py            # CategoryForm, BookForm, DeleteForm
├── requirements.txt
├── static/css/style.css
├── templates/
│   ├── base.html       # Khung chung: menu, flash, footer
│   ├── _navbar.html    # Menu, đánh dấu trang hiện tại bằng is_active()
│   ├── _macros.html    # Macro render_field
│   ├── 404.html
│   ├── dashboard.html
│   ├── categories/     # list.html, detail.html, form.html
│   └── books/          # list.html, detail.html, form.html
└── instance/library.db # CSDL SQLite, tạo tự động, không commit
```

## 6. Ghi chú thiết kế

- **Xoá chỉ bằng POST và có CSRF token.** Nút Xoá là một `<form method="post">` có `form.hidden_tag()` và hỏi lại bằng `confirm()`. Gọi URL xoá bằng GET sẽ nhận lỗi 405.
- **Không xoá danh mục còn sách.** View kiểm tra rồi báo lỗi bằng flash. Việc kiểm tra này bắt buộc vì SQLite mặc định **không** tự kiểm tra khoá ngoại (`PRAGMA foreign_keys` tắt).
- **Kiểm tra dữ liệu bằng form.** Tên danh mục trùng được báo ngay trên form (`validate_name`), không để xảy ra `IntegrityError`. Mọi thông báo lỗi đều bằng tiếng Việt.
- **Post/Redirect/Get.** Sau khi lưu thành công: `flash` rồi `redirect`, nên F5 không gửi lại form.
- **Dữ liệu mẫu bằng lệnh CLI** (`flask seed`), không tạo bằng route.
- **Dashboard đếm bằng một câu truy vấn** `LEFT OUTER JOIN` và `GROUP BY` với `count(book.id)`. Danh mục 0 sách vẫn hiện và tránh được vấn đề N+1.
- **CSDL `instance/library.db` không được commit** (đã có trong `.gitignore`). Mỗi máy tự tạo bằng lệnh `seed`.

## 7. Ghi nguồn

Có tham khảo Claude Code để gợi ý code; em đã đọc hiểu, chạy thử từng chức năng và chỉnh sửa.

## 8. Giấy phép

MIT (xem [LICENSE](../../LICENSE) ở thư mục gốc kho).
