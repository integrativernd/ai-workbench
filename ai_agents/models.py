from django.db import models
import uuid

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
    
    # You can add more fields as needed, such as:
    # capabilities = models.JSONField(default=dict)
    # performance_metrics = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
