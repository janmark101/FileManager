# Generated by Django 5.1 on 2024-09-09 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['id']},
        ),
    ]