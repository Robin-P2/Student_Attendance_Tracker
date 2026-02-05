# setup_database.py - FIXED VERSION
import os
import sys
import django
from pathlib import Path
import datetime


def setup_database():
    print("=" * 60)
    print("COMPLETE DATABASE SETUP FOR STUDENT ATTENDANCE SYSTEM")
    print("=" * 60)

    # 1. Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
    django.setup()

    from django.core.management import execute_from_command_line
    from django.contrib.auth.models import User
    from django.db.models import Count  # ADD THIS IMPORT
    from core.models import Profile, Student
    from attendance.models import Attendance

    print("\n📊 STEP 1: Running migrations...")
    print("-" * 40)

    # Run migrations
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])

    print("\n✅ Migrations completed!")

    print("\n👥 STEP 2: Creating users...")
    print("-" * 40)

    # Create Super Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@school.edu',
            password='admin123',
            first_name='System',
            last_name='Administrator'
        )
        print(f"✅ Created Super Admin: admin / admin123")
    else:
        print(f"⏩ Admin already exists")
        admin = User.objects.get(username='admin')

    # Create HOD
    if not User.objects.filter(username='hod').exists():
        hod = User.objects.create_user(
            username='hod',
            email='hod@school.edu',
            password='hod123',
            first_name='Head',
            last_name='Department',
            is_staff=True
        )
        Profile.objects.create(user=hod, role='hod')
        print(f"✅ Created HOD: hod / hod123")
    else:
        print(f"⏩ HOD already exists")
        hod = User.objects.get(username='hod')

    # Create Teachers
    teachers_data = [
        {'username': 'teacher1', 'first': 'John', 'last': 'Doe', 'year': '1'},
        {'username': 'teacher2', 'first': 'Jane', 'last': 'Smith', 'year': '2'},
        {'username': 'teacher3', 'first': 'Robert', 'last': 'Johnson', 'year': '3'},
        {'username': 'teacher4', 'first': 'Sarah', 'last': 'Williams', 'year': '4'},
    ]

    teachers = {}  # Store teacher objects by year
    for teacher in teachers_data:
        if not User.objects.filter(username=teacher['username']).exists():
            user = User.objects.create_user(
                username=teacher['username'],
                email=f"{teacher['username']}@school.edu",
                password='teacher123',
                first_name=teacher['first'],
                last_name=teacher['last'],
                is_staff=True
            )
            Profile.objects.create(
                user=user,
                role='teacher',
                assigned_year=teacher['year']
            )
            teachers[teacher['year']] = user  # Store by year
            print(f"✅ Created Teacher: {teacher['username']} / teacher123 (Year {teacher['year']})")
        else:
            print(f"⏩ {teacher['username']} already exists")
            user = User.objects.get(username=teacher['username'])
            teachers[teacher['year']] = user

    print("\n🎓 STEP 3: Creating sample students...")
    print("-" * 40)

    # Sample student data
    sample_students = [
        # Year 1 Students
        {'id': 'STU001', 'first': 'Alice', 'last': 'Brown', 'year': '1', 'email': 'alice@school.edu'},
        {'id': 'STU002', 'first': 'Bob', 'last': 'Davis', 'year': '1', 'email': 'bob@school.edu'},
        {'id': 'STU003', 'first': 'Charlie', 'last': 'Miller', 'year': '1', 'email': 'charlie@school.edu'},
        # Year 2 Students
        {'id': 'STU004', 'first': 'Diana', 'last': 'Wilson', 'year': '2', 'email': 'diana@school.edu'},
        {'id': 'STU005', 'first': 'Edward', 'last': 'Moore', 'year': '2', 'email': 'edward@school.edu'},
        # Year 3 Students
        {'id': 'STU006', 'first': 'Fiona', 'last': 'Taylor', 'year': '3', 'email': 'fiona@school.edu'},
        {'id': 'STU007', 'first': 'George', 'last': 'Anderson', 'year': '3', 'email': 'george@school.edu'},
        # Year 4 Students
        {'id': 'STU008', 'first': 'Hannah', 'last': 'Thomas', 'year': '4', 'email': 'hannah@school.edu'},
        {'id': 'STU009', 'first': 'Ian', 'last': 'Jackson', 'year': '4', 'email': 'ian@school.edu'},
        {'id': 'STU010', 'first': 'Jessica', 'last': 'White', 'year': '4', 'email': 'jessica@school.edu'},
    ]

    created_students = 0
    all_students = []
    for student_data in sample_students:
        if not Student.objects.filter(student_id=student_data['id']).exists():
            # Get teacher for this year
            teacher = teachers.get(student_data['year'])

            student = Student.objects.create(
                student_id=student_data['id'],
                first_name=student_data['first'],
                last_name=student_data['last'],
                year=student_data['year'],
                email=student_data['email'],
                phone='123-456-7890',
                address=f"123 {student_data['last']} Street, City",
                class_teacher=teacher
            )
            created_students += 1
            all_students.append(student)
            print(
                f"✅ Created Student: {student_data['id']} - {student_data['first']} {student_data['last']} (Year {student_data['year']})")
        else:
            student = Student.objects.get(student_id=student_data['id'])
            all_students.append(student)

    print(f"\n📈 Created/Found {len(all_students)} students")

    print("\n📅 STEP 4: Creating sample attendance records...")
    print("-" * 40)

    # Create some attendance records for today
    today = datetime.date.today()

    # We'll mark attendance for all students, each by their class teacher
    attendance_count = 0

    for student in all_students:
        # Get the teacher for this student's year
        teacher = teachers.get(student.year)

        if teacher:
            # Check if attendance already exists for today
            if not Attendance.objects.filter(student=student, date=today).exists():
                try:
                    Attendance.objects.create(
                        student=student,
                        date=today,
                        status='present',  # Mark all as present for demo
                        marked_by=teacher,
                        remarks='System generated sample data'
                    )
                    attendance_count += 1
                    print(f"✅ Marked attendance for {student.first_name} {student.last_name} by {teacher.username}")
                except Exception as e:
                    print(f"❌ Error marking attendance for {student.first_name}: {str(e)}")

    print(f"\n📊 Created {attendance_count} attendance records for {today}")

    # Also create some past attendance records
    print("\n🗓️  Creating past attendance records...")

    past_dates = [
        today - datetime.timedelta(days=1),
        today - datetime.timedelta(days=2),
        today - datetime.timedelta(days=3),
    ]

    past_attendance_count = 0
    for past_date in past_dates:
        # Mark attendance for 3 random students on each past date
        for i, student in enumerate(all_students[:3]):
            teacher = teachers.get(student.year)
            if teacher and not Attendance.objects.filter(student=student, date=past_date).exists():
                try:
                    # Alternate statuses for variety
                    statuses = ['present', 'absent', 'late']
                    status = statuses[i % len(statuses)]

                    Attendance.objects.create(
                        student=student,
                        date=past_date,
                        status=status,
                        marked_by=teacher,
                        remarks=f'Sample data for {past_date}'
                    )
                    past_attendance_count += 1
                except Exception as e:
                    pass  # Silently skip errors for past dates

    print(f"✅ Created {past_attendance_count} past attendance records")

    print("\n📊 STEP 5: Database Summary")
    print("-" * 40)

    # Count all records
    total_users = User.objects.count()
    total_profiles = Profile.objects.count()
    total_students = Student.objects.count()
    total_attendance = Attendance.objects.count()

    print(f"Total Users: {total_users}")
    print(f"Total Profiles: {total_profiles}")
    print(f"Total Students: {total_students}")
    print(f"Total Attendance Records: {total_attendance}")

    # Show attendance by status - FIXED THIS LINE
    if total_attendance > 0:
        print("\n📈 Attendance by Status:")
        status_counts = Attendance.objects.values('status').annotate(count=Count('id'))  # FIXED
        for item in status_counts:
            print(f"  {item['status'].title()}: {item['count']}")

    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)

    print("\n🔑 LOGIN CREDENTIALS:")
    print("-" * 30)
    print("Super Admin: admin / admin123")
    print("HOD: hod / hod123")
    print("Teachers: teacher1, teacher2, etc. / teacher123")

    print("\n🌐 ACCESS LINKS:")
    print("-" * 30)
    print("Admin Panel: http://127.0.0.1:8000/admin/")
    print("Login Page: http://127.0.0.1:8000/login/")
    print("Dashboard: http://127.0.0.1:8000/dashboard/")

    print("\n📊 SAMPLE DATA CREATED:")
    print("-" * 30)
    print(f"• {total_users} users (admin, hod, 4 teachers)")
    print(f"• {total_students} students (distributed across 4 years)")
    print(f"• {total_attendance} attendance records (today + past 3 days)")

    print("\n🚀 Next steps:")
    print("1. Run: python manage.py runserver")
    print("2. Open: http://127.0.0.1:8000/")
    print("3. Login with credentials above")
    print("4. Change passwords after first login")
    print("=" * 60)


if __name__ == "__main__":
    setup_database()