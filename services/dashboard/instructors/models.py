import uuid

from core.models import TimeStampedModel, SoftDeleteMixin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from simple_history.models import HistoricalRecords
from rest_framework_simplejwt.tokens import RefreshToken


class Instructor(AbstractUser, TimeStampedModel, SoftDeleteMixin):

    PROFILE_STATUS_CHOICES = [
        ('complete', _('Complete')),
        ('pending', _('Pending')),
        ('partial', _('Partial')),
    ]

    full_name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    phone_number = models.CharField(unique=True, max_length=15, null=True, blank=True)
    profile_completion_status = models.CharField(max_length=20, choices=PROFILE_STATUS_CHOICES, default='pending')

    history = HistoricalRecords()
    
    class Meta:
        db_table = 'instructors'
        verbose_name_plural = 'Instructors'

    def __str__(self):
        return self.username
    

class InstructorProfile(TimeStampedModel, SoftDeleteMixin):
    """
        Instructor Profile and related information.
    """
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='profiles', unique=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'instructor_profiles'
        verbose_name_plural = 'Instructor Profiles'
        ordering = ['-created_at']
    

class InstructorSession(TimeStampedModel, SoftDeleteMixin):
    """
    Enhanced user session tracking for security and analytics.
    """
    SESSION_STATUS_CHOICES = [
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('terminated', _('Terminated')),
        ('suspicious', _('Suspicious')),
    ]

    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=512, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Geographic information
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Device information
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    
    # Session status and activity
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS_CHOICES,
        default='active'
    )
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    
    # Security flags
    is_suspicious = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('Instructor Session')
        verbose_name_plural = _('Instructor Sessions')
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['instructor', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"Session for {self.instructor} from {self.ip_address}"

    @property
    def duration(self):
        """
        Calculate session duration.
        """
        end_time = self.logout_time or timezone.now()
        return end_time - self.login_time

    def terminate_session(self):
        """
        Terminate the session.
        """
        self.is_active = False
        self.status = 'terminated'
        self.logout_time = timezone.now()
        self.save()


class LoginAttempt(TimeStampedModel):
    """
    Track login attempts for security monitoring.
    """
    ATTEMPT_TYPES = [
        ('success', _('Successful Login')),
        ('failed_password', _('Failed Password')),
        ('failed_username', _('Failed Username')),
        ('blocked', _('Blocked Attempt')),
        ('suspicious', _('Suspicious Attempt')),
    ]

    username = models.CharField(max_length=150)
    instructor = models.ForeignKey(
        Instructor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='login_attempts'
    )
    
    attempt_type = models.CharField(max_length=20, choices=ATTEMPT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Geographic information
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Security context
    is_suspicious = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=200, blank=True)

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('Login Attempt')
        verbose_name_plural = _('Login Attempts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['attempt_type']),
            models.Index(fields=['is_suspicious']),
        ]

    def __str__(self):
        return f"{self.username} - {self.attempt_type} from {self.ip_address}"