from django.urls import path
from . import views

urlpatterns = [
    # ROOT URL
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Teacher Management
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('teachers/edit/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('assign-year/<int:teacher_id>/', views.assign_year, name='assign_year'),
    path('teachers/delete/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),

    # Student Management
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),

    # Teacher Panel
    path('teacher-panel/', views.teacher_panel, name='teacher_panel'),
    path('my-students/', views.view_assigned_students, name='view_assigned_students'),

    # Attendance (Core app versions - TEACHERS ONLY)
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-reports/', views.attendance_reports, name='attendance_reports'),

    # Other
    path('assign-students/', views.assign_students_to_teachers, name='assign_students'),
    path('attendance-list/', views.attendance_list, name='attendance_list'),

    path('teacher-panel/', views.teacher_panel, name='teacher_panel'),
    path('my-students/', views.view_assigned_students, name='view_assigned_students'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-reports/', views.attendance_reports, name='attendance_reports'),
    path('reports/detailed/', views.detailed_reports, name='detailed_reports'),
    path('reports/monthly/', views.monthly_reports, name='monthly_reports'),
    path('reports/student-wise/', views.student_wise_reports, name='student_wise_reports'),
    path('reports/export-csv/', views.export_report_csv, name='export_report_csv'),
    path('reports/analytics/', views.attendance_analytics, name='attendance_analytics'),
]