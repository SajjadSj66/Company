from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class WebsiteOrder(models.Model):

    HAS_WEBSITE_CHOICES = [
        ('has_domain', 'بله، سایت فعال دارم'),
        ('no_domain', 'خیر، اولین سایتم هست'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='website_orders',
        verbose_name='کاربر'
    )

    has_website = models.CharField(
        max_length=20,
        choices=HAS_WEBSITE_CHOICES,
        default='no_domain',
        verbose_name="آیا سایت داشته‌اید؟"
    )
    current_website_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="آدرس سایت فعلی"
    )

    goals = models.TextField(blank=True, verbose_name="اهداف")

    business_field = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="حوزه کاری"
    )

    design_styles = models.TextField(blank=True, verbose_name="سبک طراحی")

    selected_color = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="رنگ انتخابی"
    )

    full_name = models.CharField(
        max_length=200,
        verbose_name="نام و نام خانوادگی"
    )
    phone_number = models.CharField(
        max_length=15,
        verbose_name="شماره تماس"
    )
    email = models.EmailField(
        verbose_name="ایمیل"
    )

    raw_data = models.JSONField(default=dict, verbose_name="داده‌های خام")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="تاریخ ثبت")
    is_processed = models.BooleanField(
        default=False, verbose_name="پردازش شده")

    class Meta:
        verbose_name = "سفارش طراحی وبسایت"
        verbose_name_plural = "سفارش‌های طراحی وبسایت"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.created_at.strftime('%Y/%m/%d')}"

    def get_goals_list(self):
        return [g.strip() for g in self.goals.split(',') if g.strip()] if self.goals else []

    def get_design_styles_list(self):
        return [s.strip() for s in self.design_styles.split(',') if s.strip()] if self.design_styles else []


class Template(models.Model):
    # ===== اطلاعات اصلی =====
    title = models.CharField('عنوان قالب', max_length=200)
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    description = models.TextField('توضیحات', blank=True)

    # ===== تصاویر اصلی دستگاه‌ها =====
    image = models.ImageField(
        'تصویر اصلی (کارت)', max_length=200, upload_to='templates/', blank=True, null=True)
    desktop_image = models.ImageField(
        'تصویر اصلی دسکتاپ', max_length=200, upload_to='templates/desktop/', blank=True, null=True)
    tablet_image = models.ImageField(
        'تصویر اصلی تبلت', max_length=200, upload_to='templates/tablet/', blank=True, null=True)
    mobile_image = models.ImageField(
        'تصویر اصلی موبایل', max_length=200, upload_to='templates/mobile/', blank=True, null=True)

    # ===== بخش‌های دسکتاپ =====
    desktop_home = models.ImageField('دسکتاپ - صفحه اصلی', max_length=200,
                                     upload_to='templates/desktop/sections/', blank=True, null=True)
    desktop_store = models.ImageField(
        'دسکتاپ - صفحه فروشگاه', max_length=200, upload_to='templates/desktop/sections/', blank=True, null=True)
    desktop_about = models.ImageField(
        'دسکتاپ - درباره ما', max_length=200, upload_to='templates/desktop/sections/', blank=True, null=True)
    desktop_blog = models.ImageField(
        'دسکتاپ - وبلاگ', max_length=200, upload_to='templates/desktop/sections/', blank=True, null=True)
    desktop_cart = models.ImageField(
        'دسکتاپ - سبد خرید', max_length=200, upload_to='templates/desktop/sections/', blank=True, null=True)
    desktop_login = models.ImageField(
        'دسکتاپ - لاگین', max_length=200, upload_to='templates/desktop/sections/', blank=True, null=True)
    desktop_dash = models.ImageField(
        'دسکتاپ - داشبورد', max_length=200, upload_to='templates/desktop/sections/', blank=True, null=True)

    # ===== بخش‌های تبلت =====
    tablet_home = models.ImageField('تبلت - صفحه اصلی', max_length=200,
                                    upload_to='templates/tablet/sections/', blank=True, null=True)
    tablet_store = models.ImageField(
        'تبلت - صفحه فروشگاه', max_length=200, upload_to='templates/tablet/sections/', blank=True, null=True)
    tablet_about = models.ImageField(
        'تبلت - درباره ما', max_length=200, upload_to='templates/tablet/sections/', blank=True, null=True)
    tablet_blog = models.ImageField(
        'تبلت - وبلاگ', max_length=200, upload_to='templates/tablet/sections/', blank=True, null=True)
    tablet_cart = models.ImageField('تبلت - سبد خرید', max_length=200,
                                    upload_to='templates/tablet/sections/', blank=True, null=True)
    tablet_login = models.ImageField(
        'تبلت - لاگین', max_length=200, upload_to='templates/tablet/sections/', blank=True, null=True)
    tablet_dash = models.ImageField(
        'تبلت - داشبورد', max_length=200, upload_to='templates/tablet/sections/', blank=True, null=True)

    # ===== بخش‌های موبایل =====
    mobile_home = models.ImageField('موبایل - صفحه اصلی', max_length=200,
                                    upload_to='templates/mobile/sections/', blank=True, null=True)
    mobile_store = models.ImageField('موبایل - صفحه فروشگاه', max_length=200,
                                     upload_to='templates/mobile/sections/', blank=True, null=True)
    mobile_about = models.ImageField(
        'موبایل - درباره ما', max_length=200, upload_to='templates/mobile/sections/', blank=True, null=True)
    mobile_blog = models.ImageField(
        'موبایل - وبلاگ', max_length=200, upload_to='templates/mobile/sections/', blank=True, null=True)
    mobile_cart = models.ImageField('موبایل - سبد خرید', max_length=200,
                                    upload_to='templates/mobile/sections/', blank=True, null=True)
    mobile_login = models.ImageField(
        'موبایل - لاگین', max_length=200, upload_to='templates/mobile/sections/', blank=True, null=True)
    mobile_dash = models.ImageField('موبایل - داشبورد', max_length=200,
                                    upload_to='templates/mobile/sections/', blank=True, null=True)

    # ===== وضعیت =====
    is_popular = models.BooleanField('محبوب', default=False)
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'قالب'
        verbose_name_plural = 'قالب‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_sections(self, device):
        """دریافت لیست بخش‌های یک دستگاه با نام‌های فارسی"""
        sections_map = {
            'desktop': {
                'home': self.desktop_home,
                'store': self.desktop_store,
                'about': self.desktop_about,
                'blog': self.desktop_blog,
                'cart': self.desktop_cart,
                'login': self.desktop_login,
                'dash': self.desktop_dash,
            },
            'tablet': {
                'home': self.tablet_home,
                'store': self.tablet_store,
                'about': self.tablet_about,
                'blog': self.tablet_blog,
                'cart': self.tablet_cart,
                'login': self.tablet_login,
                'dash': self.tablet_dash,
            },
            'mobile': {
                'home': self.mobile_home,
                'store': self.mobile_store,
                'about': self.mobile_about,
                'blog': self.mobile_blog,
                'cart': self.mobile_cart,
                'login': self.mobile_login,
                'dash': self.mobile_dash,
            }
        }

        sections = sections_map.get(device, {})
        result = []

    
        section_names = {
            'home': 'صفحه اصلی',
            'store': 'صفحه فروشگاه',
            'about': 'درباره ما',
            'blog': 'وبلاگ',
            'cart': 'سبد خرید',
            'login': 'لاگین',
            'dash': 'داشبورد'
        }

        for key, image in sections.items():
            if image:
                result.append({
                    'name': section_names.get(key, key),
                    'key': key,
                    'image': image.url
                })

        return result

    def get_main_image(self, device):
        """دریافت تصویر اصلی هر دستگاه"""
        if device == 'desktop' and self.desktop_image:
            return self.desktop_image.url
        elif device == 'tablet' and self.tablet_image:
            return self.tablet_image.url
        elif device == 'mobile' and self.mobile_image:
            return self.mobile_image.url
        return None


class WebsitePlan(models.Model):
    """
    طرح‌های آماده طراحی سایت (برای trahi.html)
    """
    PLAN_TYPES = [
        ('standard', 'استاندارد'),
        ('premium', 'پیشرفته'),
        ('professional', 'حرفه‌ای'),
    ]

    name = models.CharField('نام طرح', max_length=50)
    plan_type = models.CharField(
        'نوع', max_length=20, choices=PLAN_TYPES, unique=True)
    price = models.DecimalField(
        'قیمت (تومان)', max_digits=12, decimal_places=0)
    description = models.TextField('توضیحات', blank=True)
    features = models.JSONField('ویژگی‌ها', default=list)
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'طرح آماده'
        verbose_name_plural = 'طرح‌های آماده'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - {self.price:,} تومان"

    def get_plan_type_display(self):
        """دریافت نام فارسی طرح"""
        plan_names = {
            'standard': 'استاندارد',
            'premium': 'پیشرفته',
            'professional': 'حرفه‌ای',
        }
        return plan_names.get(self.plan_type, self.plan_type)


class WebsitePlanOrder(models.Model):
    """
    سفارش خرید طرح آماده
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'پرداخت ناموفق'),
        ('processing', 'در حال اجرا'),
        ('completed', 'تکمیل شده'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plan_orders'
    )
    plan = models.ForeignKey(
        WebsitePlan,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    status = models.CharField('وضعیت', max_length=20,
                              choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField('مبلغ', max_digits=12, decimal_places=0)
    transaction_id = models.CharField(
        'شناسه پرداخت', max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)

    domain = models.CharField('دامنه درخواستی', max_length=100, blank=True)
    description = models.TextField('توضیحات تکمیلی', blank=True)

    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'سفارش طرح آماده'
        verbose_name_plural = 'سفارش‌های طرح‌های آماده'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.plan.name} - {self.user.username}"
    """
    سفارش خرید طرح آماده
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'پرداخت ناموفق'),
        ('processing', 'در حال اجرا'),
        ('completed', 'تکمیل شده'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plan_orders'
    )
    plan = models.ForeignKey(
        WebsitePlan,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    # اطلاعات سفارش
    status = models.CharField('وضعیت', max_length=20,
                              choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField('مبلغ', max_digits=12, decimal_places=0)
    transaction_id = models.CharField(
        'شناسه پرداخت', max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)

    # اطلاعات تکمیلی
    domain = models.CharField('دامنه درخواستی', max_length=100, blank=True)
    description = models.TextField('توضیحات تکمیلی', blank=True)

    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'سفارش طرح آماده'
        verbose_name_plural = 'سفارش‌های طرح‌های آماده'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.plan.name} - {self.user.username}"


class DigitalMarketing(models.Model):
    SERVICE_CHOICES =[
        ('seo', 'سئو و گوگل ادز'),
        ('web', 'طراحی سایت'),
        ('management', 'مدیرت شبکه های اجتماعی'),
        ('consult', 'مشاوره برندینگ')
    ]
    full_name = models.CharField(max_length=200,verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=15,verbose_name="شماره تماس")
    work_name = models.URLField(max_length=100, verbose_name="نام کسب و کار")
    service_choices = models.CharField(choices=SERVICE_CHOICES, max_length=40, verbose_name='خدمت مورد نیاز')
    message = models.TextField('توضیحات کوتاه')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = "مشاوره دیجیتال مارکتینگ"
        verbose_name_plural = "مشاوره های دیجیتال مارکتینگ"
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name


