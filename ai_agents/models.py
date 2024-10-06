from config.settings import EMBEDDING_MODEL_DIMENSIONS
from django.db import models
import uuid
from rq.job import Job
import django_rq
from llm.anthropic_integration import get_basic_message
from channels.models import Channel, Message
from pgvector.django import VectorField

class AIAgent(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    version = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    application_id = models.CharField(max_length=200, null=True)
    bot_token = models.CharField(max_length=200, null=True)
    job_ids = models.JSONField(default=list, blank=True)
    nickname = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.name} (v{self.version})"

    def add_job(self, job_id):
        if job_id not in self.job_ids:
            self.job_ids.append(job_id)
            self.save()

    def remove_job(self, job_id):
        if job_id in self.job_ids:
            self.job_ids.remove(job_id)
            self.save()

    def get_jobs(self):
        message_queue = django_rq.get_queue('default')
        return Job.fetch_many(self.job_ids, connection=message_queue.connection)
    
    def job_count(self):
        return len(self.job_ids)

    def active_job_count(self):
        jobs = self.get_jobs()
        return sum(1 for job in jobs if job.is_started)
    
    def respond_to_user(self, user_input):
        message = get_basic_message(
            self.description,
            [
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
        )
        return message.content[0].text


class AIAgentTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    ai_agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, related_name='tasks')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='tasks')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    result = models.JSONField(null=True, blank=True)
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

    def start_subtasks(self):
        for subtask in self.subtasks.all().order_by('order'):
            subtask.status = 'IN_PROGRESS'
            subtask.save()
            # Add any additional logic for starting subtasks

    @property
    def previous_task(self):
        if self.parent_task:
            return self.parent_task.subtasks.filter(order__lt=self.order).last()
        return None

    @property
    def next_task(self):
        if self.parent_task:
            return self.parent_task.subtasks.filter(order__gt=self.order).first()
        return None
    
class CodeRepository(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()

class CodeFile(models.Model):
    file_path = models.CharField(max_length=500, null=True)
    repository = models.ForeignKey(CodeRepository, on_delete=models.CASCADE, related_name='files', null=True)
    content = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_MODEL_DIMENSIONS, null=True)
    last_updated = models.DateTimeField(auto_now=True)