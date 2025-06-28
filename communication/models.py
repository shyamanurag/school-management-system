from django.db import models
from django.contrib.auth.models import User

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    publish_date = models.DateField()
    visible_to = models.CharField(max_length=100)  # students, teachers, etc.
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()  # Changed from content to message
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)  # Changed to ForeignKey
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')  # Changed to ForeignKey
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')  # Changed to ForeignKey
    subject = models.CharField(max_length=200)
    content = models.TextField()  # Changed from body to content
    created_at = models.DateTimeField(auto_now_add=True)  # Changed from sent_at
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} from {self.sender}"

# Create your models here.
