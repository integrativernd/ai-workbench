from django.db import models
from django.utils import timezone
import uuid


class Channel(models.Model):
    channel_name = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100, unique=True)
    channel_type = models.CharField(max_length=100)

    def __str__(self):
        return self.channel_name

class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    author = models.CharField(max_length=100)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.author}: {self.content[:50]}..."  # Returns first 50 characters of the message

    class Meta:
        ordering = ['-timestamp']  # Orders messages by most recent first

    @property
    def token(self):
        return self.token.hex