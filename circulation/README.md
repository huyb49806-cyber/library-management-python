# Domain 3: Circulation

The API operates on the catalog's MDN `BookInstance` contract: `borrower`, `status` and `due_back` live on the physical copy. It also recognizes the teammate branch's `BookCopy` label once that model is made compatible.

Endpoints:

- `GET /api/v1/circulation/loans/`
- `POST /api/v1/circulation/loans/borrow/`
- `PATCH /api/v1/circulation/loans/<book-instance-uuid>/renew/`
- `POST /api/v1/circulation/loans/<book-instance-uuid>/return/`

No separate `Loan` table is introduced, matching the MDN flow.
