# Generated by Django 5.1.1 on 2024-10-06 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_agents', '0013_remove_codefile_repository_codefile_repository'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiagent',
            name='nickname',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
