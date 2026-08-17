# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.core.paginator import Paginator
# from django.db.models import Q, Count
# from django.contrib.auth.models import User
# from django.contrib import messages
# from django.utils import timezone
# from datetime import datetime, timedelta

# # ایمپورت مدل‌ها
# from users.models import (
#     UserProfile, Article, Comment, Category,
#     ContactRequest, ContactMessage, Collaboration, StudyRequest
# )
# from educate.models import (
#     SeoSignUp, AiSignUp, WordpressSignUp,
#     UiSignUp, BackSignUp, FrontSignUp
# )

# # ========== Helper Functions ==========
# def is_admin(user):
#     return user.is_authenticated and (user.is_staff or user.is_superuser)

# def get_pagination(request, queryset, per_page=20):
#     """تابع کمکی برای pagination"""
#     page = request.GET.get('page', 1)
#     paginator = Paginator(queryset, per_page)
#     page_obj = paginator.get_page(page)
#     return page_obj

# # ========== داشبورد ==========
# @login_required
# @user_passes_test(is_admin)
# def dashboard(request):
#     """داشبورد اصلی ادمین"""
    
#     # آمار کاربران
#     total_users = User.objects.count()
#     new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
    
#     # آمار مقالات
#     total_articles = Article.objects.count()
#     published_articles = Article.objects.filter(is_published=True).count()
    
#     # آمار نظرات
#     total_comments = Comment.objects.count()
#     pending_comments = Comment.objects.filter(is_approved=False).count()
    
#     # آمار ثبت‌نام‌ها
#     total_seo = SeoSignUp.objects.count()
#     total_ai = AiSignUp.objects.count()
#     total_wordpress = WordpressSignUp.objects.count()
#     total_ui = UiSignUp.objects.count()
#     total_backend = BackSignUp.objects.count()
#     total_frontend = FrontSignUp.objects.count()
    
#     # آمار درخواست‌ها
#     total_collaborations = Collaboration.objects.count()
#     pending_collaborations = Collaboration.objects.filter(status='pending').count()
#     total_contact_messages = ContactMessage.objects.count()
#     total_contact_requests = ContactRequest.objects.count()
#     total_study_requests = StudyRequest.objects.count()
    
#     context = {
#         'title': 'داشبورد',
#         'stats': {
#             'total_users': total_users,
#             'new_users_today': new_users_today,
#             'total_articles': total_articles,
#             'published_articles': published_articles,
#             'total_comments': total_comments,
#             'pending_comments': pending_comments,
#             'total_signups': {
#                 'seo': total_seo,
#                 'ai': total_ai,
#                 'wordpress': total_wordpress,
#                 'ui': total_ui,
#                 'backend': total_backend,
#                 'frontend': total_frontend,
#             },
#             'total_collaborations': total_collaborations,
#             'pending_collaborations': pending_collaborations,
#             'total_contact_messages': total_contact_messages,
#             'total_contact_requests': total_contact_requests,
#             'total_study_requests': total_study_requests,
#         }
#     }
    
#     return render(request, 'admin_panel/dashboard.html', context)


# # ========== مدیریت کاربران ==========
# @login_required
# @user_passes_test(is_admin)
# def user_list(request):
#     """لیست کاربران"""
#     search = request.GET.get('search', '')
#     is_active = request.GET.get('is_active', '')
    
#     users = User.objects.all().select_related('dashboard_profile')
    
#     if search:
#         users = users.filter(
#             Q(username__icontains=search) |
#             Q(email__icontains=search) |
#             Q(first_name__icontains=search) |
#             Q(last_name__icontains=search) |
#             Q(dashboard_profile__phone__icontains=search)
#         )
    
#     if is_active:
#         users = users.filter(is_active=is_active == 'true')
    
#     users = users.order_by('-date_joined')
    
#     # Pagination
#     page_obj = get_pagination(request, users)
    
#     context = {
#         'title': 'مدیریت کاربران',
#         'users': page_obj,
#         'search': search,
#         'is_active': is_active,
#         'total_users': users.count(),
#         'active_users': User.objects.filter(is_active=True).count(),
#         'inactive_users': User.objects.filter(is_active=False).count(),
#     }
    
#     return render(request, 'admin_panel/users/user_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def user_detail(request, pk):
#     """جزئیات کاربر"""
#     user = get_object_or_404(User, pk=pk)
#     profile = user.dashboard_profile if hasattr(user, 'dashboard_profile') else None
    
#     # آمار کاربر
#     user_stats = {
#         'articles_count': Article.objects.filter(author=user).count(),
#         'comments_count': Comment.objects.filter(author_email=user.email).count(),
#     }
    
#     context = {
#         'title': f'پروفایل {user.username}',
#         'user': user,
#         'profile': profile,
#         'user_stats': user_stats,
#     }
    
#     return render(request, 'admin_panel/users/user_detail.html', context)


# @login_required
# @user_passes_test(is_admin)
# def user_toggle_active(request, pk):
#     """فعال/غیرفعال کردن کاربر"""
#     user = get_object_or_404(User, pk=pk)
#     user.is_active = not user.is_active
#     user.save()
    
#     if user.is_active:
#         messages.success(request, f'کاربر {user.username} فعال شد')
#     else:
#         messages.warning(request, f'کاربر {user.username} غیرفعال شد')
    
#     return redirect('admin_panel:user_detail', pk=user.id)


# @login_required
# @user_passes_test(is_admin)
# def user_update(request, pk):
#     """به‌روزرسانی کاربر"""
#     user = get_object_or_404(User, pk=pk)
#     profile = user.dashboard_profile if hasattr(user, 'dashboard_profile') else None
    
#     if request.method == 'POST':
#         # به‌روزرسانی User
#         user.first_name = request.POST.get('first_name', user.first_name)
#         user.last_name = request.POST.get('last_name', user.last_name)
#         user.email = request.POST.get('email', user.email)
#         user.is_active = request.POST.get('is_active') == 'on'
#         user.save()
        
#         # به‌روزرسانی Profile
#         if profile:
#             profile.phone = request.POST.get('phone', profile.phone)
#             profile.membership = request.POST.get('membership', profile.membership)
#             profile.save()
        
#         messages.success(request, 'اطلاعات کاربر با موفقیت به‌روزرسانی شد')
#         return redirect('admin_panel:user_detail', pk=user.id)
    
#     context = {
#         'title': f'ویرایش {user.username}',
#         'user': user,
#         'profile': profile,
#     }
    
#     return render(request, 'admin_panel/users/user_form.html', context)


# # ========== مدیریت مقالات ==========
# @login_required
# @user_passes_test(is_admin)
# def article_list(request):
#     """لیست مقالات"""
#     search = request.GET.get('search', '')
#     category = request.GET.get('category', '')
#     is_published = request.GET.get('is_published', '')
    
#     articles = Article.objects.all().select_related('category', 'author')
    
#     if search:
#         articles = articles.filter(
#             Q(title__icontains=search) |
#             Q(content__icontains=search) |
#             Q(author__username__icontains=search)
#         )
    
#     if category:
#         articles = articles.filter(category__slug=category)
    
#     if is_published:
#         articles = articles.filter(is_published=is_published == 'true')
    
#     articles = articles.order_by('-created_at')
    
#     # Pagination
#     page_obj = get_pagination(request, articles)
    
#     context = {
#         'title': 'مدیریت مقالات',
#         'articles': page_obj,
#         'categories': Category.objects.all(),
#         'search': search,
#         'selected_category': category,
#         'is_published': is_published,
#         'total_articles': articles.count(),
#         'published_count': Article.objects.filter(is_published=True).count(),
#         'draft_count': Article.objects.filter(is_published=False).count(),
#     }
    
#     return render(request, 'admin_panel/blog/article_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def article_detail(request, pk):
#     """جزئیات مقاله"""
#     article = get_object_or_404(Article, pk=pk)
#     comments = article.comments.all().order_by('-created_at')
    
#     context = {
#         'title': article.title,
#         'article': article,
#         'comments': comments,
#         'categories': Category.objects.all(),
#     }
    
#     return render(request, 'admin_panel/blog/article_detail.html', context)


# @login_required
# @user_passes_test(is_admin)
# def article_toggle_publish(request, pk):
#     """انتشار/عدم انتشار مقاله"""
#     article = get_object_or_404(Article, pk=pk)
#     article.is_published = not article.is_published
    
#     if article.is_published and not article.published_at:
#         article.published_at = timezone.now()
    
#     article.save()
    
#     if article.is_published:
#         messages.success(request, f'مقاله "{article.title}" منتشر شد')
#     else:
#         messages.warning(request, f'انتشار مقاله "{article.title}" لغو شد')
    
#     return redirect('admin_panel:article_detail', pk=article.id)


# @login_required
# @user_passes_test(is_admin)
# def article_delete(request, pk):
#     """حذف مقاله"""
#     article = get_object_or_404(Article, pk=pk)
#     title = article.title
#     article.delete()
    
#     messages.success(request, f'مقاله "{title}" با موفقیت حذف شد')
#     return redirect('admin_panel:article_list')


# # ========== مدیریت نظرات ==========
# @login_required
# @user_passes_test(is_admin)
# def comment_list(request):
#     """لیست نظرات"""
#     search = request.GET.get('search', '')
#     is_approved = request.GET.get('is_approved', '')
    
#     comments = Comment.objects.all().select_related('article')
    
#     if search:
#         comments = comments.filter(
#             Q(author_name__icontains=search) |
#             Q(author_email__icontains=search) |
#             Q(content__icontains=search) |
#             Q(article__title__icontains=search)
#         )
    
#     if is_approved:
#         comments = comments.filter(is_approved=is_approved == 'true')
    
#     comments = comments.order_by('-created_at')
    
#     # Pagination
#     page_obj = get_pagination(request, comments)
    
#     context = {
#         'title': 'مدیریت نظرات',
#         'comments': page_obj,
#         'search': search,
#         'is_approved': is_approved,
#         'total_comments': comments.count(),
#         'pending_count': Comment.objects.filter(is_approved=False).count(),
#         'approved_count': Comment.objects.filter(is_approved=True).count(),
#     }
    
#     return render(request, 'admin_panel/blog/comment_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def comment_toggle_approve(request, pk):
#     """تایید/عدم تایید نظر"""
#     comment = get_object_or_404(Comment, pk=pk)
#     comment.is_approved = not comment.is_approved
#     comment.save()
    
#     if comment.is_approved:
#         messages.success(request, 'نظر تایید شد')
#     else:
#         messages.warning(request, 'نظر رد شد')
    
#     return redirect('admin_panel:comment_list')


# @login_required
# @user_passes_test(is_admin)
# def comment_delete(request, pk):
#     """حذف نظر"""
#     comment = get_object_or_404(Comment, pk=pk)
#     comment.delete()
    
#     messages.success(request, 'نظر با موفقیت حذف شد')
#     return redirect('admin_panel:comment_list')


# # ========== مدیریت ثبت‌نام‌های تخصصی ==========
# @login_required
# @user_passes_test(is_admin)
# def seo_signup_list(request):
#     """لیست ثبت‌نام‌های سئو"""
#     search = request.GET.get('search', '')
    
#     signups = SeoSignUp.objects.all()
    
#     if search:
#         signups = signups.filter(
#             Q(full_name__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(educate__icontains=search)
#         )
    
#     signups = signups.order_by('-created_at')
    
#     page_obj = get_pagination(request, signups)
    
#     context = {
#         'title': 'ثبت‌نام‌های سئو',
#         'signups': page_obj,
#         'search': search,
#         'total_count': signups.count(),
#     }
    
#     return render(request, 'admin_panel/signups/signup_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def ai_signup_list(request):
#     """لیست ثبت‌نام‌های هوش مصنوعی"""
#     search = request.GET.get('search', '')
    
#     signups = AiSignUp.objects.all()
    
#     if search:
#         signups = signups.filter(
#             Q(full_name__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(educate__icontains=search)
#         )
    
#     signups = signups.order_by('-created_at')
    
#     page_obj = get_pagination(request, signups)
    
#     context = {
#         'title': 'ثبت‌نام‌های هوش مصنوعی',
#         'signups': page_obj,
#         'search': search,
#         'total_count': signups.count(),
#     }
    
#     return render(request, 'admin_panel/signups/signup_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def wordpress_signup_list(request):
#     """لیست ثبت‌نام‌های وردپرس"""
#     search = request.GET.get('search', '')
    
#     signups = WordpressSignUp.objects.all()
    
#     if search:
#         signups = signups.filter(
#             Q(full_name__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(educate__icontains=search)
#         )
    
#     signups = signups.order_by('-created_at')
    
#     page_obj = get_pagination(request, signups)
    
#     context = {
#         'title': 'ثبت‌نام‌های وردپرس',
#         'signups': page_obj,
#         'search': search,
#         'total_count': signups.count(),
#     }
    
#     return render(request, 'admin_panel/signups/signup_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def ui_signup_list(request):
#     """لیست ثبت‌نام‌های UI"""
#     search = request.GET.get('search', '')
    
#     signups = UiSignUp.objects.all()
    
#     if search:
#         signups = signups.filter(
#             Q(full_name__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(educate__icontains=search)
#         )
    
#     signups = signups.order_by('-created_at')
    
#     page_obj = get_pagination(request, signups)
    
#     context = {
#         'title': 'ثبت‌نام‌های UI',
#         'signups': page_obj,
#         'search': search,
#         'total_count': signups.count(),
#     }
    
#     return render(request, 'admin_panel/signups/signup_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def backend_signup_list(request):
#     """لیست ثبت‌نام‌های بک‌اند"""
#     search = request.GET.get('search', '')
    
#     signups = BackSignUp.objects.all()
    
#     if search:
#         signups = signups.filter(
#             Q(full_name__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(educate__icontains=search)
#         )
    
#     signups = signups.order_by('-created_at')
    
#     page_obj = get_pagination(request, signups)
    
#     context = {
#         'title': 'ثبت‌نام‌های بک‌اند',
#         'signups': page_obj,
#         'search': search,
#         'total_count': signups.count(),
#     }
    
#     return render(request, 'admin_panel/signups/signup_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def frontend_signup_list(request):
#     """لیست ثبت‌نام‌های فرانت‌اند"""
#     search = request.GET.get('search', '')
    
#     signups = FrontSignUp.objects.all()
    
#     if search:
#         signups = signups.filter(
#             Q(full_name__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(educate__icontains=search)
#         )
    
#     signups = signups.order_by('-created_at')
    
#     page_obj = get_pagination(request, signups)
    
#     context = {
#         'title': 'ثبت‌نام‌های فرانت‌اند',
#         'signups': page_obj,
#         'search': search,
#         'total_count': signups.count(),
#     }
    
#     return render(request, 'admin_panel/signups/signup_list.html', context)


# # ========== مدیریت درخواست‌های همکاری ==========
# @login_required
# @user_passes_test(is_admin)
# def collaboration_list(request):
#     """لیست درخواست‌های همکاری"""
#     search = request.GET.get('search', '')
#     status = request.GET.get('status', '')
    
#     collaborations = Collaboration.objects.all()
    
#     if search:
#         collaborations = collaborations.filter(
#             Q(full_name__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(email__icontains=search)
#         )
    
#     if status:
#         collaborations = collaborations.filter(status=status)
    
#     collaborations = collaborations.order_by('-created_at')
    
#     page_obj = get_pagination(request, collaborations)
    
#     context = {
#         'title': 'درخواست‌های همکاری',
#         'collaborations': page_obj,
#         'search': search,
#         'selected_status': status,
#         'total_count': collaborations.count(),
#         'pending_count': Collaboration.objects.filter(status='pending').count(),
#         'reviewing_count': Collaboration.objects.filter(status='reviewing').count(),
#         'accepted_count': Collaboration.objects.filter(status='accepted').count(),
#         'rejected_count': Collaboration.objects.filter(status='rejected').count(),
#     }
    
#     return render(request, 'admin_panel/collaborations/collaboration_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def collaboration_detail(request, pk):
#     """جزئیات درخواست همکاری"""
#     collab = get_object_or_404(Collaboration, pk=pk)
    
#     context = {
#         'title': f'درخواست {collab.full_name}',
#         'collab': collab,
#     }
    
#     return render(request, 'admin_panel/collaborations/collaboration_detail.html', context)


# @login_required
# @user_passes_test(is_admin)
# def collaboration_update_status(request, pk):
#     """به‌روزرسانی وضعیت درخواست همکاری"""
#     collab = get_object_or_404(Collaboration, pk=pk)
    
#     if request.method == 'POST':
#         collab.status = request.POST.get('status', collab.status)
#         collab.admin_note = request.POST.get('admin_note', collab.admin_note)
#         collab.save()
        
#         messages.success(request, 'وضعیت با موفقیت به‌روزرسانی شد')
#         return redirect('admin_panel:collaboration_detail', pk=collab.id)
    
#     context = {
#         'title': f'ویرایش وضعیت {collab.full_name}',
#         'collab': collab,
#     }
    
#     return render(request, 'admin_panel/collaborations/collaboration_form.html', context)


# @login_required
# @user_passes_test(is_admin)
# def collaboration_delete(request, pk):
#     """حذف درخواست همکاری"""
#     collab = get_object_or_404(Collaboration, pk=pk)
#     collab.delete()
    
#     messages.success(request, 'درخواست همکاری با موفقیت حذف شد')
#     return redirect('admin_panel:collaboration_list')


# # ========== مدیریت پیام‌های تماس با ما ==========
# @login_required
# @user_passes_test(is_admin)
# def contact_message_list(request):
#     """لیست پیام‌های تماس با ما"""
#     search = request.GET.get('search', '')
#     service_type = request.GET.get('service_type', '')
    
#     contact_messages = ContactMessage.objects.all()
    
#     if search:
#         contact_messages = contact_messages.filter(
#             Q(fullname__icontains=search) |
#             Q(phone__icontains=search) |
#             Q(email__icontains=search) |
#             Q(message__icontains=search)
#         )
    
#     if service_type:
#         contact_messages = contact_messages.filter(service_type=service_type)
    
#     contact_messages = contact_messages.order_by('-created_at')
    
#     page_obj = get_pagination(request, contact_messages)
    
#     context = {
#         'title': 'پیام‌های تماس با ما',
#         'messages': page_obj,
#         'search': search,
#         'selected_service': service_type,
#         'total_count': contact_messages.count(),
#     }
    
#     return render(request, 'admin_panel/contacts/contact_message_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def contact_message_delete(request, pk):
#     """حذف پیام تماس با ما"""
#     message = get_object_or_404(ContactMessage, pk=pk)
#     message.delete()
    
#     messages.success(request, 'پیام با موفقیت حذف شد')
#     return redirect('admin_panel:contact_message_list')


# # ========== مدیریت درخواست‌های مشاوره ==========
# @login_required
# @user_passes_test(is_admin)
# def contact_request_list(request):
#     """لیست درخواست‌های مشاوره"""
#     search = request.GET.get('search', '')
#     project_type = request.GET.get('project_type', '')
    
#     contact_requests = ContactRequest.objects.all()
    
#     if search:
#         contact_requests = contact_requests.filter(
#             Q(full_name__icontains=search) |
#             Q(phone_or_email__icontains=search) |
#             Q(work_name__icontains=search)
#         )
    
#     if project_type:
#         contact_requests = contact_requests.filter(project_choices=project_type)
    
#     contact_requests = contact_requests.order_by('-created_at')
    
#     page_obj = get_pagination(request, contact_requests)
    
#     context = {
#         'title': 'درخواست‌های مشاوره',
#         'requests': page_obj,
#         'search': search,
#         'selected_project': project_type,
#         'total_count': contact_requests.count(),
#     }
    
#     return render(request, 'admin_panel/contacts/contact_request_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def contact_request_delete(request, pk):
#     """حذف درخواست مشاوره"""
#     req = get_object_or_404(ContactRequest, pk=pk)
#     req.delete()
    
#     messages.success(request, 'درخواست مشاوره با موفقیت حذف شد')
#     return redirect('admin_panel:contact_request_list')


# # ========== مدیریت درخواست‌های دوره ==========
# @login_required
# @user_passes_test(is_admin)
# def study_request_list(request):
#     """لیست درخواست‌های دوره"""
#     search = request.GET.get('search', '')
#     study_type = request.GET.get('study_type', '')
    
#     study_requests = StudyRequest.objects.all()
    
#     if search:
#         study_requests = study_requests.filter(
#             Q(full_name__icontains=search) |
#             Q(phone_or_email__icontains=search) |
#             Q(grade__icontains=search)
#         )
    
#     if study_type:
#         study_requests = study_requests.filter(study_choices=study_type)
    
#     study_requests = study_requests.order_by('-created_at')
    
#     page_obj = get_pagination(request, study_requests)
    
#     context = {
#         'title': 'درخواست‌های دوره',
#         'requests': page_obj,
#         'search': search,
#         'selected_study': study_type,
#         'total_count': study_requests.count(),
#     }
    
#     return render(request, 'admin_panel/study/study_request_list.html', context)


# @login_required
# @user_passes_test(is_admin)
# def study_request_detail(request, pk):
#     """جزئیات درخواست دوره"""
#     req = get_object_or_404(StudyRequest, pk=pk)
    
#     context = {
#         'title': f'درخواست {req.full_name}',
#         'request': req,
#     }
    
#     return render(request, 'admin_panel/study/study_request_detail.html', context)


# @login_required
# @user_passes_test(is_admin)
# def study_request_delete(request, pk):
#     """حذف درخواست دوره"""
#     req = get_object_or_404(StudyRequest, pk=pk)
#     req.delete()
    
#     messages.success(request, 'درخواست دوره با موفقیت حذف شد')
#     return redirect('admin_panel:study_request_list')


from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import *
from .forms import *

def admin_add_blog_view(request):
    articles = Article.objects.all()
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ArticleForm()

    return render(request, 'dashboard.html', {'articles': articles})


def admin_add_tag_view(request):
    tags = Tag.objects.all()
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = TagForm()

    return render(request, 'dashboard.html', {'tags': tags})


def admin_add_category_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CategoryForm()

    return render(request, 'dashboard.html', {'categories': categories})

@login_required
def admin_edit_blog_view(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if not (request.user.is_staff or article.author == request.user):
        return HttpResponseForbidden('شما اجازه‌ی دسترسی به این صفحه را ندارید.')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'مقاله با موفقیت ویرایش شد.')
            return redirect('users:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    context = {'form': form, 'article': article}
    return render(request, 'dashboard.html', context)

@login_required
def admin_delete_blog_view(request, slug):
    article = get_object_or_404(Article, slug=slug)

    if not (request.user.is_staff or article.author == request.user):
        return HttpResponseForbidden('شما اجازه‌ی دسترسی به این صفحه را ندارید.')

    if request.method == 'POST':
        article.delete()
        messages.success(request, 'مقاله با موفقیت حذف شد.')
        return redirect('users:article_list')

    context = {'article': article}
    return render(request, 'articles/article_confirm_delete.html', context)


@login_required
def media_library_list(request):
    search_form = MediaSearchForm(request.GET or None)
    files = MediaFile.objects.select_related("folder", "uploaded_by")

    if search_form.is_valid():
        q = search_form.cleaned_data.get("q")
        file_type = search_form.cleaned_data.get("file_type")
        if q:
            files = files.filter(title__icontains=q) | files.filter(file__icontains=q)
        if file_type:
            files = files.filter(file_type=file_type)

    paginator = Paginator(files, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    upload_form = MediaFileForm()

    return render(request, "media_library/list.html", {
        "page_obj": page_obj,
        "search_form": search_form,
        "upload_form": upload_form,
    })


@login_required
@require_POST
def media_file_upload(request):
    form = MediaFileForm(request.POST, request.FILES)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.uploaded_by = request.user
        obj.save()
        messages.success(request, "فایل با موفقیت آپلود شد.")
    else:
        messages.error(request, "خطا در آپلود فایل.")
    return redirect("media_library:list")


@login_required
def media_file_edit(request, pk):
    obj = get_object_or_404(MediaFile, pk=pk)
    if request.method == "POST":
        form = MediaFileForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "فایل ویرایش شد.")
            return redirect("media_library:list")
    else:
        form = MediaFileForm(instance=obj)
    return render(request, "media_library/edit.html", {"form": form, "object": obj})


@login_required
@require_POST
def media_file_delete(request, pk):
    obj = get_object_or_404(MediaFile, pk=pk)
    obj.file.delete(save=False)
    obj.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True})
    messages.success(request, "فایل حذف شد.")
    return redirect("media_library:list")





@login_required
@permission_required("app.view_comment", raise_exception=True)
def comment_list(request):
    search_form = CommentSearchForm(request.GET or None)
    comments = Comment.objects.select_related("author", "content_type")

    if search_form.is_valid():
        q = search_form.cleaned_data.get("q")
        status = search_form.cleaned_data.get("status")
        if q:
            comments = comments.filter(body__icontains=q)
        if status:
            comments = comments.filter(status=status)

    paginator = Paginator(comments, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "comments/list.html", {
        "page_obj": page_obj,
        "search_form": search_form,
    })


@login_required
@permission_required("app.change_comment", raise_exception=True)
@require_POST
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.status = Comment.Status.APPROVED
    comment.reviewed_at = timezone.now()
    comment.save(update_fields=["status", "reviewed_at"])

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "status": comment.get_status_display()})
    messages.success(request, "دیدگاه تأیید شد.")
    return redirect("comments:list")


@login_required
@permission_required("app.delete_comment", raise_exception=True)
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True})
    messages.success(request, "دیدگاه حذف شد.")
    return redirect("comments:list")


from .models import SiteSettings
from .forms import SiteSettingsForm


@login_required
@permission_required("app.change_sitesettings", raise_exception=True)
def site_settings_view(request):
    settings_obj = SiteSettings.load()

    if request.method == "POST":
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "تنظیمات سایت با موفقیت ذخیره شد.")
            return redirect("settings:site_settings")
        else:
            messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
    else:
        form = SiteSettingsForm(instance=settings_obj)

    return render(request, "settings/site_settings.html", {
        "form": form,
        "settings": settings_obj,
    })

@login_required
@permission_required("app.change_readingsettings", raise_exception=True)
def reading_settings_view(request):
    settings_obj = ReadingSettings.load()

    if request.method == "POST":
        form = ReadingSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "تغییرات با موفقیت ذخیره شد.")
            return redirect("settings:reading_settings")
        else:
            messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
    else:
        form = ReadingSettingsForm(instance=settings_obj)

    return render(request, "settings/reading_settings.html", {"form": form})


def robots_txt(request):
    """robots.txt پویا بر اساس تنظیمات خواندن"""
    settings_obj = ReadingSettings.load()
    if settings_obj.allow_search_indexing:
        content = "User-agent: *\nAllow: /\n\nSitemap: https://example.com/sitemap.xml\n"
    else:
        content = "User-agent: *\nDisallow: /\n"
    return HttpResponse(content, content_type="text/plain")

@login_required
@permission_required("app.change_seosettings", raise_exception=True)
def seo_settings_view(request):
    settings_obj = SEOSettings.load()

    if request.method == "POST":
        form = SEOSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "تنظیمات سئو با موفقیت ذخیره شد.")
            return redirect("settings:seo_settings")
        else:
            messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
    else:
        form = SEOSettingsForm(instance=settings_obj)

    return render(request, "settings/seo_settings.html", {"form": form})


def robots_txt(request):
    """
    خروجی robots.txt واقعی سایت.
    منطق: اگه ایندکس‌شدن غیرفعال بود، هر چی کاربر نوشته رو نادیده می‌گیریم
    و کل سایت رو می‌بندیم. در غیر این‌صورت متن دستی کاربر رو نشون می‌دیم.
    """
    settings_obj = SEOSettings.load()

    if not settings_obj.allow_search_indexing:
        content = "User-agent: *\nDisallow: /\n"
    else:
        content = settings_obj.robots_txt_content or "User-agent: *\nAllow: /\n"

    return HttpResponse(content, content_type="text/plain")