# Generated by Django 4.2.18 on 2025-04-06 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rootVPN', '0014_rename_cost_in_day_tariff_cost_tariff_days_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(max_length=100, unique=True)),
                ('version', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=10000)),
            ],
        ),
    ]
