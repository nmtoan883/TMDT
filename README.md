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

#### Phương án B: Quy trình làm việc Offline (Sử dụng tệp JSON)
Dành cho trường hợp đứt mạng Supabase hoặc nhóm thống nhất code trên máy tính của mỗi người (Local). Khi đó, ta sẽ sử dụng file `tmdt_data.json` để chia sẻ dữ liệu với nhau.

**🔹 Dành cho người nhận (Muốn NẠP cơ sở dữ liệu để test máy bạn)**
Khi bạn mới tải code về hoặc nhận được thông báo có file JSON nâng cấp từ đồng đội, hãy làm như sau:
1. (Tùy chọn) Bật XAMPP MySQL. Nếu lười, Django mặc định tự xài tệp `dev.sqlite3` siêu gọn nhẹ.
2. Ép hệ thống tạo bộ khung Database bằng lệnh:
   ```bash
   python manage.py migrate
   ```
3. Nạp 100% Dữ Liệu (Nick admin, sản phẩm, tin tức... lấy từ dự án gốc) vào máy bạn:
   ```bash
   python manage.py flush
   python manage.py loaddata tmdt_data.json
   ```
*(Lưu ý: Lệnh `flush` sẽ hỏi bạn có chắc muốn dọn sạch DB hiện tại không, hãy bấm `yes`. Việc này giúp rửa sạch các rác cũ và tránh báo lỗi "trùng ID Sản phẩm" khi nạp file đè lên).*

**🔸 Dành cho người thiết kế (Muốn XUẤT cơ sở dữ liệu để xách đi chia sẻ)**
Nếu bạn là người vừa thao tác thêm cả đống Sản phẩm mới, Danh mục mới trong Admin và muốn toàn đội ai cũng có bộ Data này. Đừng gửi bảng SQL, hãy xuất bằng JSON quy chuẩn của Django:
1. Chạy lệnh Dump Data đa hệ (đã loại bỏ rác hệ thống để tránh xung đột quyền):
   ```bash
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes -e sessions > tmdt_data.json
   ```
2. Mở Git Desktop hoặc xài lệnh terminal để Commit file `.json` đó và Push lên Github. Xong! Các anh em ở trên F5 lấy code về nạp bằng lệnh `loaddata` là ngon ngay.

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
