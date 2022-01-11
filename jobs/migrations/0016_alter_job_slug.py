# Generated by Django 3.2.9 on 2021-12-10 20:46

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0015_job_paid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="slug",
            field=autoslug.fields.AutoSlugField(always_update=True, editable=False, null=True, populate_from="title"),
        ),
    ]