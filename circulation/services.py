from datetime import date, timedelta

from django.db import transaction
from catalog.models import BookInstance


def is_staff_operator(user):
    return user.is_staff or user.groups.filter(name__in=["Librarian", "Admin"]).exists()


def as_payload(instance):
    book = getattr(instance, "book", None)
    borrower = getattr(instance, "borrower", None)
    return {
        "id": str(instance.pk),
        "book_id": str(instance.book_id) if instance.book_id else None,
        "book_title": book.title if book else "",
        "borrower_id": str(instance.borrower_id) if instance.borrower_id else None,
        "borrower_name": borrower.username if borrower else "",
        "status": instance.status,
        "due_back": instance.due_back,
        "is_overdue": bool(instance.due_back and date.today() > instance.due_back),
    }


def borrow(book_instance_id, member):
    book_instance_id = str(book_instance_id).strip()
    with transaction.atomic():
        instance = BookInstance.objects.select_for_update().get(pk=book_instance_id)
        if instance.status != BookInstance.AVAILABLE:
            raise ValueError("Bản sao sách hiện không có sẵn để mượn.")
        instance.status = BookInstance.ON_LOAN
        instance.borrower = member
        instance.due_back = date.today() + timedelta(days=21)
        instance.save(update_fields=["status", "borrower", "due_back"])
    return instance


def renew(book_instance_id, new_due_back):
    book_instance_id = str(book_instance_id).strip()
    with transaction.atomic():
        instance = BookInstance.objects.select_for_update().get(pk=book_instance_id)
        if instance.borrower_id is None or instance.status != BookInstance.ON_LOAN:
            raise ValueError("Bản sao sách chưa được mượn bởi độc giả nào.")
        if instance.due_back and new_due_back <= instance.due_back:
            raise ValueError("Hạn trả mới phải sau ngày hẹn trả hiện tại.")
        instance.due_back = new_due_back
        instance.save(update_fields=["due_back"])
    return instance


def return_book(book_instance_id):
    book_instance_id = str(book_instance_id).strip()
    with transaction.atomic():
        instance = BookInstance.objects.select_for_update().get(pk=book_instance_id)
        if instance.borrower_id is None or instance.status != BookInstance.ON_LOAN:
            raise ValueError("Bản sao sách không ở trạng thái đang mượn.")
        instance.borrower = None
        instance.due_back = None
        instance.status = BookInstance.AVAILABLE
        instance.save(update_fields=["borrower", "due_back", "status"])
    return instance
