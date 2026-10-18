# Domain 2 database (MDN-aligned)

Domain 2 follows the MDN Local Library tutorial and uses Django's built-in authentication instead of creating a custom authentication schema.

## Tables

### Django tables created by `migrate`

| Table | Purpose |
| --- | --- |
| `auth_user` | Login account, password hash, active/staff flags |
| `auth_group` | Roles such as Member, Librarian, Admin |
| `auth_permission` | Fine-grained Django permissions |
| `auth_user_groups` | User-to-role membership |
| `auth_group_permissions` | Role-to-permission membership |
| `auth_user_user_permissions` | Optional direct user permissions |
| `django_session` | Browser session login/logout |
| `django_content_type` | Django permission metadata |
| `django_admin_log` | Actions performed in Django Admin |

### Project table

| Table | Purpose |
| --- | --- |
| `user_profiles` | Optional student profile extension: student code, phone, date of birth |

Catalog tables remain in Domain 1 (`Book`, `Author`, `Genre`, `Language`, `BookInstance`). Circulation tables remain in Domain 3. Those domains reference `auth_user.id` as borrower, librarian, or administrator.

## Why this is the correct scope

The MDN sample already provides login, logout, password hashing, password reset, user administration, groups and permissions. The API uses JWT as a transport credential for React, but does not create custom role/session/token tables; refresh-token revocation uses the standard SimpleJWT blacklist migrations.
