# Generated by Django 5.1 on 2024-09-03 10:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0001_initial'),
        ('FoldersFiles', '0002_alter_file_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='team',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Auth.team'),
            preserve_default=False,
        ),
    ]
