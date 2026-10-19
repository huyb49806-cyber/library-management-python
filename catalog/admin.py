from django.contrib import admin

from .models import Author, Book, BookInstance, Genre, Language

admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Book)
admin.site.register(BookInstance)
