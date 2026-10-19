from django.urls import path

from .api_views import AuthorDetailView, AuthorListCreateView, BookDetailView, BookInstanceDetailView, BookInstanceListCreateView, BookListCreateView, GenreDetailView, GenreListCreateView, LanguageDetailView, LanguageListCreateView

urlpatterns = [
    path("authors/", AuthorListCreateView.as_view(), name="catalog-authors"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="catalog-author-detail"),
    path("genres/", GenreListCreateView.as_view(), name="catalog-genres"),
    path("genres/<int:pk>/", GenreDetailView.as_view(), name="catalog-genre-detail"),
    path("languages/", LanguageListCreateView.as_view(), name="catalog-languages"),
    path("languages/<int:pk>/", LanguageDetailView.as_view(), name="catalog-language-detail"),
    path("books/", BookListCreateView.as_view(), name="catalog-books"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="catalog-book-detail"),
    path("book-instances/", BookInstanceListCreateView.as_view(), name="catalog-book-instances"),
    path("book-instances/<uuid:pk>/", BookInstanceDetailView.as_view(), name="catalog-book-instance-detail"),
]
