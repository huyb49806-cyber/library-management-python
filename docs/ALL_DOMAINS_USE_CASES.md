# Use cases toàn hệ thống

## Domain 1: Quản lý tài nguyên sách

- **UC1.1 Xem danh sách sách**: Guest, Member, Librarian, Admin xem danh sách và tra cứu sách.
- **UC1.2 Xem chi tiết sách và tình trạng kho**: các vai trò xem thông tin đầu sách và số bản sao đang có thể mượn.
- **UC1.3 Xem danh sách và chi tiết tác giả**: các vai trò xem tác giả và các sách liên quan.
- **UC1.4 Quản lý sách**: Admin thêm, sửa, xóa đầu sách.
- **UC1.5 Quản lý tác giả và thể loại**: Admin thêm, sửa, xóa tác giả và thể loại.
- **UC1.6 Quản lý bản sao vật lý**: Admin thêm bản sao, mã UUID/barcode và trạng thái bản sao.

Các thao tác nhập kho, xuất kho, thanh lý và in barcode chỉ được triển khai khi được mô tả trong flow/UC chính thức; trong baseline hiện tại, phần dữ liệu nằm ở `BookInstance`.

## Domain 2: Quản lý người dùng

- **UC2.1 Đăng nhập hệ thống**: Guest gọi API login và nhận JWT.
- **UC2.2 Đăng xuất**: Member, Librarian, Admin gọi API logout để thu hồi refresh token.
- **UC2.3 Khôi phục mật khẩu**: Guest gọi API password reset.
- **UC2.5 Quản lý tài khoản người dùng**: Admin gọi API quản lý user và Group/Permission.

`UC2.4` đăng ký công khai không nằm trong baseline MDN. `UserProfile` chỉ lưu thông tin cá nhân nếu giao diện profile được yêu cầu.

## Domain 3: Lưu thông và mượn trả

- **UC3.1 Xem sách cá nhân đang mượn**: Member xem các loan của mình và cảnh báo quá hạn dựa trên `due_date`.
- **UC3.2 Xem toàn bộ sách đang được mượn**: Librarian, Admin xem các loan đang mở.
- **UC3.3 Lập phiếu mượn sách**: Librarian xác định user, quét/chọn `BookInstance`, tạo `Loan` và chuyển bản sao sang `on_loan`.
- **UC3.4 Gia hạn sách**: Librarian cập nhật `due_date` cho phiếu mượn hợp lệ.
- **UC3.5 Ghi nhận trả sách**: Librarian ghi nhận trả, cập nhật `returned_date`, đóng `Loan` và chuyển bản sao về `available`.

Phạt, hỏng sách, từ chối gia hạn và cronjob cảnh báo chỉ được thêm sau khi các flow tương ứng xuất hiện trong tài liệu nghiệp vụ chính thức; chúng chưa được thêm vào baseline UC này.
