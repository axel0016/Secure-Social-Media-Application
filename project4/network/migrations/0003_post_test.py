# Generated by Django 3.0.2 on 2023-11-26 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_post_privacy'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='test',
            field=models.CharField(blank=True, max_length=140),
        ),
    ]