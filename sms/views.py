
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db.models import Count, Q

from .models import Batch, Student, Attendance
from .forms import StudentForm, AttendanceForm

from django.shortcuts import redirect

def home(request):
    return redirect('student_list')

# Student Registration
def register_student(request):

    if request.method == 'POST':
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Student registered successfully!')
            return redirect('student_list')

    else:
        form = StudentForm()

    return render(
        request,
        'sms/register_student.html',
        {'form': form}
    )


# Student List
def student_list(request):

    students = Student.objects.select_related('batch').all()

    return render(
        request,
        'sms/student_list.html',
        {'students': students}
    )


# Batch List
def batch_list(request):

    batches = Batch.objects.annotate(
        student_count=Count('students')
    )

    return render(
        request,
        'sms/batch_list.html',
        {'batches': batches}
    )


# Take Attendance
def take_attendance(request, batch_id):

    batch = get_object_or_404(Batch, id=batch_id)

    students = Student.objects.filter(batch=batch)

    today = timezone.localdate()

    # Check whether attendance is already recorded
    already_recorded = Attendance.objects.filter(
        student__batch=batch,
        date=today
    ).exists()

    if already_recorded:
        messages.error(
            request,
            'Attendance for this batch has already been recorded today!'
        )

        return redirect('batch_list')

    attendance_forms = []

    if request.method == 'POST':

        valid_forms = []

        # Validate all student attendance forms first
        for student in students:

            form = AttendanceForm(
                request.POST,
                prefix=str(student.id)
            )

            if form.is_valid():
                valid_forms.append((student, form))
            else:
                attendance_forms.append({
                    'student': student,
                    'form': form
                })

        if len(valid_forms) == students.count() and students.exists():

            try:
                with transaction.atomic():

                    # Recheck inside transaction before saving
                    if Attendance.objects.filter(
                        student__batch=batch,
                        date=today
                    ).exists():
                        messages.error(
                            request,
                            'Attendance has already been recorded today!'
                        )
                        return redirect('batch_list')

                    for student, form in valid_forms:

                        attendance = form.save(commit=False)
                        attendance.student = student
                        attendance.date = today
                        attendance.save()

                messages.success(
                    request,
                    'Attendance recorded successfully!'
                )

                return redirect(
                    'attendance_report',
                    batch_id=batch.id
                )

            except IntegrityError:
                messages.error(
                    request,
                    'Attendance already exists for one or more students today.'
                )
                return redirect('batch_list')

        else:
            messages.error(
                request,
                'Please select a valid attendance status for every student.'
            )

    else:

        for student in students:

            form = AttendanceForm(
                prefix=str(student.id)
            )

            attendance_forms.append({
                'student': student,
                'form': form
            })

    return render(
        request,
        'sms/take_attendance.html',
        {
            'batch': batch,
            'attendance_forms': attendance_forms,
            'today': today
        }
    )


# Batch Attendance Report
def attendance_report(request, batch_id):

    batch = get_object_or_404(Batch, id=batch_id)

    students = Student.objects.filter(batch=batch)

    attendance_summary = []

    for student in students:

        records = Attendance.objects.filter(student=student)

        summary = records.aggregate(
            present=Count('id', filter=Q(status='Present')),
            absent=Count('id', filter=Q(status='Absent')),
            late=Count('id', filter=Q(status='Late'))
        )

        attendance_summary.append({
            'student': student,
            'present': summary['present'],
            'absent': summary['absent'],
            'late': summary['late'],
            'total': records.count()
        })

    return render(
        request,
        'sms/attendance_report.html',
        {
            'batch': batch,
            'attendance_summary': attendance_summary
        }
    )


# Individual Student Attendance Report
def student_attendance_report(request, student_id):

    student = get_object_or_404(Student, id=student_id)

    attendance_records = Attendance.objects.filter(
        student=student
    ).order_by('-date')

    summary = attendance_records.aggregate(
        present=Count('id', filter=Q(status='Present')),
        absent=Count('id', filter=Q(status='Absent')),
        late=Count('id', filter=Q(status='Late'))
    )

    return render(
        request,
        'sms/student_attendance_report.html',
        {
            'student': student,
            'attendance_records': attendance_records,
            'summary': summary
        }
    )
