# Generated by Django 2.0.7 on 2018-07-09 15:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RuleDescription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=255, unique=True)),
                ('value', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
