from django.conf import settings
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Cuenta",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
                ("nombre_usuario", models.CharField(max_length=255, unique=True)),
                ("contrasena", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name="cuenta", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={"db_table": "cuenta"},
        ),
    ]
