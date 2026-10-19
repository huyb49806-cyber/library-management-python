# Catalog REST API

Base URL: `/api/v1/catalog/`

Read operations are available to Guest, Member, Librarian and Admin. Create, update and delete operations require an Admin JWT.

## Resources

```text
GET|POST         /authors/
GET|PATCH|DELETE /authors/<id>/
GET|POST         /genres/
GET|PATCH|DELETE /genres/<id>/
GET|POST         /languages/
GET|PATCH|DELETE /languages/<id>/
GET|POST         /books/
GET|PATCH|DELETE /books/<id>/
GET|POST         /book-instances/
GET|PATCH|DELETE /book-instances/<uuid>/
```

`GET /books/` supports `?search=` against title, ISBN and author name. A book response includes `author_detail`, `language_detail`, `genre_details`, `total_copies` and `available_copies`.

Book instance statuses follow the MDN model:

```text
a = Available
o = On loan
d = Maintenance
r = Reserved
```

`BookInstance` keeps the UUID barcode, borrower, due date and status so it matches the existing Circulation contract.
