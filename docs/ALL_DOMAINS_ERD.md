# ERD toàn hệ thống

Sơ đồ dưới đây chia theo ba domain ở mức code và module, nhưng vẫn dùng chung một database. Các quan hệ giữa domain chỉ dùng khóa ngoại cần thiết cho những UC đã xác định.

```mermaid
erDiagram
    %% Domain 1: Book Catalog
    AUTHOR ||--o{ BOOK : writes
    LANGUAGE ||--o{ BOOK : describes
    BOOK ||--o{ BOOK_GENRE : has
    GENRE ||--o{ BOOK_GENRE : classifies
    BOOK ||--o{ BOOK_INSTANCE : has_copies

    %% Domain 2: User Management (Django auth)
    AUTH_USER ||--o| USER_PROFILE : has
    AUTH_USER }o--o{ AUTH_GROUP : belongs_to

    %% Domain 3: Circulation
    AUTH_USER ||--o{ LOAN : borrows
    AUTH_USER ||--o{ LOAN : processes
    BOOK_INSTANCE ||--o{ LOAN : appears_in

    AUTHOR {
        int id PK
        string first_name
        string last_name
        date date_of_birth
        date date_of_death
    }
    LANGUAGE {
        int id PK
        string name UK
    }
    GENRE {
        int id PK
        string name UK
    }
    BOOK {
        int id PK
        string title
        string isbn UK
        text summary
        int author_id FK
        int language_id FK
    }
    BOOK_GENRE {
        int book_id PK,FK
        int genre_id PK,FK
    }
    BOOK_INSTANCE {
        uuid id PK
        int book_id FK
        string imprint
        string barcode UK
        string status
    }
    AUTH_USER {
        int id PK
        string username UK
        string password
        boolean is_active
        boolean is_staff
    }
    AUTH_GROUP {
        int id PK
        string name UK
    }
    USER_PROFILE {
        int id PK
        int user_id UK,FK
        string student_code UK
        string phone
        date date_of_birth
    }
    LOAN {
        int id PK
        uuid book_instance_id FK
        int member_id FK
        int processed_by_id FK
        date loan_date
        date due_date
        date returned_date
        string status
    }
```

## Phạm vi từng domain

### Domain 1: `catalog`

`Author`, `Language`, `Genre`, `Book`, `BookGenre`, `BookInstance` bám theo các model của MDN. `BookInstance` đại diện cho một cuốn vật lý và chứa UUID/mã barcode cùng trạng thái `available`, `on_loan`, `maintenance` hoặc `retired`.

### Domain 2: `accounts`

`AUTH_USER`, `AUTH_GROUP`, permission và session do Django tạo. `UserProfile` là bảng mở rộng tùy chọn cho thông tin sinh viên. Không tạo hệ thống role/JWT/OAuth riêng trong baseline.

### Domain 3: `circulation`

`Loan` là phiếu mượn gắn một người dùng với một `BookInstance`. Gia hạn cập nhật `due_date`; trả sách cập nhật `returned_date`, `status` của loan và trạng thái bản sao. Không thêm bảng riêng cho các luồng chưa có trong UC.
