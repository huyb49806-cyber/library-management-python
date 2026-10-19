import uuid

from django.conf import settings
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.RESTRICT, related_name="books")
    summary = models.TextField(blank=True)
    isbn = models.CharField("ISBN", max_length=13, unique=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name="books")
    language = models.ForeignKey(Language, on_delete=models.RESTRICT, related_name="books")

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title

    @property
    def available_copies(self):
        return self.instances.filter(status=BookInstance.AVAILABLE).count()

    @property
    def total_copies(self):
        return self.instances.count()


class BookInstance(models.Model):
    AVAILABLE = "a"
    ON_LOAN = "o"
    MAINTENANCE = "d"
    RESERVED = "r"
    STATUS_CHOICES = ((AVAILABLE, "Available"), (ON_LOAN, "On loan"), (MAINTENANCE, "Maintenance"), (RESERVED, "Reserved"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, related_name="instances")
    imprint = models.CharField(max_length=200, blank=True)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="borrowed_book_instances")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=AVAILABLE)

    class Meta:
        ordering = ("book__title", "id")

    def __str__(self):
        return f"{self.book.title} ({self.id})"

    @property
    def is_overdue(self):
        from datetime import date
        return bool(self.due_back and date.today() > self.due_back)

    @property
    def can_mark_returned(self):
        return self.status == self.ON_LOAN and self.borrower_id is not None
