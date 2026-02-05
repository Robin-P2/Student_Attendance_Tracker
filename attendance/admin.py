from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_by', 'created_at')
    list_filter = ('date', 'status', 'marked_by')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name', 'remarks')
    ordering = ('-date', 'student__student_id')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'marked_by')