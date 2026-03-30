// E-ELECTRO - Main JavaScript File
/**
 * Script chung toàn site (tùy chỉnh thêm sau).
 * Gợi ý tìm kiếm trên navbar được xử lý trong templates/base.html.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Tự động ẩn thông báo (alerts) sau 4 giây
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });
});
