# Generated by Django 4.2.18 on 2025-01-22 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rootVPN', '0003_rename_id_uservpn_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uservpn',
            old_name='user_id',
            new_name='id',
        ),
    ]
