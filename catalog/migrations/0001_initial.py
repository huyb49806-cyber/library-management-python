# Generated manually for the initial catalog schema.
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("date_of_death", models.DateField(blank=True, null=True)),
            ],
            options={"ordering": ("last_name", "first_name")},
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Language",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("summary", models.TextField(blank=True)),
                ("isbn", models.CharField(max_length=13, unique=True, verbose_name="ISBN")),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name="books", to="catalog.author")),
                ("language", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name="books", to="catalog.language")),
            ],
            options={"ordering": ("title",)},
        ),
        migrations.CreateModel(
            name="BookInstance",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("imprint", models.CharField(blank=True, max_length=200)),
                ("due_back", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("a", "Available"), ("o", "On loan"), ("d", "Maintenance"), ("r", "Reserved")], default="a", max_length=1)),
                ("book", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name="instances", to="catalog.book")),
                ("borrower", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="borrowed_book_instances", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("book__title", "id")},
        ),
        migrations.AddField(
            model_name="book",
            name="genre",
            field=models.ManyToManyField(blank=True, related_name="books", to="catalog.genre"),
        ),
    ]
