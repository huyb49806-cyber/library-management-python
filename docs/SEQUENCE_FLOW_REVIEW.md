# Review tài liệu Drive

## Kết quả đọc được

### ERD trong file `Lược đồ csdl.drawio`

ERD hiện có các bảng:

- `USERS`: `id`, `username`, `email`, `password_hash`, `role`, `created_at`.
- `AUTHORS`: thông tin tác giả.
- `BOOKS`: đầu sách, ISBN, mô tả và `author_id`.
- `GENRES`: thể loại.
- `BOOK_GENRES`: bảng nối nhiều-nhiều giữa sách và thể loại.
- `BOOK_INSTANCES`: bản sao vật lý, `imprint`, `status`, `due_back`, `book_id`, `borrower_id`.

### Sequence flow trong file `Biểu đồ luồng dữ liệu và tuần tự.drawio`

Các flow hiện có gồm:

- Tra cứu danh sách/chi tiết sách và tác giả.
- Tạo sách, xóa tác giả, tạo bản sao vật lý và tự sinh UUID barcode.
- Đăng nhập bằng username/password, tạo JWT.
- Quên mật khẩu, tạo reset token thời hạn 15 phút.
- Đăng ký, hash mật khẩu bằng bcrypt, gán role mặc định `MEMBER`.
- Đổi role user sang `LIBRARIAN`.
- Member xem sách đang mượn và kiểm tra overdue.
- Librarian/Admin xem toàn bộ sách đang mượn.
- Librarian mượn sách: kiểm tra `Available`, gán `On loan`, gán `borrower_id`, đặt `due_back = hôm nay + 21 ngày`.
- Librarian gia hạn: chỉ nhận ngày mới lớn hơn ngày cũ, sau đó cập nhật `due_back`.
- Librarian trả sách: xóa `borrower_id`, xóa `due_back`, đổi status về `Available`.

## Kết luận

Sequence flow của nhóm **đúng và nhất quán với ERD hiện tại**. Đặc biệt, flow mượn/trả đang bám sát cách MDN triển khai `BookInstance`: trạng thái, người mượn và hạn trả nằm trực tiếp trên bản sao vật lý. Không cần thêm bảng `Loan` nếu nhóm giữ nguyên flow này.

Tuy nhiên, sequence flow hiện tại **không hoàn toàn giống MDN nguyên bản** ở ba điểm: nhóm có bảng `USERS` riêng thay vì Django `auth_user`, dùng JWT/custom reset token thay vì Django session/password-reset flow, và có đăng ký/đổi role. Đây là khác biệt kiến trúc hiện có của nhóm, không phải lỗi logic.

## Những gì phải thống nhất trước khi code

1. Nếu ưu tiên **giữ nguyên flow hiện tại**, giữ UC2.1–UC2.5, bảng `USERS`, JWT, reset token và không tạo `Loan`.
2. Nếu ưu tiên **bám tuyệt đối MDN**, bỏ đăng ký/JWT/reset token custom/đổi role custom và chuyển sang `auth_user`, Group, session của Django.

Hai hướng trên không nên trộn lẫn trong cùng một baseline vì sẽ tạo hai nguồn sự thật cho user, role và authentication.
