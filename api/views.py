from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.response import Response

from core.models import Student
from attendance.models import Attendance
from .serializers import StudentSerializer, AttendanceSerializer


class StudentList(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'admin' or user.is_superuser:
            return Student.objects.all()
        return Student.objects.filter(class_teacher=user)


class AttendanceList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'admin' or user.is_superuser:
            return Attendance.objects.all()
        students = Student.objects.filter(class_teacher=user)
        return Attendance.objects.filter(student__in=students)


class ReportView(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Simple report endpoint
        from datetime import date
        today = date.today()

        if request.user.profile.role == 'admin' or request.user.is_superuser:
            total_students = Student.objects.count()
            present_today = Attendance.objects.filter(date=today, status='present').count()
            absent_today = Attendance.objects.filter(date=today, status='absent').count()
        else:
            students = Student.objects.filter(assigned_teacher=request.user)
            total_students = students.count()
            present_today = Attendance.objects.filter(
                student__in=students, date=today, status='present'
            ).count()
            absent_today = Attendance.objects.filter(
                student__in=students, date=today, status='absent'
            ).count()

        return Response({
            'date': str(today),
            'total_students': total_students,
            'present_today': present_today,
            'absent_today': absent_today,
            'attendance_rate': round((present_today / total_students * 100), 2) if total_students > 0 else 0
        })