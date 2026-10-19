from datetime import date, timedelta

from django.apps import apps
from django.db import transaction


class CatalogContractError(RuntimeError):
    pass


BOOK_MODEL_LABELS = ("catalog.BookInstance", "books.BookCopy", "domains.books.BookCopy")


def get_book_model():
    for label in BOOK_MODEL_LABELS:
        app_label, model_name = label.split(".")
        try:
            return apps.get_model(app_label, model_name)
        except LookupError:
            continue
    raise CatalogContractError("A catalog BookInstance/BookCopy model is not installed")


def require_circulation_contract(model):
    fields = {field.name for field in model._meta.get_fields()}
    missing = {"id", "status", "due_back", "borrower"} - fields
    if missing:
        raise CatalogContractError(
            f"Catalog model {model._meta.label} is missing circulation fields: {', '.join(sorted(missing))}"
        )


def status_value(model, semantic):
    choices = dict(model._meta.get_field("status").choices or [])
    aliases = {"available": ("a", "Available", "available"), "on_loan": ("o", "On loan", "on_loan")}
    for candidate in aliases[semantic]:
        if candidate in choices:
            return candidate
        if candidate in choices.values():
            return next(key for key, value in choices.items() if value == candidate)
    return aliases[semantic][0]


def is_staff_operator(user):
    return user.is_staff or user.groups.filter(name__in=["Librarian", "Admin"]).exists()


def as_payload(instance):
    return {
        "id": str(instance.pk),
        "book_id": str(instance.book_id) if instance.book_id else None,
        "borrower_id": str(instance.borrower_id) if instance.borrower_id else None,
        "status": instance.status,
        "due_back": instance.due_back,
        "is_overdue": bool(instance.due_back and date.today() > instance.due_back),
    }


def borrow(book_instance_id, member):
    model = get_book_model()
    require_circulation_contract(model)
    with transaction.atomic():
        instance = model.objects.select_for_update().get(pk=book_instance_id)
        if instance.status != status_value(model, "available"):
            raise ValueError("Book instance is not available")
        instance.status = status_value(model, "on_loan")
        instance.borrower = member
        instance.due_back = date.today() + timedelta(days=21)
        instance.save(update_fields=["status", "borrower", "due_back"])
    return instance


def renew(book_instance_id, new_due_back):
    model = get_book_model()
    require_circulation_contract(model)
    with transaction.atomic():
        instance = model.objects.select_for_update().get(pk=book_instance_id)
        if instance.borrower_id is None or instance.status != status_value(model, "on_loan"):
            raise ValueError("Book instance has no borrower")
        if instance.due_back and new_due_back <= instance.due_back:
            raise ValueError("New due date must be later than the current due date")
        instance.due_back = new_due_back
        instance.save(update_fields=["due_back"])
    return instance


def return_book(book_instance_id):
    model = get_book_model()
    require_circulation_contract(model)
    with transaction.atomic():
        instance = model.objects.select_for_update().get(pk=book_instance_id)
        if instance.borrower_id is None or instance.status != status_value(model, "on_loan"):
            raise ValueError("Book instance has no borrower")
        instance.borrower = None
        instance.due_back = None
        instance.status = status_value(model, "available")
        instance.save(update_fields=["borrower", "due_back", "status"])
    return instance
