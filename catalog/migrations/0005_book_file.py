# Generated by Django 2.1.4 on 2018-12-09 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20181207_1032'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='book_pdf/%Y/%m/%d/'),
        ),
    ]