# Generated by Django 3.0.6 on 2020-07-06 05:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_auto_20200630_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='updated_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 7, 6, 11, 29, 22, 837617), null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 7, 6, 11, 29, 22, 835961), null=True),
        ),
    ]
