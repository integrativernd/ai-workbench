from django.db import models


class AIAgent(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    version = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # You can add more fields as needed, such as:
    # capabilities = models.JSONField(default=dict)
    # performance_metrics = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
