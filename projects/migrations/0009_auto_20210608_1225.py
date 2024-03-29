# Generated by Django 3.2.4 on 2021-06-08 12:25

import autoslug.fields
import django.utils.timezone
from django.db import migrations

import projects.models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0008_alter_project_technologies"),
    ]

    operations = [
        migrations.AddField(
            model_name="maker",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                always_update=True,
                null=True,
                editable=True,
                max_length=256,
                populate_from="first_name",
                unique=True,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="technology",
            name="slug",
            field=autoslug.fields.AutoSlugField(always_update=True, null=True, editable=True, populate_from="name"),
            preserve_default=False,
        ),
    ]
