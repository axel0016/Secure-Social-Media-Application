# Generated by Django 3.0.2 on 2023-11-26 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='privacy',
            field=models.CharField(choices=[('public', 'public'), ('private', 'private')], default='public', max_length=10),
        ),
    ]