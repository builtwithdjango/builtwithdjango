# Generated by Django 3.2.4 on 2021-08-14 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0004_alter_job_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="job", name="approved", field=models.BooleanField(default=False),
        ),
    ]