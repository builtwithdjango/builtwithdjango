# Generated by Django 3.2.11 on 2022-01-23 05:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0018_auto_20211108_0616"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={"ordering": ("-created_date",)},
        ),
    ]
