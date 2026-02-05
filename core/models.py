from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Profile(models.Model):
    ROLE_CHOICES = [
        ('hod', 'Head of Department (HOD)'),
        ('teacher', 'Class Teacher'),
    ]

    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')
    assigned_year = models.CharField(max_length=1, choices=YEAR_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.role == 'hod':
            return f"{self.user.username} (HOD)"
        elif self.assigned_year:
            return f"{self.user.username} (Year {self.assigned_year} Teacher)"
        return f"{self.user.username} ({self.role})"


class Student(models.Model):
    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]

    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES, default='1')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    class_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_students'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Added missing field

    class Meta:
        ordering = ['year', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Year {self.year})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_year_display(self):

        return dict(self.YEAR_CHOICES).get(self.year, f'Year {self.year}')

    def get_attendance_today(self):

        from attendance.models import Attendance
        try:
            return Attendance.objects.get(student=self, date=date.today())
        except Attendance.DoesNotExist:
            return None

    def get_attendance_for_date(self, target_date):

        from attendance.models import Attendance
        try:
            return Attendance.objects.get(student=self, date=target_date)
        except Attendance.DoesNotExist:
            return None