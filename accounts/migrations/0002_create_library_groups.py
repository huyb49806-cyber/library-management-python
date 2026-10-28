from django.conf import settings
from django.db import migrations


def create_library_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    database = schema_editor.connection.alias

    for name in ("Member", "Librarian", "Admin"):
        Group.objects.using(database).get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            create_library_groups,
            migrations.RunPython.noop,
        ),
    ]