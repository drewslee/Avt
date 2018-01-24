# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-24 12:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Avtoregion', '0002_race_shoulder'),
    ]

    operations = [
        migrations.CreateModel(
            name='Constants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_unit_full', models.CharField(max_length=256)),
                ('organization_unit_small', models.CharField(max_length=50)),
                ('mechanic', models.CharField(max_length=50)),
                ('dispatcher', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='car',
            name='brand',
            field=models.CharField(default='Scania', max_length=20),
        ),
    ]