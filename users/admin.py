from django.contrib import admin
from django.contrib import admin
from .models import *


@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ['full_name','phone','status','work_choices','resume_file']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'article_count',
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
    ]

    readonly_fields = [
        'created_at',
    ]

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = [
        '-created_at'
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'article_count',
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
    ]

    readonly_fields = [
        'created_at',
    ]

    prepopulated_fields = {
        'slug': ('name',)
    }

    ordering = [
        '-created_at'
    ]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = [
        'title',
        'category',
        'author',
        'status',
        'is_published',
        'is_featured',
        'published_date',
        'views',
        'likes',
    ]

    list_filter = [
        'status',
        'is_published',
        'is_featured',
        'category',
        'tags',
        'published_date',
    ]

    search_fields = [
        'title',
        'content',
        'excerpt',
        'seo_title',
        'seo_description',
        'seo_keywords',
    ]

    prepopulated_fields = {
        'slug': ('title',)
    }

    filter_horizontal = [
        'tags',
    ]

    readonly_fields = [
        'views',
        'likes',
    ]

    list_editable = [
        'status',
        'is_published',
        'is_featured',
    ]

    date_hierarchy = 'published_date'

    fieldsets = (
        (
            'اطلاعات اصلی',
            {
                'fields': (
                    'title',
                    'slug',
                    'category',
                    'tags',
                    'author',
                    'image',
                )
            }
        ),

        (
            'محتوا',
            {
                'fields': (
                    'excerpt',
                    'content',
                )
            }
        ),

        (
            'تنظیمات انتشار',
            {
                'fields': (
                    'status',
                    'is_published',
                    'is_featured',
                    'published_date',
                    'publish_time',
                    'read_time',
                )
            }
        ),

        (
            'آمار مقاله',
            {
                'fields': (
                    'views',
                    'likes',
                )
            }
        ),

        (
            'SEO',
            {
                'fields': (
                    'seo_title',
                    'seo_description',
                    'seo_keywords',
                    'canonical_url',
                    'schema',
                ),
                'classes': (
                    'collapse',
                )
            }
        ),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'article',
                    'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author_name', 'content', 'author_email']
    list_editable = ['is_approved']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'متن نظر'

# ========== پروفایل کاربری ==========


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'get_full_name',
                    'membership', 'courses_count', 'created_at')
    list_filter = ('membership', 'created_at')
    search_fields = ('phone', 'first_name', 'last_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'phone', 'first_name', 'last_name')
        }),
        ('اشتراک و آمار', {
            'fields': ('membership', 'courses_count', 'tickets_count', 'projects_count', 'total_payments')
        }),
        ('زمان‌ها', {
            'fields': ('last_login_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'نام کامل'


# ========== دوره‌های کاربر ==========
@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress',
                    'is_completed', 'registered_at')
    list_filter = ('is_completed', 'registered_at')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('registered_at',)

    fieldsets = (
        ('اطلاعات', {
            'fields': ('user', 'course', 'progress', 'is_completed')
        }),
        ('زمان ثبت', {
            'fields': ('registered_at',)
        })
    )


# ========== تیکت‌های کاربر ==========
@admin.register(UserTicket)
class UserTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('اطلاعات تیکت', {
            'fields': ('user', 'title', 'description', 'status', 'priority')
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# ========== نظرات کاربر ==========
@admin.register(UserReview)
class UserReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'rating',
                    'comment_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'course__title', 'comment')
    readonly_fields = ('created_at',)

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'نظر (پیش‌نمایش)'


# ========== تراکنش‌های کاربر ==========
@admin.register(UserTransaction)
class UserTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'type', 'description', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('اطلاعات تراکنش', {
            'fields': ('user', 'amount', 'type', 'description')
        }),
        ('زمان', {
            'fields': ('created_at',)
        })
    )


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_or_email', 'work_name', 'project_choices']
    search_fields = ['full_name', 'phone_or_email', 'work_name']


@admin.register(StudyRequest)
class StudyRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_or_email', 'grade', 'study_choices']
    search_fields = ['full_name', 'phone_or_email', 'grade']


@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'mobile', 'national_id',
                    'get_domains_display', 'status', 'created_at')
    list_filter = ('status', 'education_level', 'created_at')
    search_fields = ('first_name', 'last_name', 'mobile',
                     'national_id', 'shenasname_no')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'father_name', 'national_id', 'shenasname_no', 'shenasname_place')
        }),
        ('تحصیلات', {
            'fields': ('education_level', 'major')
        }),
        ('اطلاعات تماس', {
            'fields': ('mobile',)
        }),
        ('دوره و تاریخ', {
            'fields': ('domains', 'registration_date')
        }),
        ('وضعیت', {
            'fields': ('status',)
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'نام و نام خانوادگی'

    def get_domains_display(self, obj):
        return ' , '.join(obj.get_domains_list())
    get_domains_display.short_description = 'حوزه‌های انتخابی'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'phone', 'email', 'service_type', 'created_at')
    list_filter = ('service_type', 'created_at')
    search_fields = ('fullname', 'phone', 'email', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        ('اطلاعات تماس', {
            'fields': ('fullname', 'phone', 'email')
        }),
        ('درخواست', {
            'fields': ('service_type', 'message')
        }),
        ('زمان ثبت', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(LoginModel)
class LoginModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_phone_verified', 'created_at')
    list_filter = ('is_phone_verified', 'created_at')
    search_fields = ('phone', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('phone', 'code')
    readonly_fields = ('created_at',)
