# Generated by Django 3.2.12 on 2022-02-21 17:38

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_auto_20220219_0541"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="github_handle",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="customuser",
            name="indiehackers_handle",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="customuser",
            name="interviewed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customuser",
            name="personal_website",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="short_bio",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="slug",
            field=autoslug.fields.AutoSlugField(always_update=True, default=1, editable=True, populate_from="username"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="customuser",
            name="twitter_handle",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
