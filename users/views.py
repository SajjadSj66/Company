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
from .forms import *
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
    return render(request, 'rezume.html', {'form': form, 'hide_chatbot': False})


def about_view(request):
    return render(request, 'about.html', {'hide_chatbot': False})


def blog_home(request):
    """
    صفحه اصلی وبلاگ
    """
    articles_list = Article.objects.filter(
        is_published=True).order_by('-published_at')
    featured_article = articles_list.filter(is_featured=True).first()
    categories = Category.objects.all()

    for category in categories:
        category.persian_name = category.get_name_display()

    paginator = Paginator(articles_list, 7)
    page = request.GET.get('page', 1)

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    has_more = articles.has_next()

    context = {
        'articles': articles,
        'featured_article': featured_article,
        'categories': categories,
        'has_more': has_more,
        'site_name': 'آذر یزدان',
        'hide_chatbot': False,  # چت‌بات نمایش داده بشه
    }

    return render(request, 'blog.html', context)


def article_detail(request, slug):
    """
    نمایش جزئیات یک مقاله
    """
    article = get_object_or_404(Article, slug=slug, is_published=True)

    # افزایش بازدید
    article.views += 1
    article.save()

    # مقالات مرتبط
    related_articles = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id)[:3]

    # دسته‌بندی‌های محبوب با تعداد مقالات - روش دیکشنری
    categories = []
    for cat in Category.objects.all():
        count = Article.objects.filter(category=cat, is_published=True).count()
        if count > 0:
            categories.append({
                'slug': cat.slug,
                'name': cat.name,
                'get_name_display': cat.get_name_display(),
                'article_count': count
            })

    # آخرین مقالات (۴ مقاله)
    latest_articles = Article.objects.filter(
        is_published=True
    ).order_by('-published_at')[:4]

    # محبوب‌ترین مقالات (بر اساس بازدید)
    popular_articles = Article.objects.filter(
        is_published=True
    ).order_by('-views')[:4]

    context = {
        'article': article,
        'related_articles': related_articles,
        'categories': categories,
        'latest_articles': latest_articles,
        'popular_articles': popular_articles,
        'site_name': 'آذر یزدان',
        'hide_chatbot': False,
    }

    return render(request, 'article_detail.html', context)


def blog_filter(request):
    """
    فیلتر مقالات بر اساس دسته‌بندی
    """
    category_slug = request.GET.get('category')
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 7)

    articles_list = Article.objects.filter(
        is_published=True).order_by('-published_at')

    if category_slug and category_slug != 'all':
        category = get_object_or_404(Category, slug=category_slug)
        articles_list = articles_list.filter(category=category)
        current_category_name = category.get_name_display()

    paginator = Paginator(articles_list, per_page)

    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    categories = Category.objects.all()
    for cat in categories:
        cat.persian_name = cat.get_name_display()

    featured_article = None
    if not category_slug or category_slug == 'all':
        featured_article = Article.objects.filter(
            is_published=True, is_featured=True).first()

    has_more = articles.has_next()

    context = {
        'articles': articles,
        'featured_article': featured_article,
        'categories': categories,
        'has_more': has_more,
        'current_category': category_slug or 'all',
        'site_name': 'آذر یزدان',
        'hide_chatbot': False,  # چت‌بات نمایش داده بشه
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
        articles_list = Article.objects.filter(
            is_published=True).order_by('-published_at')

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
        'hide_chatbot': False,  # چت‌بات نمایش داده بشه
    }

    return render(request, 'blog.html', context)


def category_detail(request, slug):
    """
    نمایش مقالات یک دسته‌بندی خاص
    """
    category = get_object_or_404(Category, slug=slug)
    articles_list = Article.objects.filter(
        category=category, is_published=True).order_by('-published_at')

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
        'hide_chatbot': False,  # چت‌بات نمایش داده بشه
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
    return render(request, "base_dashboard.html", {
        "user": request.user
    })

def dashboard2_view(request):
    return render(request, "dashboard2.html", {
        "user": request.user
    })

def dashboard3_view(request):
    return render(request, "dashboard3.html", {
        "user": request.user
    })

def dashboard_upload_project_view(request):
    return render(request, "dashboard_upload_project.html", {
        "user": request.user
    })


def dashboard4_view(request):
    return render(request, "dashboard4.html", {
        "user": request.user
    })



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
    return render(request, 'form_moshavere.html', {'form': form, 'messages': messages, 'hide_chatbot': False})


def study_request_view(request):
    if request.method == 'POST':
        form = StudyRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'درخواست شما با موفقیت ثبت شد.')
        else:
            messages.error(request, 'مشکلی پیش آمد')
    else:
        form = StudyRequestForm()
    return render(request, 'formdore.html', {'form': form, 'messages': messages, 'hide_chatbot': False})


def course_registration_view(request):
    """
    صفحه ثبت‌نام دوره آموزشی
    """
    if request.method == 'POST':
        form = CourseRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save()
            messages.success(
                request,
                '✅ درخواست شما با موفقیت ثبت شد. به زودی با شما تماس می‌گیریم.'
            )
            return redirect('users:course_registration')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CourseRegistrationForm()

    context = {
        'form': form,
        'hide_chatbot': False,  # چت‌بات نمایش داده بشه
    }
    return render(request, 'form.html', context)


def login_view(request):
    if request.method == "POST":
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            redirect('')

    context = {
        'hide_chatbot': True,  # ← چت‌بات خاموش (صفحه لاگین)
    }
    return render(request, 'login.html', context)


def send_otp_view(request):
    """ارسال کد تایید"""
    if request.method != 'POST':
        return redirect('users:login')

    phone = request.POST.get('phone')
    next_url = request.POST.get('next') or request.GET.get('next')

    if not phone or len(phone) != 11 or not phone.startswith('09'):
        messages.error(request, 'شماره موبایل معتبر نیست')
        return redirect('users:login')

    user, created = get_or_create_user_by_phone(phone)
    otp = create_otp_code(user, phone)
    send_sms(phone, otp.code)

    messages.success(request, f'کد تایید به شماره {phone} ارسال شد')
    request.session['login_phone'] = phone

    if next_url:
        request.session['login_next_url'] = next_url

    context = {
        'phone': phone,
        'step': 'otp',
        'next': next_url,
        'hide_chatbot': True,  # ← چت‌بات خاموش
    }
    return render(request, 'login.html', context)


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
        login(request, user)
        clear_user_session(request)
        next_url = request.session.get('login_next_url', '/')

        if 'login_next_url' in request.session:
            del request.session['login_next_url']
        messages.success(
            request, f'خوش آمدید {user.get_full_name() or user.username}')
        return redirect('users:dashboard')
    else:
        failed_attempts = request.session.get('failed_attempts', 0)
        failed_attempts += 1
        request.session['failed_attempts'] = failed_attempts

        if failed_attempts >= 5:
            messages.error(request, 'تعداد تلاش‌های شما بیش از حد مجاز است')
            clear_user_session(request)
            return redirect('users:login')

        messages.error(request, 'کد تایید نامعتبر یا منقضی شده است')
        context = {
            'phone': phone,
            'step': 'otp',
            'next': request.session.get('login_next_url', ''),
            'hide_chatbot': True,  # ← چت‌بات خاموش
        }
        return render(request, 'login.html', context)


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

    is_valid, user = verify_otp_code(phone, code)

    if is_valid and user:
        login(request, user)
        clear_user_session(request)

        next_url = request.session.get('login_next_url', '/')

        if 'login_next_url' in request.session:
            del request.session['login_next_url']

        return JsonResponse({
            'success': True,
            'message': f'خوش آمدید {user.username}',
            'redirect_url': next_url
        })
    else:
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
    featured_articles = Article.objects.filter(
        is_published=True
    ).order_by('-published_at')[:3]

    context = {
        'courses': courses,
        'featured_articles': featured_articles,
        'hide_chatbot': False,  # ← چت‌بات نمایش داده بشه
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

    context = {
        'form': form,
        'hide_chatbot': False,  # ← چت‌بات نمایش داده بشه
    }
    return render(request, 'contact.html', context)
