# Generated by Django 2.1.2 on 2018-10-18 10:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20181018_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twofactorbackupcode',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
