from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Student
from django.db.models import Q
from datetime import date
from attendance.models import Attendance


def home(request):
    return render(request, 'core/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core/login.html')


@login_required
def dashboard(request):
    user = request.user
    today = date.today()

    try:
        profile = user.profile
    except Profile.DoesNotExist:
        role = 'admin' if user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=user, role=role)

    context = {
        'user': user,
        'profile': profile,
        'today': today,
    }

    # ADMIN DASHBOARD
    if user.is_superuser:
        total_students = Student.objects.count()
        total_teachers = User.objects.filter(profile__role='teacher').count()


        year_stats = {}
        for year_code, year_name in Student.YEAR_CHOICES:
            count = Student.objects.filter(year=year_code).count()
            year_stats[year_name] = count

        context.update({
            'total_students': total_students,
            'total_teachers': total_teachers,
            'year_stats': year_stats,
            'dashboard_type': 'admin'
        })

    # HOD DASHBOARD
    elif profile.role == 'hod':
        total_students = Student.objects.count()
        total_teachers = User.objects.filter(profile__role='teacher').count()


        year_stats = {}
        for year_code, year_name in Student.YEAR_CHOICES:
            count = Student.objects.filter(year=year_code).count()
            year_stats[year_name] = count

        context.update({
            'total_students': total_students,
            'total_teachers': total_teachers,
            'year_stats': year_stats,
            'dashboard_type': 'hod'
        })

    # TEACHER DASHBOARD
    else:
        assigned_year = profile.assigned_year
        if assigned_year:
            # Get students assigned to this teacher
            my_students = Student.objects.filter(year=assigned_year, class_teacher=user)
            total_students = my_students.count()


            today_attendance = Attendance.objects.filter(
                student__in=my_students,
                date=today
            )
            present_today = today_attendance.filter(status='present').count()

            year_name = dict(Student.YEAR_CHOICES).get(assigned_year, 'Unknown')
            year_stats = {year_name: total_students}

            context.update({
                'total_students': total_students,
                'present_today': present_today,
                'year_stats': year_stats,
                'year_name': year_name,
                'dashboard_type': 'teacher'
            })
        else:
            context.update({
                'total_students': 0,
                'present_today': 0,
                'dashboard_type': 'teacher',
                'message': 'No year assigned. Contact HOD.'
            })

    return render(request, 'core/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')



@login_required
def teacher_list(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)


    if not request.user.is_superuser and profile.role != 'hod':
        messages.error(request, 'Access denied. Admin/HOD only.')
        return redirect('dashboard')

    teachers = User.objects.filter(profile__role='teacher').select_related('profile')


    for teacher in teachers:
        teacher.student_count = Student.objects.filter(class_teacher=teacher).count()
        if teacher.profile.assigned_year:
            year_name = dict(Profile.YEAR_CHOICES).get(teacher.profile.assigned_year, 'Unknown')
            teacher.assigned_year_name = year_name
        else:
            teacher.assigned_year_name = 'Not Assigned'

    context = {
        'teachers': teachers,
        'title': 'Manage Teachers',
        'is_admin': request.user.is_superuser
    }
    return render(request, 'core/teacher_list.html', context)


@login_required
def add_teacher(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)


    if not request.user.is_superuser and profile.role != 'hod':
        messages.error(request, 'Access denied. Admin/HOD only.')
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        assigned_year = request.POST.get('assigned_year', '').strip()


        if not all([username, email, password]):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'core/add_teacher.html', {
                'title': 'Add Teacher',
                'YEAR_CHOICES': Profile.YEAR_CHOICES
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'core/add_teacher.html', {
                'title': 'Add Teacher',
                'YEAR_CHOICES': Profile.YEAR_CHOICES
            })

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'core/add_teacher.html', {
                'title': 'Add Teacher',
                'YEAR_CHOICES': Profile.YEAR_CHOICES
            })

        try:

            teacher = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )


            Profile.objects.create(
                user=teacher,
                role='teacher',
                assigned_year=assigned_year if assigned_year else None
            )


            if assigned_year:
                Student.objects.filter(year=assigned_year).update(class_teacher=teacher)

            messages.success(request, f'Teacher {username} added successfully!')
            return redirect('teacher_list')
        except Exception as e:
            messages.error(request, f'Error creating teacher: {str(e)}')

    return render(request, 'core/add_teacher.html', {
        'title': 'Add Teacher',
        'YEAR_CHOICES': Profile.YEAR_CHOICES
    })


@login_required
def assign_year(request, teacher_id):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)


    if not request.user.is_superuser and profile.role != 'hod':
        messages.error(request, 'Access denied. Admin/HOD only.')
        return redirect('dashboard')

    teacher = get_object_or_404(User, id=teacher_id)
    profile_obj = get_object_or_404(Profile, user=teacher)

    if request.method == 'POST':
        assigned_year = request.POST.get('assigned_year', '').strip()
        old_year = profile_obj.assigned_year

        profile_obj.assigned_year = assigned_year if assigned_year else None
        profile_obj.save()


        if assigned_year != old_year:
            if old_year:

                Student.objects.filter(year=old_year, class_teacher=teacher).update(class_teacher=None)
            if assigned_year:

                Student.objects.filter(year=assigned_year).update(class_teacher=teacher)

        messages.success(request, f'Year {assigned_year} assigned to teacher {teacher.username}!')
        return redirect('teacher_list')

    context = {
        'teacher': teacher,
        'profile': profile_obj,
        'YEAR_CHOICES': Profile.YEAR_CHOICES,
        'title': f'Assign Year to {teacher.username}',
    }
    return render(request, 'core/assign_year.html', context)


@login_required
def edit_teacher(request, teacher_id):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # ADMIN and HOD can access
    if not request.user.is_superuser and profile.role != 'hod':
        messages.error(request, 'Access denied. Admin/HOD only.')
        return redirect('dashboard')

    teacher = get_object_or_404(User, id=teacher_id)
    profile_obj = get_object_or_404(Profile, user=teacher)

    if request.method == 'POST':
        teacher.first_name = request.POST.get('first_name', '').strip()
        teacher.last_name = request.POST.get('last_name', '').strip()
        teacher.email = request.POST.get('email', '').strip()

        password = request.POST.get('password', '').strip()
        if password:
            teacher.set_password(password)

        assigned_year = request.POST.get('assigned_year', '').strip()
        old_year = profile_obj.assigned_year

        teacher.save()
        profile_obj.assigned_year = assigned_year if assigned_year else None
        profile_obj.save()


        if assigned_year != old_year:
            if old_year:

                Student.objects.filter(year=old_year, class_teacher=teacher).update(class_teacher=None)
            if assigned_year:

                Student.objects.filter(year=assigned_year).update(class_teacher=teacher)

        messages.success(request, f'Teacher {teacher.username} updated successfully!')
        return redirect('teacher_list')

    context = {
        'teacher': teacher,
        'profile': profile_obj,
        'YEAR_CHOICES': Profile.YEAR_CHOICES,
        'title': 'Edit Teacher',
        'is_admin': request.user.is_superuser
    }
    return render(request, 'core/edit_teacher.html', context)


@login_required
def delete_teacher(request, teacher_id):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)


    if not request.user.is_superuser and profile.role != 'hod':
        messages.error(request, 'Access denied. Admin/HOD only.')
        return redirect('dashboard')

    teacher = get_object_or_404(User, id=teacher_id)


    if teacher == request.user:
        messages.error(request, 'You cannot delete your own account.')
    else:
        username = teacher.username
        teacher.delete()
        messages.success(request, f'Teacher {username} deleted successfully!')

    return redirect('teacher_list')


# ===== STUDENT MANAGEMENT =====
@login_required
def student_list(request):
    """List students based on role"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # ADMIN/HOD sees all, teachers see only their students
    if request.user.is_superuser or profile.role == 'hod':
        students = Student.objects.all()
        show_year_filter = True
    else:
        # Teacher sees only their assigned students
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(year=assigned_year, class_teacher=request.user)
            if students.count() == 0:
                messages.info(request,
                              f'No students assigned to you in Year {assigned_year}. Showing all students in your year.')
                students = Student.objects.filter(year=assigned_year)
        else:
            students = Student.objects.none()
            messages.warning(request, 'No year assigned to you. Contact HOD.')
        show_year_filter = False

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Year filter (only for Admin/HOD)
    year_filter = request.GET.get('year', '')
    if year_filter and (request.user.is_superuser or profile.role == 'hod'):
        students = students.filter(year=year_filter)

    context = {
        'students': students,
        'search_query': search_query,
        'year_filter': year_filter,
        'show_year_filter': show_year_filter,
        'YEAR_CHOICES': Student.YEAR_CHOICES,
        'title': 'Manage Students',
        'is_admin': request.user.is_superuser
    }
    return render(request, 'core/student_list.html', context)


@login_required
def add_student(request):
    """Add a new student - UPDATED TO AUTO-ASSIGN TEACHER"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    if request.method == 'POST':
        student_id = request.POST.get('student_id', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Get year (HOD selects, teacher uses assigned year)
        if request.user.is_superuser or profile.role == 'hod':
            year = request.POST.get('year', '1').strip()
        else:
            year = profile.assigned_year or '1'

        # Validation
        if not all([student_id, first_name, last_name, year]):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'core/add_student.html', {
                'title': 'Add Student',
                'YEAR_CHOICES': Student.YEAR_CHOICES,
                'show_year_field': request.user.is_superuser or profile.role == 'hod',
                'profile': profile
            })

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, 'Student ID already exists.')
            return render(request, 'core/add_student.html', {
                'title': 'Add Student',
                'YEAR_CHOICES': Student.YEAR_CHOICES,
                'show_year_field': request.user.is_superuser or profile.role == 'hod',
                'profile': profile
            })

        try:
            # AUTO-ASSIGN TEACHER BASED ON YEAR
            class_teacher = None

            if profile.role == 'teacher':
                # Teacher adding student - auto-assign to themselves
                class_teacher = request.user
            elif request.user.is_superuser or profile.role == 'hod':
                # HOD/Admin adding student - find teacher for that year
                teacher_for_year = User.objects.filter(
                    profile__role='teacher',
                    profile__assigned_year=year
                ).first()
                class_teacher = teacher_for_year

            # Create student
            student = Student.objects.create(
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                year=year,
                email=request.POST.get('email', '').strip(),
                phone=request.POST.get('phone', '').strip(),
                address=request.POST.get('address', '').strip(),
                class_teacher=class_teacher
            )

            messages.success(request, f'Student {first_name} {last_name} added successfully!')
            if class_teacher:
                messages.info(request, f'Assigned to teacher: {class_teacher.username}')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f'Error creating student: {str(e)}')

    return render(request, 'core/add_student.html', {
        'title': 'Add Student',
        'YEAR_CHOICES': Student.YEAR_CHOICES,
        'show_year_field': request.user.is_superuser or profile.role == 'hod',
        'profile': profile
    })


@login_required
def edit_student(request, student_id):
    """Edit student details"""
    student = get_object_or_404(Student, id=student_id)

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # Check permission
    if not request.user.is_superuser and profile.role != 'hod' and student.class_teacher != request.user:
        messages.error(request, 'Access denied. You can only edit your assigned students.')
        return redirect('student_list')

    # Get teachers for assignment
    if request.user.is_superuser or profile.role == 'hod':
        teachers = User.objects.filter(profile__role='teacher')
        show_year_field = True
    else:
        teachers = User.objects.filter(id=request.user.id)
        show_year_field = False

    if request.method == 'POST':
        student.first_name = request.POST.get('first_name', '').strip()
        student.last_name = request.POST.get('last_name', '').strip()
        student.email = request.POST.get('email', '').strip()
        student.phone = request.POST.get('phone', '').strip()
        student.address = request.POST.get('address', '').strip()

        # Update year (only Admin/HOD can change)
        if request.user.is_superuser or profile.role == 'hod':
            student.year = request.POST.get('year', student.year).strip()

        # Handle teacher assignment
        teacher_id = request.POST.get('class_teacher', '')
        if teacher_id:
            teacher = User.objects.filter(id=teacher_id, profile__role='teacher').first()
            student.class_teacher = teacher
        elif profile.role == 'teacher':
            student.class_teacher = request.user

        try:
            student.save()
            messages.success(request, f'Student {student.first_name} updated successfully!')
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')

    context = {
        'student': student,
        'teachers': teachers,
        'YEAR_CHOICES': Student.YEAR_CHOICES,
        'show_year_field': show_year_field,
        'profile': profile,
        'is_admin': request.user.is_superuser,
        'title': 'Edit Student'
    }
    return render(request, 'core/edit_student.html', context)


@login_required
def delete_student(request, student_id):
    """Delete a student"""
    student = get_object_or_404(Student, id=student_id)

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # Check permission
    if not request.user.is_superuser and profile.role != 'hod' and student.class_teacher != request.user:
        messages.error(request, 'Access denied. You can only delete your assigned students.')
        return redirect('student_list')

    student_name = f'{student.first_name} {student.last_name}'

    try:
        student.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting student: {str(e)}')

    return redirect('student_list')


# ===== TEACHER PANEL VIEWS =====
@login_required
def teacher_panel(request):
    """Main teacher dashboard - FIXED VERSION"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = Profile.objects.create(user=request.user, role='teacher')
        messages.info(request, 'Profile created successfully.')

    # Only teachers can access
    if profile.role != 'teacher':
        messages.error(request, 'Access denied. Teacher only.')
        return redirect('dashboard')

    # Check if teacher has assigned year
    if not profile.assigned_year:
        messages.warning(request, 'No year assigned to you. Contact HOD.')
        context = {
            'title': 'Teacher Panel',
            'profile': profile,
            'total_students': 0,
            'present_today': 0,
            'absent_today': 0,
            'late_today': 0,
            'attendance_percentage': 0,
            'students': [],
            'recent_attendance': [],
            'year_name': 'Not Assigned',
            'today': date.today(),
            'message': 'No year assigned. Contact HOD to get a year assignment.'
        }
        return render(request, 'core/teacher_panel.html', context)

    year_name = dict(Student.YEAR_CHOICES).get(profile.assigned_year, f'Year {profile.assigned_year}')
    today = date.today()

    # Get students ASSIGNED TO THIS TEACHER
    students = Student.objects.filter(
        year=profile.assigned_year,
        class_teacher=request.user
    ).order_by('first_name')

    # Get today's attendance for THESE STUDENTS
    today_attendance = Attendance.objects.filter(
        student__in=students,
        date=today
    )


    total_students = students.count()
    present_today = today_attendance.filter(status='present').count()
    absent_today = today_attendance.filter(status='absent').count()
    late_today = today_attendance.filter(status='late').count()


    if total_students > 0:
        attendance_percentage = (present_today / total_students) * 100
    else:
        attendance_percentage = 0


    recent_attendance = Attendance.objects.filter(
        student__in=students
    ).order_by('-date', '-id')[:5]

    context = {
        'title': f'Teacher Panel - {year_name}',
        'profile': profile,
        'year_name': year_name,
        'today': today,
        'total_students': total_students,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_today': late_today,
        'attendance_percentage': attendance_percentage,
        'students': students[:5],  # Show only first 5
        'recent_attendance': recent_attendance,
        'assigned_year': profile.assigned_year,
    }

    return render(request, 'core/teacher_panel.html', context)


@login_required
def view_assigned_students(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')

    if profile.role != 'teacher':
        messages.error(request, 'Access denied. Teacher only.')
        return redirect('dashboard')

    if not profile.assigned_year:
        messages.error(request, 'No year assigned to you. Contact HOD.')
        return redirect('dashboard')

    year_name = dict(Student.YEAR_CHOICES).get(profile.assigned_year, 'Unknown')


    students = Student.objects.filter(
        year=profile.assigned_year,
        class_teacher=request.user
    ).order_by('first_name')


    for student in students:
        student.total_attendance = Attendance.objects.filter(student=student).count()
        student.present_count = Attendance.objects.filter(student=student, status='present').count()
        student.attendance_percentage = (
                student.present_count / student.total_attendance * 100) if student.total_attendance > 0 else 0

    context = {
        'title': f'My Students - {year_name}',
        'students': students,
        'year_name': year_name,
        'assigned_year': profile.assigned_year,
    }

    return render(request, 'core/assign_students.html', context)



@login_required
def mark_attendance(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')


    if profile.role != 'teacher':
        messages.error(request, 'Access denied. Only teachers can mark attendance.')
        return redirect('dashboard')

    if not profile.assigned_year:
        messages.error(request, 'No year assigned to you. Contact HOD.')
        return redirect('dashboard')


    selected_date = request.GET.get('date', '')
    if selected_date:
        try:
            attendance_date = date.fromisoformat(selected_date)
            if attendance_date > date.today():
                messages.error(request, 'Cannot mark attendance for future dates.')
                attendance_date = date.today()
        except ValueError:
            attendance_date = date.today()
    else:
        attendance_date = date.today()

    year_name = dict(Student.YEAR_CHOICES).get(profile.assigned_year, 'Unknown')


    students = Student.objects.filter(
        year=profile.assigned_year,
        class_teacher=request.user
    ).order_by('first_name')

    if not students.exists():
        messages.warning(request, f'No students assigned to you in {year_name}. Contact HOD.')
        return redirect('teacher_panel')


    existing_attendance = {}
    attendance_records = Attendance.objects.filter(
        student__in=students,
        date=attendance_date
    )
    for record in attendance_records:
        existing_attendance[record.student.id] = {
            'status': record.status,
            'remarks': record.remarks
        }

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
            messages.success(request, f'Attendance marked for {success_count} student(s) in {year_name}!')
        return redirect('mark_attendance')

    context = {
        'title': f'Mark Attendance - {year_name}',
        'students': students,
        'year_name': year_name,
        'attendance_date': attendance_date,
        'today': date.today(),
        'existing_attendance': existing_attendance,
    }

    return render(request, 'core/mark_attendance.html', context)


@login_required
def attendance_reports(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')


    try:
        report_month = int(request.GET.get('month', date.today().month))
        report_year = int(request.GET.get('year', date.today().year))
    except ValueError:
        report_month = date.today().month
        report_year = date.today().year


    if request.user.is_superuser or profile.role == 'hod':
        students = Student.objects.all()
    else:

        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(
                year=assigned_year,
                class_teacher=request.user
            ).order_by('first_name')
        else:
            students = Student.objects.none()
            messages.warning(request, 'No year assigned to you.')


    import calendar
    cal = calendar.monthcalendar(report_year, report_month)
    month_name = calendar.month_name[report_month]


    student_calendar_data = []
    for student in students:

        monthly_attendance = Attendance.objects.filter(
            student=student,
            date__year=report_year,
            date__month=report_month
        )


        attendance_by_day = {}
        for attendance in monthly_attendance:
            day = attendance.date.day
            attendance_by_day[day] = {
                'status': attendance.status,
                'remarks': attendance.remarks,
                'date': attendance.date
            }


        total_days = monthly_attendance.count()
        present_days = monthly_attendance.filter(status='present').count()

        if total_days > 0:
            attendance_percentage = (present_days / total_days) * 100
        else:
            attendance_percentage = 0

        student_calendar_data.append({
            'student': student,
            'attendance_by_day': attendance_by_day,
            'total_days': total_days,
            'present_days': present_days,
            'attendance_percentage': round(attendance_percentage, 2),
        })


    prev_month = report_month - 1 if report_month > 1 else 12
    prev_year = report_year if report_month > 1 else report_year - 1
    next_month = report_month + 1 if report_month < 12 else 1
    next_year = report_year if report_month < 12 else report_year + 1


    month_names = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]


    current_year = date.today().year
    year_range = range(current_year - 2, current_year + 1)

    context = {
        'title': f'Attendance Calendar - {month_name} {report_year}',
        'profile': profile,
        'students_data': student_calendar_data,
        'calendar': cal,
        'report_month': report_month,
        'report_year': report_year,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'month_names': month_names,
        'year_range': year_range,
        'is_admin': request.user.is_superuser or profile.role == 'hod',
    }

    return render(request, 'core/attendance_calendar.html', context)




@login_required
def assign_students_to_teachers(request):
    """Admin/HOD: Assign unassigned students to teachers"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # Only HOD/Admin can access
    if not (request.user.is_superuser or profile.role == 'hod'):
        messages.error(request, 'Access denied. Admin/HOD only.')
        return redirect('dashboard')

    if request.method == 'POST':
        # Get all unassigned students
        unassigned_students = Student.objects.filter(class_teacher__isnull=True)
        assigned_count = 0

        for student in unassigned_students:
            # Find teacher for this student's year
            teacher = User.objects.filter(
                profile__role='teacher',
                profile__assigned_year=student.year
            ).first()

            if teacher:
                student.class_teacher = teacher
                student.save()
                assigned_count += 1

        if assigned_count > 0:
            messages.success(request, f'Assigned {assigned_count} students to their teachers!')
        else:
            messages.info(request, 'No unassigned students found.')

        return redirect('student_list')

    # Get statistics
    total_students = Student.objects.count()
    unassigned_students = Student.objects.filter(class_teacher__isnull=True)
    assigned_students = Student.objects.filter(class_teacher__isnull=False)

    # Students by year with teacher assignment status
    year_stats = []
    for year_code, year_name in Student.YEAR_CHOICES:
        students_in_year = Student.objects.filter(year=year_code)
        assigned_in_year = students_in_year.filter(class_teacher__isnull=False)
        unassigned_in_year = students_in_year.filter(class_teacher__isnull=True)

        # Get teacher for this year
        teacher = User.objects.filter(
            profile__role='teacher',
            profile__assigned_year=year_code
        ).first()

        year_stats.append({
            'year_code': year_code,
            'year_name': year_name,
            'total': students_in_year.count(),
            'assigned': assigned_in_year.count(),
            'unassigned': unassigned_in_year.count(),
            'teacher': teacher.username if teacher else 'No teacher'
        })

    context = {
        'title': 'Assign Students to Teachers',
        'total_students': total_students,
        'unassigned_count': unassigned_students.count(),
        'assigned_count': assigned_students.count(),
        'year_stats': year_stats,
    }

    return render(request, 'core/assign_students.html', context)


@login_required
def attendance_list(request):
    """View attendance records - COMPATIBILITY VIEW"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')

    if request.user.is_superuser or profile.role == 'hod':
        # Admin/HOD can see all attendance
        attendances = Attendance.objects.all().order_by('-date')[:100]
    else:
        # Teacher can only see their students' attendance
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(
                year=assigned_year,
                class_teacher=request.user
            )
            attendances = Attendance.objects.filter(
                student__in=students
            ).order_by('-date', 'student__student_id')[:100]
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
def view_assigned_students(request):
    """View students assigned to this teacher"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, role='teacher')

    if profile.role != 'teacher':
        messages.error(request, 'Access denied. Teacher only.')
        return redirect('dashboard')

    if not profile.assigned_year:
        messages.error(request, 'No year assigned to you. Contact HOD.')
        return redirect('dashboard')

    year_name = dict(Student.YEAR_CHOICES).get(profile.assigned_year, 'Unknown')

    # Get students ASSIGNED TO THIS TEACHER
    students = Student.objects.filter(
        year=profile.assigned_year,
        class_teacher=request.user
    ).order_by('first_name')

    # If no students assigned, show all students in that year
    if students.count() == 0:
        students = Student.objects.filter(year=profile.assigned_year).order_by('first_name')
        messages.info(request, f'No students specifically assigned to you. Showing all {students.count()} students in {year_name}.')

    # Add attendance stats for each student
    for student in students:
        student.total_attendance = Attendance.objects.filter(student=student).count()
        student.present_count = Attendance.objects.filter(student=student, status='present').count()
        if student.total_attendance > 0:
            student.attendance_percentage = (student.present_count / student.total_attendance) * 100
        else:
            student.attendance_percentage = 0

    context = {
        'title': f'My Students - {year_name}',
        'students': students,
        'year_name': year_name,
        'assigned_year': profile.assigned_year,
        'total_students': students.count(),
    }

    return render(request, 'core/assign_students.html', context)


# ===== ENHANCED REPORTING MODULE =====
@login_required
def detailed_reports(request):
    """Detailed attendance reports with filters"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # Default date range (current month)
    today = date.today()
    start_date = request.GET.get('start_date', date(today.year, today.month, 1).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())

    year_filter = request.GET.get('year', '')
    teacher_filter = request.GET.get('teacher', '')
    status_filter = request.GET.get('status', '')

    # Base queryset based on role
    if request.user.is_superuser or profile.role == 'hod':
        attendances = Attendance.objects.all()
        students = Student.objects.all()
        teachers = User.objects.filter(profile__role='teacher')
    else:
        # Teacher can only see their students
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(year=assigned_year, class_teacher=request.user)
            attendances = Attendance.objects.filter(student__in=students)
            teachers = User.objects.filter(id=request.user.id)
        else:
            students = Student.objects.none()
            attendances = Attendance.objects.none()
            teachers = User.objects.none()
            messages.warning(request, 'No year assigned to you.')

    # Apply filters
    if start_date:
        start_date_obj = date.fromisoformat(start_date)
        attendances = attendances.filter(date__gte=start_date_obj)
    if end_date:
        end_date_obj = date.fromisoformat(end_date)
        attendances = attendances.filter(date__lte=end_date_obj)
    if year_filter:
        students_in_year = Student.objects.filter(year=year_filter)
        attendances = attendances.filter(student__in=students_in_year)
    if teacher_filter:
        teacher = User.objects.filter(id=teacher_filter, profile__role='teacher').first()
        if teacher:
            students_of_teacher = Student.objects.filter(class_teacher=teacher)
            attendances = attendances.filter(student__in=students_of_teacher)
    if status_filter:
        attendances = attendances.filter(status=status_filter)

    # Calculate statistics
    total_records = attendances.count()
    present_count = attendances.filter(status='present').count()
    absent_count = attendances.filter(status='absent').count()
    late_count = attendances.filter(status='late').count()
    excused_count = attendances.filter(status='excused').count()

    if total_records > 0:
        present_percentage = (present_count / total_records) * 100
        absent_percentage = (absent_count / total_records) * 100
        late_percentage = (late_count / total_records) * 100
        excused_percentage = (excused_count / total_records) * 100
    else:
        present_percentage = absent_percentage = late_percentage = excused_percentage = 0

    # Get top/bottom performing students
    student_stats = []
    student_queryset = students if students.exists() else Student.objects.all()

    for student in student_queryset[:20]:  # Limit to 20 for performance
        student_attendance = attendances.filter(student=student)
        student_total = student_attendance.count()
        student_present = student_attendance.filter(status='present').count()

        if student_total > 0:
            student_percentage = (student_present / student_total) * 100
        else:
            student_percentage = 0

        student_stats.append({
            'student': student,
            'total': student_total,
            'present': student_present,
            'percentage': round(student_percentage, 2),
            'year': student.get_year_display(),
            'teacher': student.class_teacher.username if student.class_teacher else 'Not Assigned'
        })

    # Sort by percentage (descending)
    student_stats.sort(key=lambda x: x['percentage'], reverse=True)

    context = {
        'title': 'Detailed Attendance Reports',
        'profile': profile,
        'attendances': attendances.order_by('-date')[:50],  # Limit to 50 records
        'student_stats': student_stats,
        'start_date': start_date,
        'end_date': end_date,
        'year_filter': year_filter,
        'teacher_filter': teacher_filter,
        'status_filter': status_filter,
        'YEAR_CHOICES': Student.YEAR_CHOICES,
        'teachers': teachers,
        'STATUS_CHOICES': Attendance.STATUS_CHOICES,
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'excused_count': excused_count,
        'present_percentage': round(present_percentage, 2),
        'absent_percentage': round(absent_percentage, 2),
        'late_percentage': round(late_percentage, 2),
        'excused_percentage': round(excused_percentage, 2),
        'is_admin': request.user.is_superuser or profile.role == 'hod',
    }

    return render(request, 'core/detailed_reports.html', context)


@login_required
def monthly_reports(request):
    """Monthly attendance summary reports"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # Get year and month from request or use current
    report_year = request.GET.get('year', date.today().year)
    report_month = request.GET.get('month', date.today().month)

    try:
        report_year = int(report_year)
        report_month = int(report_month)
    except ValueError:
        report_year = date.today().year
        report_month = date.today().month

    # Base queryset based on role
    if request.user.is_superuser or profile.role == 'hod':
        students = Student.objects.all()
    else:
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(year=assigned_year, class_teacher=request.user)
        else:
            students = Student.objects.none()
            messages.warning(request, 'No year assigned to you.')

    # Calculate monthly statistics for each student
    monthly_data = []
    for student in students:
        # Get attendance for the month
        monthly_attendance = Attendance.objects.filter(
            student=student,
            date__year=report_year,
            date__month=report_month
        )

        total_days = monthly_attendance.count()
        present_days = monthly_attendance.filter(status='present').count()
        absent_days = monthly_attendance.filter(status='absent').count()
        late_days = monthly_attendance.filter(status='late').count()
        excused_days = monthly_attendance.filter(status='excused').count()

        if total_days > 0:
            attendance_percentage = (present_days / total_days) * 100
        else:
            attendance_percentage = 0

        monthly_data.append({
            'student': student,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'excused_days': excused_days,
            'attendance_percentage': round(attendance_percentage, 2),
        })

    # Calculate overall statistics
    total_students = len(monthly_data)
    if total_students > 0:
        avg_attendance = sum(item['attendance_percentage'] for item in monthly_data) / total_students
        total_present = sum(item['present_days'] for item in monthly_data)
        total_absent = sum(item['absent_days'] for item in monthly_data)
        total_late = sum(item['late_days'] for item in monthly_data)
        total_excused = sum(item['excused_days'] for item in monthly_data)
        total_days_all = sum(item['total_days'] for item in monthly_data)

        if total_days_all > 0:
            overall_percentage = (total_present / total_days_all) * 100
        else:
            overall_percentage = 0
    else:
        avg_attendance = overall_percentage = total_present = total_absent = total_late = total_excused = 0

    # Year and month choices for dropdown
    current_year = date.today().year
    year_choices = list(range(current_year - 2, current_year + 1))
    month_choices = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    context = {
        'title': f'Monthly Report - {month_choices[report_month - 1][1]} {report_year}',
        'profile': profile,
        'monthly_data': monthly_data,
        'report_year': report_year,
        'report_month': report_month,
        'year_choices': year_choices,
        'month_choices': month_choices,
        'total_students': total_students,
        'avg_attendance': round(avg_attendance, 2),
        'overall_percentage': round(overall_percentage, 2),
        'total_present': total_present,
        'total_absent': total_absent,
        'total_late': total_late,
        'total_excused': total_excused,
        'is_admin': request.user.is_superuser or profile.role == 'hod',
    }

    return render(request, 'core/monthly_reports.html', context)


@login_required
def student_wise_reports(request):
    """Student-wise detailed attendance reports"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    student_id = request.GET.get('student_id', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', date.today().isoformat())

    # Get students based on role
    if request.user.is_superuser or profile.role == 'hod':
        students = Student.objects.all()
    else:
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(year=assigned_year, class_teacher=request.user)
        else:
            students = Student.objects.none()
            messages.warning(request, 'No year assigned to you.')

    student = None
    attendance_records = []
    summary = {}

    if student_id:
        student = get_object_or_404(Student, id=student_id)

        # Check permission
        if not (request.user.is_superuser or profile.role == 'hod' or
                (student.class_teacher == request.user)):
            messages.error(request, 'Access denied.')
            return redirect('student_wise_reports')

        # Get attendance with date filter
        attendance_qs = Attendance.objects.filter(student=student)

        if start_date:
            start_date_obj = date.fromisoformat(start_date)
            attendance_qs = attendance_qs.filter(date__gte=start_date_obj)
        if end_date:
            end_date_obj = date.fromisoformat(end_date)
            attendance_qs = attendance_qs.filter(date__lte=end_date_obj)

        attendance_records = attendance_qs.order_by('-date')

        # Calculate summary
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        late_days = attendance_records.filter(status='late').count()
        excused_days = attendance_records.filter(status='excused').count()

        if total_days > 0:
            attendance_percentage = (present_days / total_days) * 100
        else:
            attendance_percentage = 0

        summary = {
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'excused_days': excused_days,
            'attendance_percentage': round(attendance_percentage, 2),
            'start_date': start_date,
            'end_date': end_date,
        }

    context = {
        'title': 'Student-wise Reports',
        'profile': profile,
        'students': students,
        'selected_student': student,
        'attendance_records': attendance_records,
        'summary': summary,
        'start_date': start_date,
        'end_date': end_date,
        'student_id': student_id,
        'is_admin': request.user.is_superuser or profile.role == 'hod',
    }

    return render(request, 'core/student_wise_reports.html', context)


@login_required
def export_report_csv(request):
    """Export attendance report as CSV"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # Get filter parameters
    report_type = request.GET.get('type', 'detailed')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    year_filter = request.GET.get('year', '')

    import csv
    from django.http import HttpResponse
    import io

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{date.today()}.csv"'

    # Create CSV writer
    writer = csv.writer(response)

    if report_type == 'detailed':
        # Detailed report
        writer.writerow(['Student ID', 'Student Name', 'Year', 'Teacher', 'Date', 'Status', 'Remarks', 'Marked By'])

        # Get data based on role
        if request.user.is_superuser or profile.role == 'hod':
            attendances = Attendance.objects.all()
        else:
            assigned_year = profile.assigned_year
            if assigned_year:
                students = Student.objects.filter(year=assigned_year, class_teacher=request.user)
                attendances = Attendance.objects.filter(student__in=students)
            else:
                attendances = Attendance.objects.none()

        # Apply filters
        if start_date:
            attendances = attendances.filter(date__gte=date.fromisoformat(start_date))
        if end_date:
            attendances = attendances.filter(date__lte=date.fromisoformat(end_date))
        if year_filter:
            students_in_year = Student.objects.filter(year=year_filter)
            attendances = attendances.filter(student__in=students_in_year)

        for attendance in attendances.order_by('date'):
            writer.writerow([
                attendance.student.student_id,
                f"{attendance.student.first_name} {attendance.student.last_name}",
                attendance.student.year,
                attendance.student.class_teacher.username if attendance.student.class_teacher else 'N/A',
                attendance.date,
                attendance.status,
                attendance.remarks,
                attendance.marked_by.username
            ])

    elif report_type == 'summary':
        # Summary report
        writer.writerow(
            ['Student ID', 'Student Name', 'Year', 'Teacher', 'Total Days', 'Present', 'Absent', 'Late', 'Excused',
             'Attendance %'])

        # Get students based on role
        if request.user.is_superuser or profile.role == 'hod':
            students = Student.objects.all()
        else:
            assigned_year = profile.assigned_year
            if assigned_year:
                students = Student.objects.filter(year=assigned_year, class_teacher=request.user)
            else:
                students = Student.objects.none()

        for student in students:
            # Get attendance with date filter
            attendances = Attendance.objects.filter(student=student)
            if start_date:
                attendances = attendances.filter(date__gte=date.fromisoformat(start_date))
            if end_date:
                attendances = attendances.filter(date__lte=date.fromisoformat(end_date))
            if year_filter and student.year != year_filter:
                continue

            total_days = attendances.count()
            present_days = attendances.filter(status='present').count()
            absent_days = attendances.filter(status='absent').count()
            late_days = attendances.filter(status='late').count()
            excused_days = attendances.filter(status='excused').count()

            if total_days > 0:
                attendance_percentage = (present_days / total_days) * 100
            else:
                attendance_percentage = 0

            writer.writerow([
                student.student_id,
                f"{student.first_name} {student.last_name}",
                student.year,
                student.class_teacher.username if student.class_teacher else 'N/A',
                total_days,
                present_days,
                absent_days,
                late_days,
                excused_days,
                round(attendance_percentage, 2)
            ])

    return response


@login_required
def attendance_analytics(request):
    """Attendance analytics with charts"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        role = 'admin' if request.user.is_superuser else 'teacher'
        profile = Profile.objects.create(user=request.user, role=role)

    # Default to current month
    today = date.today()
    month = request.GET.get('month', today.month)
    year = request.GET.get('year', today.year)

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = today.month
        year = today.year

    # Get data based on role
    if request.user.is_superuser or profile.role == 'hod':
        students = Student.objects.all()
        attendances = Attendance.objects.filter(date__year=year, date__month=month)
    else:
        assigned_year = profile.assigned_year
        if assigned_year:
            students = Student.objects.filter(year=assigned_year, class_teacher=request.user)
            attendances = Attendance.objects.filter(
                student__in=students,
                date__year=year,
                date__month=month
            )
        else:
            students = Student.objects.none()
            attendances = Attendance.objects.none()
            messages.warning(request, 'No year assigned to you.')

    # Calculate daily attendance
    daily_data = {}
    for day in range(1, 32):
        try:
            day_date = date(year, month, day)
            day_attendances = attendances.filter(date=day_date)
            total = day_attendances.count()
            present = day_attendances.filter(status='present').count()

            if total > 0:
                percentage = (present / total) * 100
            else:
                percentage = 0

            daily_data[day] = {
                'date': day_date,
                'total': total,
                'present': present,
                'percentage': round(percentage, 2)
            }
        except ValueError:
            # Invalid day for this month (e.g., day 31 in February)
            pass

    # Calculate status distribution
    status_counts = {
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
        'excused': attendances.filter(status='excused').count(),
    }

    # Year and month choices
    current_year = today.year
    year_choices = list(range(current_year - 2, current_year + 1))
    month_choices = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    context = {
        'title': 'Attendance Analytics',
        'profile': profile,
        'daily_data': daily_data,
        'status_counts': status_counts,
        'month': month,
        'year': year,
        'year_choices': year_choices,
        'month_choices': month_choices,
        'total_students': students.count(),
        'total_attendances': attendances.count(),
        'is_admin': request.user.is_superuser or profile.role == 'hod',
    }

    return render(request, 'core/attendance_analytics.html', context)