# Generated by Django 3.2.4 on 2021-08-12 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0010_auto_20210608_1240"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="technologies",
            field=models.ManyToManyField(blank=True, related_name="projects", to="projects.Technology"),
        ),
    ]
