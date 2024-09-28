from django.db import models
import uuid
from rq.job import Job
import django_rq
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
    
    # You can add more fields as needed, such as:
    # capabilities = models.JSONField(default=dict)
    # performance_metrics = models.JSONField(default=dict)
    
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
        return Job.fetch_many([self.job_ids], connection=message_queue.connection)
