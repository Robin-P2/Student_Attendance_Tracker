from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('login/', obtain_auth_token, name='api_login'),
    path('students/', views.StudentList.as_view(), name='api_students'),
    path('attendance/', views.AttendanceList.as_view(), name='api_attendance'),
    path('reports/', views.ReportView.as_view(), name='api_reports'),
]