from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Reglamento",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
            ],
            options={"db_table": "reglamento"},
        ),
        migrations.CreateModel(
            name="Regla",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("orden", models.IntegerField()),
                ("texto", models.TextField()),
                ("esta_seleccionable", models.BooleanField(default=True)),
                ("reglamento", models.ForeignKey(on_delete=models.PROTECT, related_name="reglas", to="agents.reglamento")),
            ],
            options={"db_table": "regla", "ordering": ["orden"]},
        ),
    ]
