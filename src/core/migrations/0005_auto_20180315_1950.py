# Generated by Django 2.0.3 on 2018-03-15 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20180315_1944'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='setting',
            options={'ordering': ('key',)},
        ),
    ]