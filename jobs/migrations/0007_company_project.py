# Generated by Django 3.2.4 on 2021-08-19 21:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0012_auto_20210819_2054"),
        ("jobs", "0006_alter_company_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="project",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="projects.project",
            ),
        ),
    ]
