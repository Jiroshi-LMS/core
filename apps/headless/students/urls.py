from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
# router.register(r'instructor', views.InstructorViewSet)

urlpatterns = [
    # Student Auth
    path('signup/', views.StudentSignUpView.as_view(), name='student-signup'),
    path('login/', views.StudentLoginView.as_view(), name='student-login'),
    path('refresh-token/', views.StudentRefreshTokenView.as_view(), name="student-refresh-token"),
    path('lookup/', views.StudentExistsLookup.as_view(), name="quick-student-exists-lookup"),
    path('profile/', views.StudentProfileView.as_view(), name="student-profile"),
    path('account/update/', views.StudentAccountDetailsUpdateView.as_view(), name="student-account-update"),
    path('logout/', views.StudentLogoutView.as_view(), name='student-logout'),

]

urlpatterns += router.urls