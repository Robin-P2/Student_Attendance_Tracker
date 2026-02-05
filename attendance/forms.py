from django import forms
from django.utils import timezone
from .models import Attendance
from core.models import Student


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class BulkAttendanceForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)

        if teacher:
            students = Student.objects.filter(assigned_teacher=teacher)
            for student in students:
                self.fields[f'student_{student.id}'] = forms.ChoiceField(
                    choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late'), ('excused', 'Excused')],
                    initial='present',
                    label=f"{student.full_name} ({student.student_class})",
                    widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
                )