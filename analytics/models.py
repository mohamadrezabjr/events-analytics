from django.db import models

class Event(models.Model):
    event_name = models.CharField(max_length=100)
    user_id = models.CharField(null=True, blank=True, max_length=256)
    client_timestamp = models.DateTimeField(blank=True, null=True)
    server_timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=256, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    def __str__(self):
        return self.event_name, self.server_timestamp