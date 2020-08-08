# Generated by Django 3.1 on 2020-08-08 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0009_listentry_from_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listentry',
            name='listing_type',
            field=models.CharField(choices=[('blocked', 'Blocked'), ('allowed', 'Allowed')], db_index=True, max_length=12, verbose_name='Listing type'),
        ),
    ]
