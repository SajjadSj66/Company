import os
from django import forms
from .models import ContactMessage
from django.core.validators import RegexValidator
from .models import ContactMessage, CourseRegistration, ContactRequest,Collaboration

class CollaborationForm(forms.ModelForm):
    """
    فرم ارسال رزومه برای همکاری (صفحه work_with_us)
    """
    class Meta:
        model = Collaboration
        fields = ['full_name', 'phone', 'email', 'message', 'work_choices', 'resume_file', 'portfolio']
        widgets = {
            'resume_file': forms.FileInput(attrs={'id': 'fileInput','accept': '.pdf,.doc,.docx,.txt',}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09123456789'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}),
            'work_choices': forms.Select(attrs={'class': 'form-control'}),
            'portfolio': forms.URLInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'پیام خود را بنویسید'})
        }

    def clean_resume_file(self):
        file = self.cleaned_data.get('resume_file')
        if not file:
            raise forms.ValidationError('لطفاً یک فایل انتخاب کنید.')
        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError('حجم فایل نباید بیشتر از 10 مگابایت باشد.')
        return file



class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['full_name', 'phone_or_email', 'work_name', 'project_choices', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_or_email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09123456789'}),
            'work_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_choices': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'پیام خود را بنویسید'})
        }


class CourseRegistrationForm(forms.ModelForm):
    """
    فرم ثبت‌نام دوره آموزشی
    """
    # فیلدهای اضافی برای اعتبارسنجی
    mobile = forms.CharField(
        label='تلفن همراه',
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^09[0-9]{9}$',
                message='شماره موبایل باید با 09 شروع و 11 رقم باشد'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': '09123456789',
            'id': 'mobile'
        })
    )

    national_id = forms.CharField(
        label='کد ملی',
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{10}$',
                message='کد ملی باید ۱۰ رقم باشد'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'کد ملی ۱۰ رقمی',
            'id': 'nationalCode',
            'maxlength': '10'
        })
    )

    # فیلدهای حوزه انتخابی (چند انتخابی)
    domains = forms.MultipleChoiceField(
        label='حوزه‌های انتخابی',
        choices=CourseRegistration.DOMAIN_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'domain-cards'
        })
    )

    class Meta:
        model = CourseRegistration
        fields = [
            'first_name', 'last_name', 'father_name',
            'national_id', 'shenasname_no', 'shenasname_place',
            'education_level', 'major',
            'mobile', 'registration_date', 'domains'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'نام خود را وارد کنید', 'id': 'firstName'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'نام خانوادگی خود را وارد کنید', 'id': 'lastName'}),
            'father_name': forms.TextInput(attrs={'placeholder': 'نام پدر', 'id': 'fatherName'}),
            'shenasname_no': forms.TextInput(attrs={'placeholder': 'شماره شناسنامه', 'id': 'birthCertNo'}),
            'shenasname_place': forms.TextInput(attrs={'placeholder': 'محل صدور شناسنامه', 'id': 'issuePlace'}),
            'education_level': forms.Select(attrs={'id': 'educationLevel'}),
            'major': forms.TextInput(attrs={'placeholder': 'رشته تحصیلی خود را بنویسید', 'id': 'studyField'}),
            'registration_date': forms.TextInput(attrs={
                'id': 'registrationDate',
                'readonly': 'readonly',
                'class': 'persian-date-input'
            }),
        }

    def clean_domains(self):
        domains = self.cleaned_data.get('domains')
        if not domains:
            raise forms.ValidationError(
                'لطفاً حداقل یک حوزه آموزشی انتخاب کنید')
        # تبدیل لیست به رشته با کاما جدا شده
        return ','.join(domains)


class PhoneLoginForm(forms.Form):
    """فرم ورود با شماره موبایل"""
    phone = forms.CharField(
        label='شماره موبایل',
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^09[0-9]{9}$',
                message='شماره موبایل باید با 09 شروع و 11 رقم باشد'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'phone-input',
            'placeholder': '09123456789',
            'maxlength': '11'
        })
    )


class OTPVerifyForm(forms.Form):
    """فرم تایید کد OTP"""
    code = forms.CharField(
        label='کد تایید',
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'otp-input',
            'maxlength': '6',
            'pattern': '[0-9]*'
        })
    )


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['fullname', 'phone', 'email', 'service_type', 'message']
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09123456789'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'پیام خود را بنویسید'})
        }
