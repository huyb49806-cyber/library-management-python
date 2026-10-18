# Library Management

Django project organized into three domains, following the MDN Local Library tutorial.

## Domains

- `accounts/`: REST API authentication, JWT refresh/revocation, password reset and admin user management.
- `catalog/`: reserved for Domain 1; intentionally empty.
- `circulation/`: reserved for Domain 3; intentionally empty.

## Local setup

1. Create a virtual environment and install `requirements.txt`.
2. Configure `.env` from `.env.example` with the local MySQL database.
3. Run `python manage.py migrate`.
4. Run `python manage.py createsuperuser`.
5. Run `python manage.py runserver`.

The React frontend consumes `/api/v1/`. The API uses Django's built-in `auth.User`, Group and Permission models. Catalog endpoints remain reserved for the teammate branch; circulation endpoints use the MDN copy contract.

## API endpoints

- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/refresh/`
- `POST /api/v1/auth/logout/`
- `GET/PATCH /api/v1/auth/me/`
- `POST /api/v1/auth/password-reset/`
- `POST /api/v1/auth/password-reset/confirm/`
- `GET/POST /api/v1/auth/admin/users/` (admin only)
- `GET/PATCH/DELETE /api/v1/auth/admin/users/<id>/` (admin only)

## Circulation API

- `GET /api/v1/circulation/loans/`
- `POST /api/v1/circulation/loans/borrow/`
- `PATCH /api/v1/circulation/loans/<book-instance-uuid>/renew/`
- `POST /api/v1/circulation/loans/<book-instance-uuid>/return/`
