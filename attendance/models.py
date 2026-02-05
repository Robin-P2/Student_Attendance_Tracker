from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey('core.Student', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date', 'student__student_id']  # Changed from student__first_name to student__student_id
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.student_id} - {self.date} ({self.status})"

    def clean(self):
        # Prevent future date attendance
        if self.date > timezone.now().date():
            raise ValidationError('Attendance date cannot be in the future.')

        # Check for duplicate (handled by unique_together but nice to have)
        if Attendance.objects.filter(student=self.student, date=self.date).exclude(id=self.id).exists():
            raise ValidationError('Attendance already marked for this student on this date.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)