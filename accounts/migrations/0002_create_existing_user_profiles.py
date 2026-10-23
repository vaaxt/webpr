from django.conf import settings
from django.db import migrations


def create_profiles_for_existing_users(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    UserProfile = apps.get_model('accounts', 'UserProfile')
    database = schema_editor.connection.alias
    UserProfile.objects.using(database).bulk_create(
        UserProfile(user_id=user_id)
        for user_id in User.objects.using(database).values_list('pk', flat=True)
    )


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_profiles_for_existing_users,
            migrations.RunPython.noop,
        ),
    ]
