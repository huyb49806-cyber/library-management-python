# Domain 2 use cases (MDN-aligned)

## Included

- **UC2.1 Đăng nhập hệ thống**: Guest gọi API login và nhận JWT.
- **UC2.2 Đăng xuất**: Member, Librarian, Admin gọi API logout để thu hồi refresh token.
- **UC2.3 Khôi phục mật khẩu**: Guest gọi API password reset.
- **UC2.5 Quản lý tài khoản người dùng**: Admin gọi API quản lý user và Group/Permission.

## Removed from this baseline

- UC2.4 đăng ký công khai, OAuth, profile notification và audit nghiệp vụ riêng: chưa có trong GitHub mẫu và không thêm vào baseline.

## Optional profile

Nếu bài yêu cầu trang cá nhân, `UserProfile` bổ sung mã sinh viên, số điện thoại và ngày sinh. Đây là phần mở rộng dữ liệu, không tạo thêm luồng xác thực mới.
