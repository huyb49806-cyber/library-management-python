from rest_framework import serializers

from .models import Author, Book, BookInstance, Genre, Language


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
    book_title = serializers.CharField(source="book.title", read_only=True)
    borrower_name = serializers.CharField(source="borrower.username", read_only=True, allow_null=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    can_mark_returned = serializers.BooleanField(read_only=True)

    class Meta:
        model = BookInstance
        fields = ("id", "book", "book_title", "imprint", "due_back", "borrower", "borrower_name", "status", "status_label", "is_overdue", "can_mark_returned")
        read_only_fields = ("id", "borrower", "due_back", "is_overdue", "can_mark_returned")

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
    author_detail = AuthorSerializer(source="author", read_only=True)
    language_detail = LanguageSerializer(source="language", read_only=True)
    genre_details = GenreSerializer(source="genre", many=True, read_only=True)
    total_copies = serializers.SerializerMethodField()
    available_copies = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ("id", "title", "author", "author_detail", "summary", "isbn", "genre", "genre_details", "language", "language_detail", "total_copies", "available_copies")

    def get_total_copies(self, obj):
        return getattr(obj, "annotated_total_copies", obj.total_copies)

    def get_available_copies(self, obj):
        return getattr(obj, "annotated_available_copies", obj.available_copies)
