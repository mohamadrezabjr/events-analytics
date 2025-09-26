from django.db import models

class Event(models.Model):
    event_name = models.CharField(max_length=100)
    user_id = models.CharField(null=True, blank=True, max_length=256)
    client_timestamp = models.DateTimeField(blank=True, null=True)
    server_timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=256, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    def __str__(self):
        return f'{self.event_name}  server_time : {self.server_timestamp.strftime("%Y-%m-%d %H:%M:%S")}'