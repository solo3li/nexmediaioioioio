from django.conf import settings
from django.db import models
from django.utils import timezone


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('InProgress', 'In Progress'),
        ('Closed', 'Closed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open', db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject} ({self.status}) - {self.user.username}"


class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_messages')
    content = models.TextField()
    attachment_url = models.URLField(max_length=1000, blank=True, null=True)
    attachment_type = models.CharField(max_length=50, blank=True, help_text="image, audio, document")
    is_admin_message = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Ticket Message'
        verbose_name_plural = 'Ticket Messages'
        ordering = ['created_at']

    def __str__(self):
        author = 'Admin' if self.is_admin_message else (self.sender.username if self.sender else 'User')
        return f"{author}: {self.content[:40]}..."
