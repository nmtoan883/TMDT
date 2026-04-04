import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import Category, Post


def run():
    categories = {
        'Smartphone': Category.objects.get_or_create(name='Smartphone')[0],
        'Laptop': Category.objects.get_or_create(name='Laptop')[0],
        'AI': Category.objects.get_or_create(name='AI')[0],
        'Phụ kiện': Category.objects.get_or_create(name='Phụ kiện')[0],
        'Thủ thuật': Category.objects.get_or_create(name='Thủ thuật')[0],
    }

    posts = [
        {
            'category': categories['Smartphone'],
            'title': 'iPhone 15 Pro Max có gì đáng chú ý trong năm nay?',
            'summary': 'Đánh giá nhanh thiết kế, camera, hiệu năng và trải nghiệm thực tế của iPhone 15 Pro Max.',
            'content': 'iPhone 15 Pro Max tiếp tục là mẫu điện thoại cao cấp được quan tâm nhờ hiệu năng mạnh, camera tốt và thời lượng pin ổn định. Thiết bị phù hợp với người dùng thích trải nghiệm mượt mà và hệ sinh thái Apple...',
            'author': 'Admin',
            'is_featured': True,
        },
        {
            'category': categories['Smartphone'],
            'title': 'Samsung Galaxy S24 Ultra có thực sự đáng mua?',
            'summary': 'Mẫu flagship Android nổi bật với bút S Pen và camera zoom mạnh mẽ.',
            'content': 'Galaxy S24 Ultra hướng đến người dùng cần một thiết bị mạnh cho công việc và giải trí. Màn hình lớn, hiệu năng cao và khả năng zoom là những điểm mạnh nổi bật...',
            'author': 'Admin',
        },
        {
            'category': categories['Laptop'],
            'title': 'Top 5 laptop tốt cho sinh viên công nghệ thông tin',
            'summary': 'Gợi ý các mẫu laptop học lập trình, làm đồ án và chạy máy ảo ổn định.',
            'content': 'Sinh viên CNTT nên ưu tiên laptop có RAM từ 16GB, SSD tốc độ cao và CPU đủ mạnh để lập trình web, mobile hay AI cơ bản...',
            'author': 'Admin',
        },
        {
            'category': categories['AI'],
            'title': 'AI đang thay đổi thương mại điện tử như thế nào?',
            'summary': 'AI hỗ trợ cá nhân hóa trải nghiệm mua sắm và tăng hiệu quả vận hành.',
            'content': 'Trong thương mại điện tử, AI giúp gợi ý sản phẩm, chatbot tự động, phân tích hành vi người dùng và tối ưu chuyển đổi bán hàng...',
            'author': 'Admin',
        },
        {
            'category': categories['Phụ kiện'],
            'title': '5 mẫu tai nghe bluetooth đáng mua trong tầm giá tốt',
            'summary': 'Tổng hợp tai nghe phù hợp cho học tập, làm việc và giải trí.',
            'content': 'Khi chọn tai nghe bluetooth, người dùng nên quan tâm tới chất âm, thời lượng pin, độ trễ và khả năng chống ồn...',
            'author': 'Admin',
        },
        {
            'category': categories['Thủ thuật'],
            'title': 'Cách tăng tốc laptop Windows sau thời gian dài sử dụng',
            'summary': 'Một số mẹo đơn giản giúp máy chạy mượt và ổn định hơn.',
            'content': 'Người dùng nên dọn rác hệ thống, tắt ứng dụng khởi động cùng Windows, cập nhật driver và kiểm tra dung lượng ổ cứng định kỳ...',
            'author': 'Admin',
        },
        {
            'category': categories['Laptop'],
            'title': 'MacBook hay laptop Windows: đâu là lựa chọn tốt hơn?',
            'summary': 'So sánh theo nhu cầu học tập, thiết kế và lập trình.',
            'content': 'MacBook phù hợp với người thích sự ổn định và tối ưu pin, trong khi laptop Windows linh hoạt hơn về giá và lựa chọn cấu hình...',
            'author': 'Admin',
        },
        {
            'category': categories['AI'],
            'title': 'Xu hướng AI năm nay mà sinh viên công nghệ nên biết',
            'summary': 'Các xu hướng nổi bật về trợ lý AI, tạo nội dung và tự động hóa.',
            'content': 'AI đang tiến nhanh trong các lĩnh vực tạo sinh nội dung, học máy ứng dụng và công cụ hỗ trợ lập trình. Sinh viên nên sớm tiếp cận các nền tảng phổ biến...',
            'author': 'Admin',
        },
    ]

    for item in posts:
        Post.objects.get_or_create(
            title=item['title'],
            defaults=item
        )

    print("Seed blog thành công.")


if __name__ == '__main__':
    run()