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


def send_sms(phone, code):
    """ارسال کد تایید (در کنسول چاپ می‌شود)"""
    print("=" * 50)
    print(f"📱 ارسال کد تایید به {phone}")
    print(f"🔑 کد: {code}")
    print("=" * 50)
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