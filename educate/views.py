# educate/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from .models import Course, CourseFeature, Cart, CartItem, Order, OrderItem, CourseOrder
from .forms import *
from users.models import UserProfile, UserCourse, UserTransaction
import requests
import logging

logger = logging.getLogger(__name__)



def course_list(request):
    """نمایش لیست دوره‌ها"""
    queryset = Course.objects.filter(is_active=True)
    form = CourseSearchForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(short_description__icontains=q)
            )
        if category:
            queryset = queryset.filter(category=category)

    # صفحه‌بندی
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)

    context = {
        'courses': courses,
        'search_form': form,
        'popular_courses': Course.objects.filter(is_popular=True, is_active=True)[:3],
        'is_paginated': courses.has_other_pages(),
        'page_obj': courses,
    }
    return render(request, 'course_list.html', context)


def course_detail(request, slug):
    """نمایش جزئیات یک دوره"""
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # دوره‌های مرتبط
    related_courses = Course.objects.filter(
        category=course.category,
        is_active=True
    ).exclude(id=course.id)[:3]

    # بررسی خرید کاربر
    is_purchased = False
    if request.user.is_authenticated:
        from users.models import UserCourse
        is_purchased = UserCourse.objects.filter(
            user=request.user,
            course=course,
            payment_status='paid'
        ).exists()

    context = {
        'course': course,
        'related_courses': related_courses,
        'is_purchased': is_purchased,
    }
    return render(request, 'course_detail.html', context)



def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, course=course)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(
            request, f"تعداد دوره «{course.title}» در سبد خرید شما افزایش یافت.")
    else:
        messages.success(
            request, f"دوره «{course.title}» به سبد خرید اضافه شد.")
    return redirect('courses:cart_detail')


@login_required
def cart_detail(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('course').all()
    item_forms = {}
    for item in items:
        item_forms[item.id] = CartItemUpdateForm(instance=item)

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            item = get_object_or_404(CartItem, id=item_id, cart=cart)
            form = CartItemUpdateForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                messages.success(request, "تعداد با موفقیت به‌روزرسانی شد.")
            else:
                messages.error(request, "تعداد وارد شده معتبر نیست.")
            return redirect('courses:cart_detail')

    context = {
        'cart': cart,
        'items': items,
        'item_forms': item_forms,
        'total': cart.total_price(),
    }
    return render(request, 'cart_detail.html', context)


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    course_title = cart_item.course.title
    cart_item.delete()
    messages.success(request, f"دوره «{course_title}» از سبد خرید حذف شد.")
    return redirect('courses:cart_detail')


@login_required
def checkout(request):
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('course').all()

    if not items.exists():
        messages.error(request, "سبد خرید شما خالی است.")
        return redirect('courses:cart_detail')

    total = cart.total_price()

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                postal_code=form.cleaned_data['postal_code'],
                city=form.cleaned_data.get('city', ''),
                state=form.cleaned_data.get('state', ''),
                total_amount=total,
                status='pending'
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    course=item.course,
                    price_at_purchase=item.course.price,
                    quantity=item.quantity
                )
            cart.clear()
            messages.success(
                request, "سفارش شما با موفقیت ثبت شد. لطفاً برای پرداخت اقدام کنید.")
            return redirect('courses:payment', order_id=order.id)
        else:
            messages.error(request, "لطفاً اطلاعات را به درستی وارد کنید.")
    else:
        form = CheckoutForm(user=request.user)

    context = {
        'form': form,
        'items': items,
        'total': total,
    }
    return render(request, 'checkout.html', context)


@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'paid':
        messages.info(request, "این سفارش قبلاً پرداخت شده است.")
        return redirect('courses:order_history')

    if request.method == 'POST':
        transaction_id = f"TRX-{order.id}-{request.user.id}"
        order.mark_as_paid(transaction_id=transaction_id)
        messages.success(
            request, "پرداخت با موفقیت انجام شد. به جمع دانشجویان خوش آمدید.")
        return redirect('courses:order_history')

    return render(request, 'payment.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related(
        'items__course').order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


def zibal_request_payment(amount, order_id, callback_url=None, description=None):
    """درخواست پرداخت از زیبال"""
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
        'amount': amount_rial,  # <-- استفاده از amount_int
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


def amozesh_page(request):
    return render(request, 'academy.html')


@login_required
def create_course_order(request, course_id):
    """
    ایجاد سفارش برای دوره و ارسال به درگاه پرداخت
    """
    course = get_object_or_404(Course, id=course_id, is_active=True)

    final_price = course.get_final_price()

    # بررسی سفارش pending قبلی
    pending_order = CourseOrder.objects.filter(
        user=request.user,
        course=course,
        status='pending'
    ).first()

    if pending_order:
        pending_order.delete()

    # ایجاد سفارش جدید
    order = CourseOrder.objects.create(
        user=request.user,
        course=course,
        amount=final_price,
        status='pending'
    )

    # ایجاد UserCourse با وضعیت pending
    user_course, created = UserCourse.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'order': order,
            'payment_status': 'pending',
            'progress': 0,
            'is_completed': False
        }
    )

    if not created:
        user_course.order = order
        user_course.payment_status = 'pending'
        user_course.save()

    # ذخیره در سشن
    request.session['course_order_id'] = order.id
    request.session['user_course_id'] = user_course.id

    # ارسال به درگاه زیبال
    callback_url = request.build_absolute_uri('/payment/verify/')
    track_id, pay_url, error = zibal_request_payment(
        amount=final_price,
        order_id=order.id,
        callback_url=callback_url,
        description=f'خرید دوره {course.title} - کاربر {request.user.username}'
    )

    if error:
        messages.error(request, f'خطا در اتصال به درگاه پرداخت: {error}')
        return redirect('users:dashboard')

    # ذخیره track_id در سشن
    request.session['payment_track_id'] = track_id
    request.session['payment_order_id'] = order.id
    request.session['payment_order_type'] = 'course'

    # هدایت به درگاه
    return redirect(pay_url)


@login_required
def buy_course_by_slug(request, slug):
    """
    ایجاد سفارش برای دوره با شناسه slug
    """
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    final_price = course.get_final_price()

    # بررسی سفارش pending قبلی
    pending_order = CourseOrder.objects.filter(
        user=request.user,
        course=course,
        status='pending'
    ).first()

    if pending_order:
        pending_order.delete()

    # ایجاد سفارش جدید
    order = CourseOrder.objects.create(
        user=request.user,
        course=course,
        amount=final_price,
        status='pending'
    )

    # ایجاد UserCourse با وضعیت pending
    user_course, created = UserCourse.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'order': order,
            'payment_status': 'pending',
            'progress': 0,
            'is_completed': False
        }
    )

    if not created:
        user_course.order = order
        user_course.payment_status = 'pending'
        user_course.save()

    # ذخیره در سشن
    request.session['course_order_id'] = order.id
    request.session['user_course_id'] = user_course.id

    # ارسال به درگاه زیبال
    callback_url = request.build_absolute_uri('/payment/verify/')
    track_id, pay_url, error = zibal_request_payment(
        amount=final_price,
        order_id=order.id,
        callback_url=callback_url,
        description=f'خرید دوره {course.title} - کاربر {request.user.username}'
    )

    if error:
        messages.error(request, f'خطا در اتصال به درگاه پرداخت: {error}')
        return redirect('users:dashboard')

    # ذخیره track_id در سشن
    request.session['payment_track_id'] = track_id
    request.session['payment_order_id'] = order.id
    request.session['payment_order_type'] = 'course'

    # هدایت به درگاه
    return redirect(pay_url)


def seo_signup(request):
    if request.method == 'POST':
        form = SeoSignUpForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = SeoSignUpForm()
    return render(request, 'seo-signup.html')


def ai_signup(request):
    if request.method == 'POST':
        print("ok")

        form = AiSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = AiSignUpForm()
    return render(request, 'ai-signup.html')


def wordpress_signup(request):
    if request.method == 'POST':
        form = WordpressSignUpForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = WordpressSignUpForm()
    return render(request, 'wordpress-signup.html')


def ui_signup(request):
    if request.method == 'POST':
        form = UiSignUpForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UiSignUpForm()
    return render(request, 'ui-signup.html')


def back_signup(request):
    if request.method == 'POST':
        form = BackSignUpForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = BackSignUpForm()
    return render(request, 'backend-signup.html')


def front_signup(request):
    if request.method == 'POST':
        form = FrontSignUpForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = FrontSignUpForm()
    return render(request, 'frontend-signup.html')