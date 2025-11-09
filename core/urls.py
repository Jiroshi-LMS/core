from django.urls import path
from . import views


urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('generate-upload-presigned-url/', views.GetUploadPresignedURL.as_view(), name='generate_upload_presigned_url')
]
