# Generated by Django 5.1.1 on 2024-09-30 02:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_agents', '0005_aiagent_job_ids'),
        ('channels', '0003_message_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIAgentTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('result', models.JSONField(blank=True, null=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('ai_agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='ai_agents.aiagent')),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='channels.channel')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='channels.message')),
                ('parent_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='ai_agents.aiagenttask')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
