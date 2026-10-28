from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Author, Book, BookInstance, Genre, Language
from .serializers import (
    AuthorSerializer,
    BookInstanceSerializer,
    BookSerializer,
    GenreSerializer,
    LanguageSerializer,
)


class ReadOrAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_staff
                or user.groups.filter(name="Admin").exists()
            )
        )


class CatalogListCreateView(generics.ListCreateAPIView):
    permission_classes = (ReadOrAdminPermission,)
    search_fields = ()

    def get_queryset(self):
        queryset = self.queryset.all()
        search = self.request.query_params.get("search", "").strip()

        if search and self.search_fields:
            query = Q()

            for term in search.split():
                term_query = Q()
                for field in self.search_fields:
                    term_query |= Q(**{f"{field}__icontains": term})
                query &= term_query

            queryset = queryset.filter(query)

        return queryset


class CatalogDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (ReadOrAdminPermission,)


class AuthorListCreateView(CatalogListCreateView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    search_fields = ("first_name", "last_name")


class AuthorDetailView(CatalogDetailView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class GenreListCreateView(CatalogListCreateView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ("name",)


class GenreDetailView(CatalogDetailView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class LanguageListCreateView(CatalogListCreateView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    search_fields = ("name",)


class LanguageDetailView(CatalogDetailView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class BookListCreateView(CatalogListCreateView):
    queryset = (
        Book.objects
        .select_related("author", "language")
        .prefetch_related("genre")
        .annotate(
            annotated_total_copies=Count("instances", distinct=True),
            annotated_available_copies=Count(
                "instances",
                filter=Q(instances__status=BookInstance.AVAILABLE),
                distinct=True,
            ),
        )
    )
    serializer_class = BookSerializer
    search_fields = (
        "title",
        "isbn",
        "author__first_name",
        "author__last_name",
    )


class BookDetailView(CatalogDetailView):
    queryset = (
        Book.objects
        .select_related("author", "language")
        .prefetch_related("genre")
    )
    serializer_class = BookSerializer

    def destroy(self, request, *args, **kwargs):
        book = self.get_object()

        if book.instances.exists():
            return Response(
                {
                    "detail": (
                        "Không thể xóa đầu sách khi còn bản sao. "
                        "Hãy ghi nhận trả các bản đang mượn, rồi xóa các bản sao trước."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        self.perform_destroy(book)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookInstanceListCreateView(CatalogListCreateView):
    queryset = BookInstance.objects.select_related("book", "borrower")
    serializer_class = BookInstanceSerializer
    search_fields = ("book__title", "book__isbn", "id")


class BookInstanceDetailView(CatalogDetailView):
    queryset = BookInstance.objects.select_related("book", "borrower")
    serializer_class = BookInstanceSerializer