# Generated by Django 3.2.15 on 2022-08-18 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nom151', '0002_auto_20210409_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conservationcertificate',
            name='data',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='conservationcertificate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]