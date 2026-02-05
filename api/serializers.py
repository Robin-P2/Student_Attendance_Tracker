from rest_framework import serializers
from core.models import Student
from attendance.models import Attendance


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'student_class', 'email', 'phone']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_class = serializers.CharField(source='student.student_class', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'student_class', 'date', 'status', 'remarks']