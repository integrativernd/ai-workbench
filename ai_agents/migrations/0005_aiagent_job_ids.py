# Generated by Django 5.1.1 on 2024-09-27 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_agents', '0004_aiagent_bot_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiagent',
            name='job_ids',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
