# Generated by Django 2.1.4 on 2018-12-11 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='birth_date',
        ),
    ]
