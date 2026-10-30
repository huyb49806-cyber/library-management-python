import random
import uuid
from rest_framework import serializers

from .models import Author, Book, BookInstance, Genre, Language


def generate_isbn13():
    while True:
        digits = [9, 7, 8] + [random.randint(0, 9) for _ in range(9)]
        checksum = (10 - sum(d * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits)) % 10) % 10
        isbn = "".join(map(str, digits)) + str(checksum)
        if not Book.objects.filter(isbn=isbn).exists():
            return isbn


class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name", "full_name", "date_of_birth", "date_of_death")

    def get_full_name(self, obj):
        return str(obj)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ("id", "name")


class BookInstanceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, default=uuid.uuid4)
    book_title = serializers.CharField(source="book.title", read_only=True)
    borrower_name = serializers.CharField(source="borrower.username", read_only=True, allow_null=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    can_mark_returned = serializers.BooleanField(read_only=True)

    class Meta:
        model = BookInstance
        fields = ("id", "book", "book_title", "imprint", "due_back", "borrower", "borrower_name", "status", "status_label", "is_overdue", "can_mark_returned")
        read_only_fields = ("borrower", "due_back", "is_overdue", "can_mark_returned")

    def validate(self, attrs):
        current_status = self.instance.status if self.instance else None
        requested_status = attrs.get("status", current_status)

        if self.instance is None and requested_status == BookInstance.ON_LOAN:
            raise serializers.ValidationError({
                "status": "Use the circulation API to loan a book instance."
            })

        if (
            current_status == BookInstance.ON_LOAN
            and "status" in attrs
            and requested_status != BookInstance.ON_LOAN
        ):
            raise serializers.ValidationError({
                "status": "Return the book through the circulation API first."
            })

        return attrs


class BookSerializer(serializers.ModelSerializer):
    copies = serializers.IntegerField(write_only=True, required=False, default=1, min_value=0)
    isbn = serializers.CharField(max_length=13, required=False, allow_blank=True)
    author_detail = AuthorSerializer(source="author", read_only=True)
    language_detail = LanguageSerializer(source="language", read_only=True)
    genre_details = GenreSerializer(source="genre", many=True, read_only=True)
    total_copies = serializers.SerializerMethodField()
    available_copies = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "author_detail",
            "summary",
            "isbn",
            "genre",
            "genre_details",
            "language",
            "language_detail",
            "total_copies",
            "available_copies",
            "copies",
        )

    def get_total_copies(self, obj):
        return getattr(obj, "annotated_total_copies", obj.total_copies)

    def get_available_copies(self, obj):
        return getattr(obj, "annotated_available_copies", obj.available_copies)

    def to_internal_value(self, data):
        if hasattr(data, "getlist"):
            # Xử lý QueryDict khi gửi dưới dạng form-data
            normal_data = {}
            for k in data.keys():
                vals = data.getlist(k)
                normal_data[k] = vals if len(vals) > 1 or k == "genre" else vals[0]
            data = normal_data
        else:
            data = data.copy() if hasattr(data, "copy") else dict(data)

        # 1. Tự viết tên tác giả hoặc chọn ID tác giả có sẵn
        author_val = data.get("author")
        if isinstance(author_val, str) and not author_val.isdigit():
            author_name = author_val.strip()
            if author_name:
                matched_author = None
                for a in Author.objects.all():
                    if f"{a.first_name} {a.last_name}".strip().lower() == author_name.lower():
                        matched_author = a
                        break
                if not matched_author:
                    parts = author_name.split()
                    if len(parts) == 1:
                        first_name, last_name = "", parts[0]
                    else:
                        first_name, last_name = parts[0], " ".join(parts[1:])
                    matched_author = Author.objects.create(first_name=first_name, last_name=last_name)
                data["author"] = matched_author.pk

        # 2. Tự viết tên ngôn ngữ hoặc chọn ID ngôn ngữ có sẵn
        lang_val = data.get("language")
        if isinstance(lang_val, str) and not lang_val.isdigit():
            lang_name = lang_val.strip()
            if lang_name:
                matched_lang = Language.objects.filter(name__iexact=lang_name).first()
                if not matched_lang:
                    matched_lang = Language.objects.create(name=lang_name)
                data["language"] = matched_lang.pk

        # 3. Tự động sinh mã ISBN nếu để trống
        isbn_val = str(data.get("isbn", "")).replace("-", "").replace(" ", "").strip()
        if not isbn_val:
            if self.instance and self.instance.isbn:
                data["isbn"] = self.instance.isbn
            else:
                data["isbn"] = generate_isbn13()
        else:
            data["isbn"] = isbn_val

        # 4. Tự viết hoặc chọn thể loại (hỗ trợ cả ID hoặc tên thể loại)
        genre_val = data.get("genre")
        if genre_val is not None:
            if isinstance(genre_val, list):
                raw_items = genre_val
            elif isinstance(genre_val, str):
                raw_items = [g.strip() for g in genre_val.split(",") if g.strip()]
            else:
                raw_items = [genre_val]

            resolved_genres = []
            for g in raw_items:
                if isinstance(g, int) or (isinstance(g, str) and str(g).isdigit()):
                    resolved_genres.append(int(g))
                elif isinstance(g, str) and g.strip():
                    g_name = g.strip()
                    genre_obj = Genre.objects.filter(name__iexact=g_name).first()
                    if not genre_obj:
                        genre_obj = Genre.objects.create(name=g_name)
                    resolved_genres.append(genre_obj.pk)
            data["genre"] = resolved_genres

        return super().to_internal_value(data)

    def create(self, validated_data):
        copies = validated_data.pop("copies", 1)
        book = super().create(validated_data)
        if copies > 0:
            instances = [
                BookInstance(book=book, status=BookInstance.AVAILABLE)
                for _ in range(copies)
            ]
            BookInstance.objects.bulk_create(instances)
        return book

    def update(self, instance, validated_data):
        copies = validated_data.pop("copies", None)
        book = super().update(instance, validated_data)

        if copies is not None:
            current_copies = book.instances.count()
            if copies > current_copies:
                new_instances = [
                    BookInstance(book=book, status=BookInstance.AVAILABLE)
                    for _ in range(copies - current_copies)
                ]
                BookInstance.objects.bulk_create(new_instances)
            elif copies < current_copies:
                to_remove = current_copies - copies
                avail_instances = book.instances.filter(status=BookInstance.AVAILABLE)
                if avail_instances.count() < to_remove:
                    on_loan_count = book.instances.filter(status=BookInstance.ON_LOAN).count()
                    raise serializers.ValidationError({
                        "copies": f"Không thể giảm số lượng xuống {copies} vì có {on_loan_count} bản sao đang được mượn chưa trả."
                    })
                delete_pks = list(avail_instances.values_list("pk", flat=True)[:to_remove])
                BookInstance.objects.filter(pk__in=delete_pks).delete()

        return book
