# Generated by Django 2.1.5 on 2019-01-21 01:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('specifier', '0002_auto_20190120_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='condition',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='specifier.Condition'),
        ),
    ]