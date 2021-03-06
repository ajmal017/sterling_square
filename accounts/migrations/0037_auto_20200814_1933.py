# Generated by Django 3.0.6 on 2020-08-14 14:03

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_auto_20200811_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gainlosshistory',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 8, 14, 19, 33, 1, 700450), null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='updated_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 8, 14, 19, 33, 1, 697828), null=True),
        ),
        migrations.AlterField(
            model_name='topsearched',
            name='stock',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_top_search_rel', to='accounts.StockNames'),
        ),
        migrations.AlterField(
            model_name='totalgainloss',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 8, 14, 19, 33, 1, 699817), null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='time',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 8, 14, 19, 33, 1, 696981), null=True),
        ),
        migrations.AlterField(
            model_name='transactionhistory',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 8, 14, 19, 33, 1, 699356), null=True),
        ),
    ]
