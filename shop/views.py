import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from .models import WebsiteOrder, Template, WebsitePlan, WebsitePlanOrder
from .forms import DigitalMarketinfForm
from users.models import UserProfile
import requests

logger = logging.getLogger(__name__)




@csrf_exempt
@require_http_methods(["POST"])
def save_order(request):
    try:
        data = json.loads(request.body)
        has_website = data.get('has_website', 'no_domain')
        current_url = data.get('current_website_url', '')
        goals = ','.join(data.get('goals', []))
        business_field = data.get('business_field', '')
        design_styles = ','.join(data.get('design_styles', []))
        selected_color = data.get('selected_color', '')
        full_name = data.get('full_name', '')
        phone_number = data.get('phone_number', '')
        email = data.get('email', '')

        from django.contrib.auth.models import User
        from users.models import UserProfile

        # ===== اعتبارسنجی اولیه =====
        if not full_name:
            return JsonResponse({
                'success': False,
                'message': 'لطفاً نام خود را وارد کنید'
            }, status=400)

        if not phone_number or len(phone_number) < 10:
            return JsonResponse({
                'success': False,
                'message': 'لطفاً شماره تماس معتبر وارد کنید'
            }, status=400)

        if not email or '@' not in email:
            return JsonResponse({
                'success': False,
                'message': 'لطفاً ایمیل معتبر وارد کنید'
            }, status=400)

        # ===== پیدا کردن یا ایجاد کاربر =====
        user = None

        # 1. اول با شماره موبایل پیدا کن
        try:
            profile = UserProfile.objects.get(phone=phone_number)
            user = profile.user
        except UserProfile.DoesNotExist:
            # 2. اگه شماره نبود، با ایمیل پیدا کن
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # 3. هیچ‌کدوم نبود، کاربر جدید بساز
                username = phone_number
                if User.objects.filter(username=username).exists():
                    import time
                    username = f"{phone_number}_{int(time.time())}"

                # جدا کردن نام و نام خانوادگی
                name_parts = full_name.strip().split()
                first_name = name_parts[0] if name_parts else ''
                last_name = ' '.join(name_parts[1:]) if len(
                    name_parts) > 1 else ''

                user = User.objects.create_user(
                    username=username,
                    password=None,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )

                # پروفایل کاربر بساز
                UserProfile.objects.create(
                    user=user,
                    phone=phone_number,
                    first_name=first_name,
                    last_name=last_name,
                    is_phone_verified=False
                )

        # ===== اگه کاربر وجود داره ولی پروفایل نداره =====
        if user:
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                name_parts = full_name.strip().split()
                first_name = name_parts[0] if name_parts else ''
                last_name = ' '.join(name_parts[1:]) if len(
                    name_parts) > 1 else ''

                UserProfile.objects.create(
                    user=user,
                    phone=phone_number,
                    first_name=first_name,
                    last_name=last_name,
                    is_phone_verified=False
                )

        # ===== ذخیره سفارش =====
        order = WebsiteOrder.objects.create(
            user=user,
            has_website=has_website,
            current_website_url=current_url,
            goals=goals,
            business_field=business_field,
            design_styles=design_styles,
            selected_color=selected_color,
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            raw_data=data,
            is_processed=True
        )

        return JsonResponse({
            'success': True,
            'message': 'اطلاعات با موفقیت ثبت شد',
            'order_id': order.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'داده ارسالی معتبر نیست'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا در ثبت اطلاعات: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
def get_orders(request):
    orders = WebsiteOrder.objects.all()[:50]
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'full_name': order.full_name,
            'phone_number': order.phone_number,
            'email': order.email,
            'business_field': order.get_business_field_display() if order.business_field else '',
            'created_at': order.created_at.strftime('%Y/%m/%d %H:%M'),
        })
    return JsonResponse({'orders': data, 'count': len(data)})


@csrf_exempt
@require_http_methods(["POST"])
def save_selection(request):
    if 'step_data' not in request.session:
        request.session['step_data'] = {}

    step = request.POST.get('step')
    data = request.POST.get('data')

    if step and data:
        request.session['step_data'][step] = data
        request.session.modified = True

    return JsonResponse({'success': True, 'step': step})


def get_session_data(request):
    step_data = request.session.get('step_data', {})
    return JsonResponse(step_data)


@require_http_methods(["POST"])
def clear_session(request):
    if 'step_data' in request.session:
        del request.session['step_data']
    return JsonResponse({'success': True})


def template_list_view(request):
    templates = Template.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(templates, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'templates': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'product.html', context)


def get_file_url(field):
    """
    گرفتن URL امن از ImageField / FileField
    """
    if not field:
        return None

    try:
        if hasattr(field, "name") and field.name:
            return field.url
    except (ValueError, AttributeError):
        return None

    return None


@csrf_exempt
def template_data_view(request, template_id):
    """API برای دریافت اطلاعات کامل یک قالب"""

    try:
        # -----------------------------
        # دریافت قالب
        # -----------------------------
        template = Template.objects.get(
            id=template_id,
            is_active=True
        )

        # -----------------------------
        # Desktop
        # -----------------------------
        desktop_fields = [
            ("home", "صفحه اصلی", template.desktop_home),
            ("store", "صفحه فروشگاه", template.desktop_store),
            ("about", "درباره ما", template.desktop_about),
            ("blog", "وبلاگ", template.desktop_blog),
            ("cart", "سبد خرید", template.desktop_cart),
            ("login", "لاگین", template.desktop_login),
            ("dash", "داشبورد", template.desktop_dash),
        ]

        desktop_sections = []

        for key, name, field in desktop_fields:

            image_url = get_file_url(field)

            if image_url:
                desktop_sections.append({
                    "name": name,
                    "key": key,
                    "image": image_url,
                })

        # -----------------------------
        # Tablet
        # -----------------------------
        tablet_fields = [
            ("home", "صفحه اصلی", template.tablet_home),
            ("store", "صفحه فروشگاه", template.tablet_store),
            ("about", "درباره ما", template.tablet_about),
            ("blog", "وبلاگ", template.tablet_blog),
            ("cart", "سبد خرید", template.tablet_cart),
            ("login", "لاگین", template.tablet_login),
            ("dash", "داشبورد", template.tablet_dash),
        ]

        tablet_sections = []

        for key, name, field in tablet_fields:

            image_url = get_file_url(field)

            if image_url:
                tablet_sections.append({
                    "name": name,
                    "key": key,
                    "image": image_url,
                })

        # -----------------------------
        # Mobile
        # -----------------------------
        mobile_fields = [
            ("home", "صفحه اصلی", template.mobile_home),
            ("store", "صفحه فروشگاه", template.mobile_store),
            ("about", "درباره ما", template.mobile_about),
            ("blog", "وبلاگ", template.mobile_blog),
            ("cart", "سبد خرید", template.mobile_cart),
            ("login", "لاگین", template.mobile_login),
            ("dash", "داشبورد", template.mobile_dash),
        ]

        mobile_sections = []

        for key, name, field in mobile_fields:

            image_url = get_file_url(field)

            if image_url:
                mobile_sections.append({
                    "name": name,
                    "key": key,
                    "image": image_url,
                })

        # -----------------------------
        # Response
        # -----------------------------

        data = {
            "id": template.id,
            "title": template.title,
            "slug": template.slug,
            "description": template.description,

            "image": get_file_url(template.image),

            "desktop_image": get_file_url(
                template.desktop_image
            ),

            "tablet_image": get_file_url(
                template.tablet_image
            ),

            "mobile_image": get_file_url(
                template.mobile_image
            ),

            "desktop_sections": desktop_sections,
            "tablet_sections": tablet_sections,
            "mobile_sections": mobile_sections,

            "is_popular": template.is_popular,
        }

        # -----------------------------
        # Debug
        # -----------------------------

        print("=" * 60)
        print(f"Template ID: {template.id}")
        print(f"Template title: {template.title}")

        print(
            f"Desktop sections: {len(desktop_sections)}"
        )

        print(
            f"Tablet sections: {len(tablet_sections)}"
        )

        print(
            f"Mobile sections: {len(mobile_sections)}"
        )

        print(
            f"Desktop image: {data['desktop_image']}"
        )

        print(
            f"Tablet image: {data['tablet_image']}"
        )

        print(
            f"Mobile image: {data['mobile_image']}"
        )

        print("=" * 60)

        return JsonResponse(data)

    except Template.DoesNotExist:

        return JsonResponse(
            {
                "error": "قالب یافت نشد"
            },
            status=404
        )

    except Exception as e:

        import traceback

        print("=" * 60)
        print("❌ ERROR IN TEMPLATE DATA VIEW")
        print(f"Template ID: {template_id}")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        print("=" * 60)

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )

def plan_list(request):
    """نمایش لیست طرح‌ها (همون trahi.html)"""
    plans = WebsitePlan.objects.filter(is_active=True)
    return render(request, 'trahi.html', {'plans': plans})


@login_required
def create_plan_order(request, plan_type):
    """
    ایجاد سفارش برای طرح انتخابی و ارسال به درگاه پرداخت
    """
    # دریافت طرح
    plan = get_object_or_404(WebsitePlan, plan_type=plan_type, is_active=True)

    # ایجاد سفارش
    order = WebsitePlanOrder.objects.create(
        user=request.user,
        plan=plan,
        amount=plan.price,
        status='pending'
    )

    # ذخیره در سشن
    request.session['plan_order_id'] = order.id

    # ارسال به درگاه زیبال
    callback_url = request.build_absolute_uri('/payment/verify/')
    track_id, pay_url, error = zibal_request_payment(
        amount=plan.price,
        order_id=order.id,
        callback_url=callback_url,
        description=f'خرید طرح {plan.name} - کاربر {request.user.username}'
    )

    if error:
        messages.error(request, f'خطا در اتصال به درگاه پرداخت: {error}')
        return redirect('shop:plans')

    # ذخیره track_id در سشن
    request.session['payment_track_id'] = track_id
    request.session['payment_order_id'] = order.id
    request.session['payment_order_type'] = 'plan'

    # هدایت به درگاه
    return redirect(pay_url)


@login_required
def plan_order_success(request, order_id):
    """صفحه موفقیت پرداخت - ریدایرکت به داشبورد"""
    order = get_object_or_404(WebsitePlanOrder, id=order_id, user=request.user)
    messages.success(
        request, f'✅ خرید طرح {order.plan.name} با موفقیت انجام شد.')
    return redirect('users:dashboard')


def zibal_request_payment(amount, order_id, callback_url=None, description=None):
    """
    درخواست پرداخت از زیبال
    """
    if callback_url is None:
        callback_url = getattr(settings, 'ZIBAL_CALLBACK_URL',
                               'http://localhost:8000/payment/verify/')

    merchant_id = getattr(settings, 'ZIBAL_MERCHANT_ID', 'zibal')

    # ===== تبدیل درست Decimal به int =====
    from decimal import Decimal
    if isinstance(amount, Decimal):
        amount_toman = int(amount)
    else:
        amount_toman = int(amount)
    amount_rial = amount_toman * 10
    # ===== اعتبارسنجی مبلغ =====
    if amount_rial <= 0:
        return None, None, f'مبلغ {amount} نامعتبر است'

    payload = {
        'merchant': merchant_id,
        'amount': amount_rial,
        'callbackUrl': callback_url,
        'orderId': str(order_id),
        'description': description or f'پرداخت سفارش #{order_id}'
    }

    try:
        response = requests.post(
            'https://gateway.zibal.ir/v1/request',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        result = response.json()
        logger.info(f"Zibal request response: {result}")

        if result.get('result') == 100:
            track_id = result.get('trackId')
            pay_url = f'https://gateway.zibal.ir/start/{track_id}'
            return track_id, pay_url, None
        else:
            error_code = result.get('result')
            error_messages = {
                -1: 'خطای داخلی سرور زیبال',
                101: 'مبلغ ارسال شده معتبر نیست',
                102: 'مرچنت نامعتبر است',
                103: 'مبلغ تراکنش از حد مجاز بیشتر است',
                104: 'مبلغ تراکنش کمتر از حد مجاز است',
                105: 'ایمیل یا شماره شبا نامعتبر است',
            }
            error_message = error_messages.get(
                error_code, f'خطای ناشناخته (کد: {error_code})')
            return None, None, error_message

    except requests.RequestException as e:
        logger.error(f"Zibal request error: {e}")
        return None, None, str(e)


def zibal_verify_payment(track_id):
    """
    تایید پرداخت از زیبال
    بازگشت: (success, amount, order_id, ref_number, error)
    """
    merchant_id = getattr(settings, 'ZIBAL_MERCHANT_ID', 'zibal')

    payload = {
        'merchant': merchant_id,
        'trackId': track_id
    }

    try:
        response = requests.post(
            'https://gateway.zibal.ir/v1/verify',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        result = response.json()

        # ===== برای دیباگ - لاگ بگیر =====
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Zibal verify response: {result}")
        print(f"Zibal verify response: {result}")  # <-- چاپ در ترمینال

        # ===== بررسی کدهای نتیجه =====
        result_code = result.get('result')

        # کد 100 = پرداخت موفق
        if result_code == 100:
            return (
                True,
                result.get('amount'),
                result.get('orderId'),
                result.get('refNumber'),
                None
            )
        # کد 201 = پرداخت ناموفق بوده است
        elif result_code == 201:
            # اطلاعات پرداخت رو از دیتابیس بگیر (اگه قبلاً ثبت شده)
            # بعضی مواقع زیبال 201 برمیگردونه ولی پرداخت قبلاً تایید شده
            # ما میتونیم سفارش رو با track_id پیدا کنیم
            try:
                from shop.models import DirectOrder, WebsitePlanOrder
                from educate.models import CourseOrder

                # سعی کن سفارش رو با track_id پیدا کنی
                # چون track_id توی سشن هست، از اون استفاده میکنیم
                pass
            except:
                pass

            error_messages = {
                201: 'پرداخت ناموفق بوده است',
            }
            error_message = error_messages.get(
                result_code, f'خطای ناشناخته (کد: {result_code})')
            return False, None, None, None, error_message
        else:
            error_messages = {
                -1: 'خطای داخلی سرور زیبال',
                202: 'تراکنش توسط کاربر کنسل شده است',
                204: 'تراکنش ناموفق بوده است (خطای بانکی)',
                205: 'تراکنش قبلاً تایید شده است',
            }
            error_message = error_messages.get(
                result_code, f'خطای ناشناخته (کد: {result_code})')
            return False, None, None, None, error_message

    except requests.RequestException as e:
        logger.error(f"Zibal verify error: {e}")
        return False, None, None, None, str(e)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def payment_verify(request):
    track_id = request.GET.get('trackId') or request.POST.get('trackId')

    if not track_id:
        messages.error(request, '❌ شناسه پرداخت دریافت نشد')
        return redirect('users:dashboard')

    success, amount_rial, order_id, ref_number, error = zibal_verify_payment(
        track_id)

    if not success:
        messages.error(request, f'❌ پرداخت ناموفق بود: {error}')
        return redirect('users:dashboard')

    amount_toman = amount_rial // 10

    session_order_id = request.session.get('payment_order_id')
    session_order_type = request.session.get('payment_order_type')

    if not session_order_id:
        messages.error(request, 'اطلاعات سفارش یافت نشد')
        return redirect('users:dashboard')

    try:
        # ===== پرداخت برای طرح‌های آماده (trahi.html) =====
        if session_order_type == 'plan':
            from shop.models import WebsitePlanOrder
            order = get_object_or_404(
                WebsitePlanOrder, id=session_order_id, user=request.user)

            if order.status == 'paid':
                messages.info(request, 'این سفارش قبلاً پرداخت شده است.')
                return redirect('users:dashboard')

            profile = UserProfile.objects.get(user=request.user)
            profile.add_to_wallet(amount_toman)

            try:
                profile.deduct_from_wallet(amount_toman)
            except ValueError:
                messages.warning(
                    request, 'پرداخت انجام شد اما خطایی در کسر از کیف پول رخ داد.')

            order.status = 'paid'
            order.transaction_id = ref_number
            order.paid_at = timezone.now()
            order.save()

            for key in ['payment_track_id', 'payment_order_id', 'payment_order_type', 'plan_order_id']:
                if key in request.session:
                    del request.session[key]

            messages.success(
                request, f'✅ خرید طرح {order.plan.name} با موفقیت انجام شد.')
            return redirect('users:dashboard')

        # ===== پرداخت برای دوره‌های آموزشی =====
        elif session_order_type == 'course':
            from educate.models import CourseOrder
            from users.models import UserCourse

            order = get_object_or_404(
                CourseOrder, id=session_order_id, user=request.user)

            if order.status == 'paid':
                messages.info(request, 'این سفارش قبلاً پرداخت شده است.')
                return redirect('users:dashboard')

            paid_amount = order.amount

            profile = UserProfile.objects.get(user=request.user)
            profile.add_to_wallet(paid_amount)

            try:
                profile.deduct_from_wallet(paid_amount)
            except ValueError:
                messages.warning(
                    request, 'پرداخت انجام شد اما خطایی در کسر از کیف پول رخ داد.')

            order.status = 'paid'
            order.transaction_id = ref_number
            order.paid_at = timezone.now()
            order.save()

            # به‌روزرسانی یا ایجاد UserCourse
            user_course = UserCourse.objects.filter(
                user=request.user,
                course=order.course,
                payment_status='pending'
            ).first()

            if user_course:
                user_course.payment_status = 'paid'
                user_course.transaction_id = ref_number
                user_course.paid_at = timezone.now()
                user_course.order = order
                user_course.save()
            else:
                UserCourse.objects.create(
                    user=request.user,
                    course=order.course,
                    order=order,
                    payment_status='paid',
                    transaction_id=ref_number,
                    paid_at=timezone.now(),
                    progress=0,
                    is_completed=False
                )

            for key in ['payment_track_id', 'payment_order_id', 'payment_order_type', 'course_order_id', 'user_course_id']:
                if key in request.session:
                    del request.session[key]

            messages.success(
                request, f'✅ خرید دوره {order.course.title} با موفقیت انجام شد.')
            return redirect('users:dashboard')

        else:
            messages.error(request, '❌ نوع سفارش نامعتبر است')
            return redirect('users:dashboard')

    except UserProfile.DoesNotExist:
        messages.error(request, 'پروفایل کاربر یافت نشد')
        return redirect('users:dashboard')
    except Exception as e:
        logger.error(f"Payment verify error: {e}")
        messages.error(request, f'❌ خطا در تایید پرداخت: {str(e)}')
        return redirect('users:dashboard')


def payment_status(request, order_id):
    """
    مشاهده وضعیت پرداخت (API)
    """
    try:
        order = WebsitePlanOrder.objects.get(id=order_id, user=request.user)
        return JsonResponse({
            'status': order.status,
            'amount': order.amount,
            'transaction_id': order.transaction_id,
            'paid_at': order.paid_at
        })
    except WebsitePlanOrder.DoesNotExist:
        return JsonResponse({'error': 'سفارش یافت نشد'}, status=404)

def services_page_view(request):
    return render(request, 'services-page.html')

def services_wordpress_view(request):
    return render(request, 'service-wordpress.html')

def services_seo_view(request):
    return render(request, 'seoservice.html')

def services_web_view(request):
    return render(request, 'tarahiweb.html')

def services_digital_view(request):
    if request.method == 'POST':
        form = DigitalMarketinfForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = DigitalMarketinfForm()
    return render(request, 'digital-marketing.html', {'form': form})

def services_support_view(request):
    return render(request, 'services-support.html')