# Generated by Django 5.0.4 on 2024-04-19 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0020_job_external_id_job_source_job_submitted_datetime_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="listing_url",
            field=models.URLField(),
        ),
    ]