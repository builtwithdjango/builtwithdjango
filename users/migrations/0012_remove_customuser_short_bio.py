# Generated by Django 3.2.17 on 2023-03-06 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_delete_paypaltransaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='short_bio',
        ),
    ]
