import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("agents", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tienda",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("cuenta", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="tiendas", to="users.cuenta")),
            ],
            options={"db_table": "tienda"},
        ),
        migrations.CreateModel(
            name="Producto",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
                ("precio", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ("esta_activa", models.BooleanField(default=True)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("descripcion_prompt", models.TextField(blank=True, null=True)),
                ("stock", models.IntegerField(default=0)),
                ("agendable", models.BooleanField(default=True)),
            ],
            options={"db_table": "producto"},
        ),
        migrations.CreateModel(
            name="Categoria",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
                ("esta_activa", models.BooleanField(default=True)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("descripcion_prompt", models.TextField(blank=True, null=True)),
                ("logica_venta", models.TextField(blank=True, null=True)),
                ("regla", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="categorias", to="agents.regla")),
            ],
            options={"db_table": "categoria"},
        ),
        migrations.CreateModel(
            name="CategoriaTienda",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("categoria", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="tiendas", to="ecommerce.categoria")),
                ("tienda", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="categorias", to="ecommerce.tienda")),
            ],
            options={"db_table": "categoria_tienda"},
        ),
        migrations.CreateModel(
            name="ProductoCategoria",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("categoria", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="producto_relaciones", to="ecommerce.categoria")),
                ("producto", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="categoria_relaciones", to="ecommerce.producto")),
            ],
            options={"db_table": "producto_categoria"},
        ),
        migrations.CreateModel(
            name="Agenda",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("inicio", models.DateTimeField()),
                ("fin", models.DateTimeField()),
                ("cliente_id", models.IntegerField(blank=True, null=True)),
                ("producto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="agendas", to="ecommerce.producto")),
            ],
            options={"db_table": "agenda"},
        ),
    ]
