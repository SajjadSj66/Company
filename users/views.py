from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .forms import ContactForm, CourseRegistrationForm, PhoneLoginForm, ContactRequestForm, CollaborationForm
from educate.models import Course, CourseOrder
from shop.models import WebsiteOrder, WebsitePlanOrder
from .models import UserProfile, UserCourse, UserTicket, UserReview, UserTransaction, Category, Article, Collaboration
import jdatetime

from .utils import (
    get_or_create_user_by_phone,
    create_otp_code,
    verify_otp_code,
    send_sms,
    get_user_session_data,
    clear_user_session
)


def collaboration_view(request):
    """
    صفحه همکاری با ما - دریافت رزومه
    """
    if request.method == 'POST':
        form = CollaborationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'rezume.html', {'form': form, 'success': True})
    else:
        form = CollaborationForm()
    return render(request, 'rezume.html', {'form': form})


def about_view(request):
    return render(request, 'aboutus.html')


def blog_home(request):
    """
    صفحه اصلی وبلاگ
    """
    # دریافت همه مقالات منتشر شده
    articles_list = Article.objects.filter(is_published=True).order_by('-published_at')
    
    # دریافت مقاله ویژه
    featured_article = articles_list.filter(is_featured=True).first()
    
    # دریافت همه دسته‌بندی‌ها
    categories = Category.objects.all()

    for category in categories:
        category.persian_name = category.get_name_display() 
    # صفحه‌بندی
    paginator = Paginator(articles_list, 7)  # 7 مقاله در هر صفحه
    page = request.GET.get('page', 1)
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # بررسی وجود صفحات بیشتر
    has_more = articles.has_next()
    
    context = {
        'articles': articles,
        'featured_article': featured_article,
        'categories': categories,
        'has_more': has_more,
        'site_name': 'آذر یزدان',
    }
    
    return render(request, 'blog.html', context)


def article_detail(request, slug):
    """
    نمایش جزئیات یک مقاله
    """
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # مقالات مرتبط (همان دسته‌بندی)
    related_articles = Article.objects.filter(
        category=article.category, 
        is_published=True
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'site_name': 'آذر یزدان',
    }
    
    return render(request, 'article_detail.html', context)


def blog_filter(request):
    """
    فیلتر مقالات بر اساس دسته‌بندی
    """
    category_slug = request.GET.get('category')
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 7)
    
    articles_list = Article.objects.filter(is_published=True).order_by('-published_at')
    
    if category_slug and category_slug != 'all':
        category = get_object_or_404(Category, slug=category_slug)
        articles_list = articles_list.filter(category=category)
        current_category_name = category.get_name_display()
    
    # صفحه‌بندی
    paginator = Paginator(articles_list, per_page)
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # دریافت همه دسته‌بندی‌ها برای نمایش در صفحه
    categories = Category.objects.all()
    for cat in categories:
        cat.persian_name = cat.get_name_display()
    
    # دریافت مقاله ویژه (اگر دسته‌بندی خاصی انتخاب نشده باشد)
    featured_article = None
    if not category_slug or category_slug == 'all':
        featured_article = Article.objects.filter(is_published=True, is_featured=True).first()
    
    has_more = articles.has_next()
    
    context = {
        'articles': articles,
        'featured_article': featured_article,
        'categories': categories,
        'has_more': has_more,
        'current_category': category_slug or 'all',
        'site_name': 'آذر یزدان',
    }
    
    return render(request, 'blog.html', context)


def blog_search(request):
    """
    جستجو در مقالات
    """
    query = request.GET.get('q', '').strip()
    
    if query:
        articles_list = Article.objects.filter(
            Q(is_published=True) &
            (Q(title__icontains=query) | 
             Q(excerpt__icontains=query) | 
             Q(content__icontains=query) |
             Q(category__name__icontains=query))
        ).order_by('-published_at')
    else:
        articles_list = Article.objects.filter(is_published=True).order_by('-published_at')
    
    # صفحه‌بندی
    paginator = Paginator(articles_list, 7)
    page = request.GET.get('page', 1)
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    has_more = articles.has_next()
    
    context = {
        'articles': articles,
        'categories': categories,
        'has_more': has_more,
        'search_query': query,
        'site_name': 'آذر یزدان',
    }
    
    return render(request, 'blog.html', context)


def category_detail(request, slug):
    """
    نمایش مقالات یک دسته‌بندی خاص
    """
    category = get_object_or_404(Category, slug=slug)
    articles_list = Article.objects.filter(category=category, is_published=True).order_by('-published_at')
    
    # صفحه‌بندی
    paginator = Paginator(articles_list, 7)
    page = request.GET.get('page', 1)
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()
    has_more = articles.has_next()
    
    context = {
        'articles': articles,
        'categories': categories,
        'has_more': has_more,
        'current_category': category.slug,
        'category': category,
        'site_name': 'آذر یزدان',
    }
    
    return render(request, 'blog.html', context)


def to_jalali(dt):
    """تبدیل تاریخ میلادی به شمسی"""
    if not dt:
        return ''
    try:
        return jdatetime.date.fromgregorian(date=dt).strftime('%Y/%m/%d')
    except:
        return str(dt)


@login_required
def dashboard_view(request):
    user = request.user

    # ===== 1. پروفایل کاربر =====
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'phone': user.username if user.username.startswith('09') else '',
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    )

    # ===== 2. دوره‌های کاربر (فقط پرداخت شده) =====
    user_courses = UserCourse.objects.filter(
        user=user,
        payment_status='paid'
    ).select_related('course').order_by('-registered_at')[:5]

    courses_data = []
    for uc in user_courses:
        color = '#6366f1' if uc.progress >= 50 else '#f59e0b'
        courses_data.append({
            'title': uc.course.title,
            'progress': uc.progress,
            'color': color,
            'paid_at': to_jalali(uc.paid_at) if uc.paid_at else '-',
            'transaction_id': uc.transaction_id or '-',
        })

    # ===== 3. سفارش‌های طراحی سایت (فرم) =====
    website_orders = WebsiteOrder.objects.filter(
        Q(email=user.email) | Q(phone_number=profile.phone)
    ).order_by('-created_at')[:10]

    # ===== 4. سفارش‌های طرح‌های آماده =====
    plan_orders = WebsitePlanOrder.objects.filter(
        user=user).order_by('-created_at')[:10]

    # ===== 5. ترکیب سفارش‌ها در یک لیست (فقط طراحی سایت و طرح‌ها) =====
    services_data = []

    # سفارش‌های طراحی سایت (فرم)
    for order in website_orders:
        if order.is_processed:
            status_text = 'تکمیل شده'
            status_color = '#10b981'
        else:
            status_text = 'در انتظار بررسی'
            status_color = '#f59e0b'

        title = f"طراحی سایت - {order.business_field or 'پروژه'}"
        if len(title) > 50:
            title = title[:47] + '...'

        services_data.append({
            'title': title,
            'status': status_text,
            'color': status_color,
            'created_at': to_jalali(order.created_at),
            'order_id': order.id,
            'type': 'website',
        })

    # سفارش‌های طرح‌های آماده
    status_map = {
        'pending': 'در انتظار پرداخت',
        'paid': 'پرداخت شده',
        'failed': 'ناموفق',
        'processing': 'در حال اجرا',
        'completed': 'تکمیل شده',
    }

    status_color_map = {
        'pending': '#f59e0b',
        'paid': '#10b981',
        'failed': '#ef4444',
        'processing': '#3b82f6',
        'completed': '#8b5cf6',
    }

    plan_names = {
        'standard': 'استاندارد',
        'premium': 'پیشرفته',
        'professional': 'حرفه‌ای',
    }

    for order in plan_orders:
        plan_fa = plan_names.get(order.plan.plan_type, order.plan.plan_type)
        services_data.append({
            'title': f"طرح {plan_fa} - {order.plan.name}",
            'status': status_map.get(order.status, order.status),
            'color': status_color_map.get(order.status, '#94a3b8'),
            'created_at': to_jalali(order.created_at),
            'order_id': order.id,
            'type': 'plan',
            'amount': order.amount,
            'transaction_id': order.transaction_id,
        })

    # مرتب‌سازی بر اساس تاریخ
    services_data.sort(key=lambda x: x['created_at'], reverse=True)

    # ===== 6. محاسبات مالی و کیف پول =====
    total_deposits = UserTransaction.objects.filter(
        user=user,
        type='deposit'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_withdraws = UserTransaction.objects.filter(
        user=user,
        type='payment'
    ).aggregate(total=Sum('amount'))['total'] or 0

    wallet_balance = profile.wallet_balance

    # ===== 7. تراکنش‌ها =====
    transactions = UserTransaction.objects.filter(
        user=user
    ).order_by('-created_at')[:10]

    transactions_data = []
    for tr in transactions:
        color = '#10b981' if tr.type == 'deposit' else (
            '#ef4444' if tr.type == 'payment' else '#f59e0b')
        label = 'شارژ کیف پول' if tr.type == 'deposit' else (
            'پرداخت' if tr.type == 'payment' else 'بازگشت وجه')
        transactions_data.append({
            'label': label,
            'amount': tr.amount,
            'color': color,
            'type': tr.type,
            'created_at': to_jalali(tr.created_at),
            'description': tr.description or label,
        })

    # ===== 8. آمار =====
    stats = {
        'courses_count': UserCourse.objects.filter(user=user, payment_status='paid').count(),
        'courses_active': UserCourse.objects.filter(user=user, payment_status='paid', is_completed=False).count(),
        'tickets_count': UserTicket.objects.filter(user=user).count(),
        'open_tickets': UserTicket.objects.filter(user=user, status='open').count(),
        'projects_count': WebsiteOrder.objects.filter(
            Q(email=user.email) | Q(phone_number=profile.phone)
        ).count(),
        'plan_orders_count': WebsitePlanOrder.objects.filter(user=user, status='paid').count(),
        'course_orders_count': CourseOrder.objects.filter(user=user, status='paid').count(),
        'wallet_balance': wallet_balance,
        'total_deposits': total_deposits,
        'total_withdraws': total_withdraws,
    }

    # ===== 9. تیکت‌ها =====
    tickets = UserTicket.objects.filter(user=user).order_by('-created_at')[:3]
    tickets_data = []
    for t in tickets:
        color = '#10b981' if t.status == 'open' else (
            '#f59e0b' if t.status == 'in_progress' else '#94a3b8')
        tickets_data.append({
            'title': t.title,
            'status_display': t.get_status_display(),
            'color': color,
        })

    # ===== 10. نظرات =====
    reviews = UserReview.objects.filter(user=user).select_related(
        'course').order_by('-created_at')[:3]
    reviews_data = []
    for r in reviews:
        reviews_data.append({
            'course': r.course.title,
            'stars': '⭐' * r.rating,
            'comment': r.comment[:30] + '...' if len(r.comment) > 30 else r.comment,
        })

    # ===== 11. اطلاعات کاربر =====
    user_info = {
        'full_name': profile.get_full_name(),
        'phone': profile.phone,
        'email': user.email,
        'membership': profile.membership,
        'membership_badge': profile.get_membership_badge(),
        'joined_date': to_jalali(user.date_joined),
        'last_login': to_jalali(user.last_login) if user.last_login else 'اولین ورود شماست',
        'wallet_balance': wallet_balance,
    }

    # ===== 12. context نهایی =====
    context = {
        'user_info': user_info,
        'stats': stats,
        'courses': courses_data,          # دوره‌های خریداری شده
        'tickets': tickets_data,           # تیکت‌ها
        'reviews': reviews_data,           # نظرات
        'transactions': transactions_data,  # تراکنش‌ها
        'services': services_data,         # فقط طراحی سایت و طرح‌ها
    }

    return render(request, 'dashboard.html', context)


def contact_request_view(request):
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'درخواست شما با موفقیت ثبت شد.')
        else:
            messages.error(request, 'مشکلی پیش آمد')
    else:
        form = ContactRequestForm()
    return render(request, 'form_moshavere.html', {'form': form , 'messages': messages})


def course_registration_view(request):
    """
    صفحه ثبت‌نام دوره آموزشی
    """
    if request.method == 'POST':
        form = CourseRegistrationForm(request.POST)
        if form.is_valid():
            # ذخیره فرم
            registration = form.save()

            # نمایش پیام موفقیت
            messages.success(
                request,
                '✅ درخواست شما با موفقیت ثبت شد. به زودی با شما تماس می‌گیریم.'
            )

            # ریدایرکت به همان صفحه با فرم خالی
            return redirect('users:course_registration')
        else:
            # نمایش خطاهای فرم
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CourseRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'form.html', context)


def login_view(request):
    if request.method == "POST":
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            return send_otp_view(request)  # یا منطق مناسب خودت
    else:
        form = PhoneLoginForm()

    return render(request, 'login.html', {'form': form, 'step': 'phone'})

def send_otp_view(request):
    """ارسال کد تایید"""
    if request.method != 'POST':
        return redirect('users:login')

    phone = request.POST.get('phone')
    next_url = request.POST.get('next') or request.GET.get('next')

    if not phone or len(phone) != 11 or not phone.startswith('09'):
        messages.error(request, 'شماره موبایل معتبر نیست')
        return redirect('users:login')

    # دریافت یا ایجاد کاربر
    user, created = get_or_create_user_by_phone(phone)

    # ایجاد کد تایید
    otp = create_otp_code(user, phone)

    # ارسال پیامک
    send_sms(phone, otp.code)

    messages.success(request, f'کد تایید به شماره {phone} ارسال شد')

    # ذخیره شماره در سشن
    request.session['login_phone'] = phone

    if next_url:
        request.session['login_next_url'] = next_url

    return render(request, 'login.html', {'phone': phone, 'step': 'otp', 'next': next_url})


def verify_otp_view(request):
    """تایید کد و ورود کاربر"""
    if request.method != 'POST':
        return redirect('users:login')

    code = request.POST.get('code')
    phone = get_user_session_data(request)

    if not phone or not code:
        messages.error(request, 'اطلاعات ناقص است')
        return redirect('users:login')

    is_valid, user = verify_otp_code(phone, code)

    if is_valid and user:
        # ورود کاربر
        login(request, user)
        clear_user_session(request)
        next_url = request.session.get('login_next_url', '/')

        # پاک کردن سشن
        if 'login_next_url' in request.session:
            del request.session['login_next_url']
        messages.success(
            request, f'خوش آمدید {user.get_full_name() or user.username}')
        return redirect('home_view')
    else:
        # کد نامعتبر
        failed_attempts = request.session.get('failed_attempts', 0)
        failed_attempts += 1
        request.session['failed_attempts'] = failed_attempts

        if failed_attempts >= 5:
            messages.error(request, 'تعداد تلاش‌های شما بیش از حد مجاز است')
            clear_user_session(request)
            return redirect('users:login')

        messages.error(request, 'کد تایید نامعتبر یا منقضی شده است')
        return render(request, 'login.html', {'phone': phone, 'step': 'otp', 'next': request.session.get('login_next_url', '')})


def verify_otp_submit(request):
    """
    تایید کد و ورود کاربر - با پاسخ JSON برای AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    code = request.POST.get('code')
    phone = get_user_session_data(request)

    if not phone or not code:
        return JsonResponse({'success': False, 'message': 'اطلاعات ناقص است'}, status=400)

    # بررسی کد
    is_valid, user = verify_otp_code(phone, code)

    if is_valid and user:
        # ورود کاربر
        login(request, user)
        clear_user_session(request)

        next_url = request.session.get('login_next_url', '/')

        # پاک کردن سشن
        if 'login_next_url' in request.session:
            del request.session['login_next_url']

        return JsonResponse({
            'success': True,
            'message': f'خوش آمدید {user.username}',
            'redirect_url': next_url
        })
    else:
        # کد نامعتبر
        failed_attempts = request.session.get('failed_attempts', 0)
        failed_attempts += 1
        request.session['failed_attempts'] = failed_attempts

        if failed_attempts >= 5:
            clear_user_session(request)
            return JsonResponse({
                'success': False,
                'message': 'تعداد تلاش‌های شما بیش از حد مجاز است',
                'redirect_url': '/users/login/'
            }, status=400)

        return JsonResponse({
            'success': False,
            'message': 'کد تایید نامعتبر یا منقضی شده است',
            'failed_attempts': failed_attempts
        }, status=400)


def resend_otp(request):
    """ارسال مجدد کد تایید"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    phone = get_user_session_data(request)

    if not phone:
        return JsonResponse({'success': False, 'message': 'شماره موبایل یافت نشد'}, status=400)

    try:
        user = User.objects.get(username=phone)
        otp = create_otp_code(user, phone)
        send_sms(phone, otp.code)

        return JsonResponse({'success': True, 'message': 'کد جدید با موفقیت ارسال شد'})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'کاربر یافت نشد'}, status=404)


def logout_view(request):
    """خروج از حساب کاربری"""
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید')
    return redirect('users:login')


def home_view(request):
    courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]
    # products = Product.objects.filter(is_active=True)[:6]
    featured_articles = Article.objects.filter(
        is_published=True
    ).order_by('-published_at')[:3]

    context = {
        'courses': courses,
        'featured_articles': featured_articles,
        # 'products': products,
    }

    return render(request, 'landing.html', context)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد")
        else:
            messages.error(
                request, "خطا در ارسال پیام. لطفاً دوباره تلاش کنید")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
