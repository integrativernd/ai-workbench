# Generated by Django 5.1.1 on 2024-09-25 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.CharField(max_length=100)),
                ('channel_id', models.CharField(max_length=100, unique=True)),
                ('channel_type', models.CharField(max_length=100)),
            ],
        ),
    ]
