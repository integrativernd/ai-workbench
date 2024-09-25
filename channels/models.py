from django.db import models


class Channel(models.Model):
    channel_name = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100, unique=True)
    channel_type = models.CharField(max_length=100)

    def __str__(self):
        return self.channel_name
