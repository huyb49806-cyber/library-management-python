# Domain 2 REST API

Base URL: `/api/v1/auth/`

## Authentication

- `POST login/` body `{ "username": "...", "password": "..." }` returns `access` and `refresh` JWTs.
- `POST refresh/` body `{ "refresh": "..." }` returns a new access token.
- `POST logout/` with Bearer access token and body `{ "refresh": "..." }` blacklists the refresh token.

## Current user

- `GET me/` returns the authenticated user, groups and profile.
- `PATCH me/` updates `email`, `first_name`, `last_name` and profile fields.

## Password recovery

- `POST password-reset/` body `{ "email": "..." }`; the reset email is printed to the local backend console.
- `POST password-reset/confirm/` body `{ "uid": "...", "token": "...", "new_password": "..." }`.

## Admin user management

Requires an authenticated Django staff user.

- `GET/POST admin/users/`
- `GET/PATCH/DELETE admin/users/<id>/`

Groups are assigned by sending group names such as `Member`, `Librarian`, or `Admin` in the `groups` field. The groups must first exist in Django Admin.
