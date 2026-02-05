from django.contrib import admin
from .models import Profile, Student


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_year', 'phone', 'created_at')
    list_filter = ('role', 'assigned_year')
    search_fields = ('user__username', 'user__email', 'phone')
    ordering = ('role', 'user__username')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'year', 'class_teacher', 'created_at')
    list_filter = ('year', 'class_teacher')
    search_fields = ('student_id', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('year', 'first_name', 'last_name')


    def get_queryset(self, request):
        return super().get_queryset(request).select_related('class_teacher')