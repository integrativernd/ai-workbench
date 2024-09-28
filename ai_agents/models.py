from django.db import models
import uuid
from rq.job import Job
import django_rq
from llm.anthropic_integration import get_basic_message
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
