import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("agents", "0001_initial"),
        ("ecommerce", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModeloIA",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
            ],
            options={"db_table": "modelo_ia"},
        ),
        migrations.CreateModel(
            name="TipoAgente",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255, unique=True)),
            ],
            options={"db_table": "tipo_agente"},
        ),
        migrations.CreateModel(
            name="FlujoAgente",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
                ("nombre_comercial", models.CharField(max_length=255)),
                ("descripcion", models.TextField(blank=True, null=True)),
                ("tienda", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="flujos_agente", to="ecommerce.tienda")),
            ],
            options={"db_table": "flujo_agente"},
        ),
        migrations.CreateModel(
            name="ProductoFlujoAgente",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("flujo_agente", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="producto_relaciones", to="agents.flujoagente")),
                ("producto", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="flujo_agente_relaciones", to="ecommerce.producto")),
            ],
            options={"db_table": "producto_flujo_agente"},
        ),
        migrations.CreateModel(
            name="CategoriaFlujoAgente",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("categoria", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="flujos_agente", to="ecommerce.categoria")),
                ("flujo_agente", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="categorias", to="agents.flujoagente")),
            ],
            options={"db_table": "categoria_flujo_agente"},
        ),
        migrations.CreateModel(
            name="AgentSession",
            fields=[
                ("session_id", models.CharField(max_length=255, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "agent_sessions"},
        ),
        migrations.CreateModel(
            name="Agente",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=255)),
                ("logica", models.TextField(blank=True, null=True)),
                ("flujo_agente", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="agentes", to="agents.flujoagente")),
                ("modelo_ia", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="agentes", to="agents.modeloia")),
                ("reglamento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="agentes", to="agents.reglamento")),
                ("tienda", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="agentes", to="ecommerce.tienda")),
                ("tipo_agente", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="agentes", to="agents.tipoagente")),
            ],
            options={"db_table": "agente"},
        ),
        migrations.CreateModel(
            name="AgentMessage",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("message_data", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="messages", to="agents.agentsession")),
            ],
            options={"db_table": "agent_messages"},
        ),
    ]
