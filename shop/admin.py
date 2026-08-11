from django.contrib import admin
from .models import WebsiteOrder, Template, WebsitePlan, WebsitePlanOrder, DigitalMarketing


@admin.register(WebsiteOrder)
class WebsiteOrderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number',
                    'email', 'business_field', 'created_at']
    list_filter = ['has_website', 'business_field',
                   'created_at', 'is_processed']
    search_fields = ['full_name', 'phone_number',
                     'email', 'business_field', 'goals']
    readonly_fields = ['created_at', 'raw_data']

    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('full_name', 'phone_number', 'email')
        }),
        ('اطلاعات سفارش', {
            'fields': ('has_website', 'current_website_url', 'business_field', 'goals', 'design_styles', 'selected_color')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('raw_data', 'created_at', 'is_processed'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_popular', 'is_active', 'created_at')
    list_filter = ('is_popular', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'description')
        }),
        ('تصاویر اصلی', {
            'fields': ('image', 'desktop_image', 'tablet_image', 'mobile_image')
        }),
        ('بخش‌های دسکتاپ', {
            'fields': (
                'desktop_home',
                'desktop_about',
                'desktop_store',
                'desktop_cart',
                'desktop_blog',
                'desktop_login',
                'desktop_dash',
            ),
            'classes': ('collapse',)
        }),
        ('بخش‌های تبلت', {
            'fields': (
                'tablet_home',
                'tablet_store',
                'tablet_about',
                'tablet_blog',
                'tablet_cart',
                'tablet_login',
                'tablet_dash',
            ),
            'classes': ('collapse',)
        }),
        ('بخش‌های موبایل', {
            'fields': (
                'mobile_home',
                'mobile_store',
                'mobile_about',
                'mobile_blog',
                'mobile_cart',
                'mobile_login',
                'mobile_dash',
            ),
            'classes': ('collapse',)
        }),
        ('وضعیت', {
            'fields': ('is_popular', 'is_active')
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(WebsitePlan)
class WebsitePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price_display', 
                    'is_active', 'created_at')
    list_filter = ('plan_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'plan_type', 'price', 'description')
        }),
        ('ویژگی‌ها', {
            'fields': ('features',),
            'classes': ('wide',)
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('زمان‌ها', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def price_display(self, obj):
        """نمایش قیمت با جداکننده هزارگان"""
        return f"{obj.price:,} تومان"
    price_display.short_description = 'قیمت'


# ===== اضافه کردن ادمین برای WebsitePlanOrder =====
@admin.register(WebsitePlanOrder)
class WebsitePlanOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'plan', 'status_display', 
                    'amount_display', 'created_at')
    list_filter = ('status', 'plan', 'created_at', 'paid_at')
    search_fields = ('user__username', 'user__email', 
                     'transaction_id', 'domain')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'plan')
    
    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': ('user', 'plan', 'status', 'amount')
        }),
        ('اطلاعات پرداخت', {
            'fields': ('transaction_id', 'paid_at'),
            'classes': ('collapse',)
        }),
        ('اطلاعات تکمیلی', {
            'fields': ('domain', 'description')
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_display(self, obj):
        """نمایش وضعیت به فارسی"""
        status_map = {
            'pending': '⏳ در انتظار پرداخت',
            'paid': '✅ پرداخت شده',
            'failed': '❌ پرداخت ناموفق',
            'processing': '🔄 در حال اجرا',
            'completed': '✔️ تکمیل شده',
        }
        return status_map.get(obj.status, obj.status)
    status_display.short_description = 'وضعیت'
    
    def amount_display(self, obj):
        """نمایش مبلغ با جداکننده هزارگان"""
        return f"{obj.amount:,} تومان"
    amount_display.short_description = 'مبلغ'


@admin.register(DigitalMarketing)
class DigitalMarketingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'service_choices']
    search_fields = ['full_name', 'phone', 'work_name', 'service_choices']