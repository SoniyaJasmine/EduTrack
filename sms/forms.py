
from django import forms
from .models import Student, Attendance


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'batch'
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'batch': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ['status']

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
