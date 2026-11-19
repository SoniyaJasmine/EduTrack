
from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    # Student URLs
    path(
        'register/',
        views.register_student,
        name='register_student'
    ),

    path(
        'students/',
        views.student_list,
        name='student_list'
    ),

    # Batch URLs
    path(
        'batches/',
        views.batch_list,
        name='batch_list'
    ),

    path(
        'batches/<int:batch_id>/attendance/',
        views.take_attendance,
        name='take_attendance'
    ),

    # Attendance Reports
    path(
        'batches/<int:batch_id>/report/',
        views.attendance_report,
        name='attendance_report'
    ),

    path(
        'students/<int:student_id>/attendance/',
        views.student_attendance_report,
        name='student_attendance_report'
    ),
]
