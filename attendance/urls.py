from django.urls import path
from . import views

urlpatterns = [
    path('mark/', views.mark_attendance, name='attendance_mark'),
    path('list/', views.attendance_list, name='attendance_list'),
    path('reports/', views.attendance_reports_view, name='attendance_reports_view'),
]