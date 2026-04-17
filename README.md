# 🛒 Electro E-Commerce - Dự án Thương Mại Điện Tử

Dự án phát triển nền tảng Website Thương Mại Điện Tử chuyên nghiệp sử dụng công nghệ Python (Django Framework) và giao diện Electro hiện đại.

## 🌟 Tính Năng Nổi Bật

- **🛍 Giao diện Chuẩn E-Commerce:** Giao diện Electro bản quyền với thiết kế tối ưu hóa trải nghiệm người dùng (UX/UI).
- **🛒 Quản lý Giỏ hàng (Cart) & Đặt hàng (Checkout):** Hệ thống thêm vào giỏ, điều chỉnh số lượng và trừ hàng tồn kho real-time tự động.
- **❤️ Danh sách Yêu thích (Wishlist):** Lưu trữ các sản phẩm mong muốn.
- **🎁 Khuyến Mãi (Coupon):** Quản lý mã giảm giá đa dạng.
- **⚙️ Quản trị Admin Dashboard:** Bảng điều khiển riêng cho chủ Shop phân tích và quản lý Sản phẩm, Bài viết.
- **🌩️ Cloud Database (Supabase PostgreSQL):** Dữ liệu được quản trị Tập Trung chuyên nghiệp trên đám mây, các thành viên Cập Nhật Thời Gian Thực (Real-time).
- **📝 Hệ thống Blog & Liên hệ (Contact):** Nơi cập nhật tin tức công nghệ và hỗ trợ người tiêu dùng.
- **⚡ Tối ưu Production:** Tích hợp `Whitenoise` xử lý tĩnh tự động và gỡ lỗi Database tối ưu.

## 🛠️ Công Nghệ Sử Dụng

- **Backend:** Python + Django 4.2 LTS (Ổn định, bảo vệ sự cố MariaDB XAMPP).
- **Database:** PostgreSQL (Supabase Cloud).
- **Giao diện:** HTML5, CSS3, Bootstrap, Javascript (Theme: Electro).
- **Deployment:** Cấu hình Production-ready (Gunicorn, Whitenoise, dj-database-url).

---

## 🚀 Hướng Dẫn Cài Đặt Dành Cho Team

Dự án hỗ trợ 2 môi trường làm việc: Đồng bộ với Cloud (Khuyên dùng) hoặc Chạy Local Offline bằng file chia sẻ.

### Bước 1: Kéo Code và cài đặt môi trường
Đảm bảo bạn đã cài đặt Python (3.10 trở lên).
```bash
git clone https://github.com/nmtoan883/TMDT.git
cd TMDT
pip install -r requirements.txt
```

### Bước 2: Thiết lập Database (Chọn 1 trong 2 phương án)

#### Phương án A: Dùng chung Cloud Database Supabase (Khuyên dùng)
Dữ liệu được cập nhật Real-time. Người này thêm sản phẩm thì người kia F5 là thấy ngay.
1. Không cần bật XAMPP.
2. Tạo 1 file tên là `.env` (có dấu chấm ở đầu) nằm ngay cạnh file `manage.py`.
3. Xin đoạn mã kết nối `DATABASE_URL=postgresql://...` từ các thành viên khác và dán vào file `.env`.
4. Xong! Không cần gõ lệnh nạp dữ liệu gì thêm.

#### Phương án B: Dùng Offline Local Database (Thông qua tệp JSON)
Dành cho ai muốn chạy độc lập không phụ thuộc mạng, hoặc làm việc chia nhỏ nhóm.
1. (Tùy chọn) Bật XAMPP MySQL. Nếu không bật, Django mặc định sẽ tự xài SQLite siêu nhẹ.
2. Nạp cấu trúc Database:
   ```bash
   python manage.py migrate
   ```
3. Nạp Data Seed (100% dữ liệu: Nick admin, sản phẩm, tin tức... lấy từ dự án gốc):
   ```bash
   python manage.py loaddata tmdt_data.json
   ```
*(🌟 Mẹo: Bất kì khi nào bạn tải code mới về và thấy có file `tmdt_data.json` cập nhật, hãy chạy `python manage.py flush` -> Nhập "yes" để rửa sạch DB máy bạn, rồi thả lại lệnh loaddata ở trên để dữ liệu mới nhất được tái tạo chuẩn 100%)*

### Bước 3: Chạy Server
Sau khi thiết lập xong DB:
```bash
python manage.py runserver
```
▶️ Truy cập link: `http://127.0.0.1:8000/`
🔑 Tài khoản Admin (nếu dùng chung Cloud hoặc load JSON): **User:** `admin` | **Pass:** `admin123`

---

## 📦 Deploy Production

Hệ thống đã trải qua quá trình Build hoàn chỉnh qua lệnh:
```bash
python manage.py collectstatic --noinput
```
(Lệnh này dùng khi chuẩn bị đẩy hệ thống lên Server ảo như Render, Vercel, AWS v.v...). Các Cấu hình Database và Gunicorn đã sẵn sàng. Thư mục `staticfiles` sẽ tự động đóng gói vận chuyển.

> **Team Development:** Cám ơn toàn bộ các thành viên vì những cống hiến để tạo nên sản phẩm tuyệt vời này! 🚀
