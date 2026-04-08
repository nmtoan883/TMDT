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

Do hệ thống đã kết nối hoàn chỉnh với Cloud Postgresql qua Supabase, anh em trong Team **không cần xài XAMPP** hay gõ lệnh Nạp Dữ Liệu (`loaddata`). Chỉ cần làm theo 3 bước sau:

### Bước 1: Kéo Code về máy
```bash
git clone https://github.com/nmtoan883/TMDT.git
cd TMDT
```

### Bước 2: Cài đặt thư viện
Yêu cầu đã cài đặt Python (3.10 trở lên). Cài đặt toàn bộ môi trường:
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình Database Cloud (Secret .env)
Mọi dữ liệu của dự án đều dùng chung trên hệ thống máy chủ Cloud, tuy nhiên đường dẫn kết nối đã được ẩn đi vì lý do bảo mật. 
1. Cần phải có đoạn mã kết nối `DATABASE_URL` (bạn có thể xin từ các thành viên khác trong dự án).
2. Tạo 1 file tên là `.env` (có dấu chấm ở đầu) nằm cùng vị trí với file `manage.py`.
3. Dán đoạn mã đã nhận vào file đó. (Ví dụ: `DATABASE_URL=postgresql://...`)

### Bước 4: Chạy Server
Sau khi có `.env`, anh em thả nhẹ lệnh khởi động:
```bash
python manage.py runserver
```
Truy cập vào trang bằng đường link: `http://127.0.0.1:8000/`. Mọi thay đổi về dữ liệu do 1 người thêm sẽ có hiệu lực trên máy toàn nhóm.

---

## 📦 Deploy Production

Hệ thống đã trải qua quá trình Build hoàn chỉnh qua lệnh:
```bash
python manage.py collectstatic --noinput
```
(Lệnh này dùng khi chuẩn bị đẩy hệ thống lên Server ảo như Render, Vercel, AWS v.v...). Các Cấu hình Database và Gunicorn đã sẵn sàng. Thư mục `staticfiles` sẽ tự động đóng gói vận chuyển.

> **Team Development:** Cám ơn toàn bộ các thành viên vì những cống hiến để tạo nên sản phẩm tuyệt vời này! 🚀
