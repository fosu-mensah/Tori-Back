# Generated by Django 4.2.3 on 2023-07-26 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='like_count',
            field=models.IntegerField(default=0, verbose_name='좋아요'),
        ),
    ]
