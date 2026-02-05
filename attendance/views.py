from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from core.models import Student, Profile
from .models import Attendance


@login_required
def mark_attendance(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')


    if profile.role != 'teacher':
        messages.error(request, 'Only class teachers can mark attendance.')
        return redirect('dashboard')


    if not profile.assigned_year:
        messages.error(request, 'No year assigned to you. Contact HOD.')
        return redirect('dashboard')


    selected_date = request.GET.get('date', '')
    if selected_date:
        try:
            attendance_date = date.fromisoformat(selected_date)
        except ValueError:
            attendance_date = date.today()
    else:
        attendance_date = date.today()


    students = Student.objects.filter(year=profile.assigned_year).order_by('first_name')

    existing_attendance = {}
    if students.exists():
        attendance_records = Attendance.objects.filter(
            student__in=students,
            date=attendance_date
        )
        for record in attendance_records:
            existing_attendance[record.student.id] = record.status

    if request.method == 'POST':
        success_count = 0

        for student in students:
            status_key = f"status_{student.id}"
            remarks_key = f"remarks_{student.id}"

            status = request.POST.get(status_key, 'present')
            remarks = request.POST.get(remarks_key, '')

            attendance, created = Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={
                    'status': status,
                    'marked_by': request.user,
                    'remarks': remarks
                }
            )

            success_count += 1

        if success_count > 0:
            year_name = dict(Student.YEAR_CHOICES).get(profile.assigned_year, 'Unknown')
            messages.success(request, f'Attendance marked for {success_count} student(s) in {year_name}!')
        return redirect('mark_attendance')

    year_name = dict(Student.YEAR_CHOICES).get(profile.assigned_year, 'Unknown')

    context = {
        'title': f'Mark Attendance - {year_name}',
        'students': students,
        'assigned_year': profile.assigned_year,
        'year_name': year_name,
        'attendance_date': attendance_date,
        'existing_attendance': existing_attendance,
        'today': date.today(),
    }
    return render(request, 'attendance/../templates/core/mark_attendance.html', context)


@login_required
def attendance_list(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')

    if profile.role == 'hod':
        attendances = Attendance.objects.all().order_by('-date')[:100]
    else:
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(year=assigned_year)
            attendances = Attendance.objects.filter(
                student__in=students
            ).order_by('-date', 'student__first_name')[:100]
        else:
            attendances = Attendance.objects.none()
            messages.warning(request, 'No year assigned to you. Contact HOD.')

    context = {
        'title': 'Attendance Records',
        'attendances': attendances,
        'profile': profile,
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def attendance_reports_view(request):
    """Generate simple attendance reports"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')

    if profile.role == 'hod':
        total_students = Student.objects.count()
        today_attendance = Attendance.objects.filter(date=date.today()).count()
    else:
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(year=assigned_year)
            total_students = students.count()
            today_attendance = Attendance.objects.filter(
                student__in=students,
                date=date.today()
            ).count()
        else:
            total_students = 0
            today_attendance = 0
            messages.warning(request, 'No year assigned to you. Contact HOD.')

    context = {
        'title': 'Attendance Reports',
        'total_students': total_students,
        'today_attendance': today_attendance,
        'date': date.today(),
        'profile': profile,
    }
    return render(request, 'core/reports.html', context)