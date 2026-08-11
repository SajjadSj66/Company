from django import forms
from .models import *

# فرم جستجو و فیلتر دوره‌ها
class CourseSearchForm(forms.Form):
    q = forms.CharField(
        label='جستجو',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'جستجوی دوره...',
        })
    )
    category = forms.ChoiceField(
        label='دسته‌بندی',
        choices=[('', 'همه دسته‌ها')] + Course.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'category-select'})
    )

# فرم مقداردهی تعداد آیتم در سبد خرید (برای آپدیت)
class CartItemUpdateForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'max': 10, 'class': 'quantity-input'})
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError('تعداد باید حداقل ۱ باشد.')
        if quantity > 10:
            raise forms.ValidationError('حداکثر تعداد مجاز ۱۰ است.')
        return quantity

# فرم تسویه حساب (ثبت سفارش)
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone', 
            'address', 'postal_code', 'city', 'state'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام و نام خانوادگی'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '۰۹۱۲xxxxxxx'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'آدرس کامل'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد پستی ۱۰ رقمی'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شهر'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'استان'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # اگر کاربر وارد شده باشد، فیلدها را با اطلاعات پروفایل و کاربر پر می‌کنیم
        if self.user and self.user.is_authenticated:
            profile = self.user.profile
            self.fields['full_name'].initial = f"{self.user.first_name} {self.user.last_name}".strip()
            if not self.fields['full_name'].initial:
                self.fields['full_name'].initial = self.user.username
            self.fields['email'].initial = self.user.email
            self.fields['phone'].initial = profile.phone
            self.fields['address'].initial = profile.address
            self.fields['postal_code'].initial = profile.postal_code
            self.fields['city'].initial = profile.city
            self.fields['state'].initial = profile.state

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # اعتبارسنجی ساده شماره ایرانی
        if phone and not phone.isdigit():
            raise forms.ValidationError('شماره تلفن باید فقط شامل اعداد باشد.')
        return phone

class SeoSignUpForm(forms.ModelForm):
    class Meta:
        model = SeoSignUp
        fields = ['full_name', 'phone', 'educate']
        wdgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'educate': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AiSignUpForm(forms.ModelForm):
    class Meta:
        model = AiSignUp
        fields = ['full_name', 'phone', 'educate']
        wdgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'educate': forms.TextInput(attrs={'class': 'form-control'}),
        }


class WordpressSignUpForm(forms.ModelForm):
    class Meta:
        model = WordpressSignUp
        fields = ['full_name', 'phone', 'educate']
        wdgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'educate': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UiSignUpForm(forms.ModelForm):
    class Meta:
        model = UiSignUp
        fields = ['full_name', 'phone', 'educate']
        wdgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'educate': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BackSignUpForm(forms.ModelForm):
    class Meta:
        model = BackSignUp
        fields = ['full_name', 'phone', 'educate']
        wdgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'educate': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FrontSignUpForm(forms.ModelForm):
    class Meta:
        model = FrontSignUp
        fields = ['full_name', 'phone', 'educate']
        wdgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'educate': forms.TextInput(attrs={'class': 'form-control'}),
        }