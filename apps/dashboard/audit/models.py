"""
Audit models for tracking system changes.
"""
from django.db import models
from apps.dashboard.instructors.models import Instructor
from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """
    Model for tracking system audit logs.
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)  # Model name or resource type
    resource_id = models.CharField(max_length=100, null=True, blank=True)  # ID of the affected resource
    resource_name = models.CharField(max_length=200, null=True, blank=True)  # Human readable name
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    changes = models.JSONField(default=dict, blank=True)  # Before/after values for updates
    metadata = models.JSONField(default=dict, blank=True)  # Additional context
    
    class Meta:
        db_table = 'audit_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'action']),
            models.Index(fields=['resource_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_name = self.instructor.get_full_name() if self.instructor else 'System'
        return f"{user_name} {self.action} {self.resource_type} - {self.created_at}" 