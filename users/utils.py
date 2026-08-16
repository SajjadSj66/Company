# users/utils.py
import random
import datetime
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from .models import UserProfile, OTPCode


def generate_otp():
    """تولید کد تایید ۶ رقمی یکبار مصرف"""
    return f"{random.randint(100000, 999999)}"


import requests
from django.conf import settings


class SmsIrError(Exception):
    """خطای مربوط به ارسال پیامک از طریق SMS.ir"""
    pass


def send_sms(phone, code):
    """
    ارسال کد تایید از طریق SMS.ir (سرویس Verify/OTP)
    در صورت موفقیت True برمی‌گرداند، در غیر این صورت SmsIrError raise می‌کند
    """
    # گرفتن و پاک‌سازی API key از settings
    api_key = getattr(settings, "SMSIR_API_KEY", "")
    api_key = api_key.strip() if isinstance(api_key, str) else ""
    if not api_key:
        raise SmsIrError("API key برای SMS.ir تنظیم نشده یا خالی است")

    template_id = getattr(settings, "SMSIR_TEMPLATE_ID", 0)
    if not template_id:
        raise SmsIrError("Template ID برای SMS.ir تنظیم نشده است")

    url = "https://api.sms.ir/v1/send/verify"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-KEY": api_key,
    }

    payload = {
        "mobile": phone,
        "templateId": int(template_id),
        "parameters": [{"name": "code", "value": str(code)}],
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        raise SmsIrError(f"خطا در اتصال به SMS.ir: {e}")

    # بررسی کد وضعیت HTTP
    try:
        data = response.json()
    except ValueError:
        raise SmsIrError(f"پاسخ نامعتبر از SMS.ir (status {response.status_code})")

    # ساختار پاسخ SMS.ir: status == 1 یعنی موفق
    if response.status_code != 200 or data.get("status") != 1:
        message = data.get("message", "خطای نامشخص")
        raise SmsIrError(f"ارسال پیامک ناموفق بود: {message} (status={data.get('status')})")

    return True

def get_or_create_user_by_phone(phone):
    """
    دریافت یا ایجاد کاربر بر اساس شماره موبایل
    بازگشت: (user, created)
    """
    with transaction.atomic():
        # 1. اول ببین پروفایلی با این شماره وجود داره؟
        try:
            profile = UserProfile.objects.select_related('user').get(phone=phone)
            return profile.user, False
        except UserProfile.DoesNotExist:
            pass
        
        # 2. ببین کاربری با این شماره به عنوان username وجود داره؟
        try:
            user = User.objects.get(username=phone)
        except User.DoesNotExist:
            # 3. هیچی نیست، همه رو از صفر بساز
            user = User.objects.create_user(username=phone, password=None)
            UserProfile.objects.create(
                user=user,
                phone=phone,
                is_phone_verified=False
            )
            return user, True
        
        # 4. کاربر وجود داره، پروفایل بساز
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': phone,
                'is_phone_verified': False
            }
        )
        
        # اگه پروفایل قبلاً وجود داشته ولی شماره‌ش فرق داره، آپدیت کن
        if not created and profile.phone != phone:
            profile.phone = phone
            profile.save()
        
        return user, False


def create_otp_code(user, phone):
    """ایجاد کد تایید جدید برای کاربر"""
    # کدهای قبلی استفاده نشده رو منقضی کن
    OTPCode.objects.filter(user=user, is_used=False).update(is_used=True)
    
    code = generate_otp()
    expires_at = timezone.now() + datetime.timedelta(minutes=5)
    
    otp = OTPCode.objects.create(
        user=user,
        phone=phone,
        code=code,
        expires_at=expires_at
    )
    
    return otp


def verify_otp_code(phone, code):
    """
    بررسی اعتبار کد تایید
    بازگشت: (True, user) اگر کد معتبر باشد، در غیر این صورت (False, None)
    """
    try:
        # پیدا کردن کد معتبر
        otp = OTPCode.objects.filter(
            phone=phone,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        ).last()
        
        if otp:
            # کد رو استفاده شده علامت بزن
            otp.is_used = True
            otp.save()
            
            # پیدا کردن پروفایل کاربر
            try:
                profile = UserProfile.objects.get(phone=phone)
                user = profile.user
                profile.is_phone_verified = True
                profile.save()
                return True, user
            except UserProfile.DoesNotExist:
                # پروفایل وجود نداره، کاربر رو با شماره موبایل بساز
                user, created = get_or_create_user_by_phone(phone)
                return True, user
        
        return False, None
        
    except Exception as e:
        print(f"Error in verify_otp_code: {e}")
        return False, None


def get_user_session_data(request):
    """دریافت شماره موبایل از سشن"""
    return request.session.get('login_phone')


def clear_user_session(request):
    """پاک کردن اطلاعات سشن"""
    if 'login_phone' in request.session:
        del request.session['login_phone']
    if 'failed_attempts' in request.session:
        del request.session['failed_attempts']