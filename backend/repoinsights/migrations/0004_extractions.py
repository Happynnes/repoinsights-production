# Generated by Django 4.2.2 on 2023-06-26 23:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("repoinsights", "0003_alter_user_table"),
    ]

    operations = [
        migrations.CreateModel(
            name="Extractions",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("date", models.DateTimeField()),
                ("ext_ref_id", models.CharField(max_length=32)),
            ],
            options={
                "db_table": "extractions",
                "managed": False,
            },
        ),
    ]
