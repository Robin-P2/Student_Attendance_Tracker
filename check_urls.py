# check_urls.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.urls import get_resolver

print("=== CHECKING URLS ===")
print()

# Get all URL patterns
resolver = get_resolver()


def list_urls(patterns, prefix=''):
    for pattern in patterns:
        if hasattr(pattern, 'pattern'):
            if hasattr(pattern, 'name') and pattern.name:
                print(f"{prefix}/{pattern.pattern} -> {pattern.name}")
            if hasattr(pattern, 'url_patterns'):
                list_urls(pattern.url_patterns, f"{prefix}/{pattern.pattern}")


list_urls(resolver.url_patterns)

print()
print("=== CHECKING FOR 'attendance_reports' URL ===")

# Check specifically for attendance_reports
from django.urls import reverse, NoReverseMatch

try:
    url = reverse('attendance_reports')
    print(f"✓ Found 'attendance_reports' URL: {url}")
except NoReverseMatch:
    print("✗ 'attendance_reports' URL not found!")

print()
print("=== CHECKING FOR 'reports' URL ===")
try:
    url = reverse('reports')
    print(f"✓ Found 'reports' URL: {url}")
except NoReverseMatch:
    print("✗ 'reports' URL not found!")