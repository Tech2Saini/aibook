# Generated by Django 5.1.6 on 2025-02-07 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0003_bookmark_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookmark',
            name='count',
        ),
    ]
