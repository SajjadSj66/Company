from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    پروفایل کاربر با اطلاعات کامل
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_profile'
    )
    wallet_balance = models.DecimalField(
        'موجودی کیف پول',
        max_digits=12,
        decimal_places=0,
        default=0
    )

    # ===== متدهای کیف پول =====
    def add_to_wallet(self, amount):
        """افزایش موجودی کیف پول"""
        self.wallet_balance += amount
        self.save(update_fields=['wallet_balance'])
        # ثبت تراکنش
        UserTransaction.objects.create(
            user=self.user,
            amount=amount,
            type='deposit',
            description=f'شارژ کیف پول - مبلغ {amount:,} تومان'
        )
        return self.wallet_balance

    def deduct_from_wallet(self, amount):
        """کسر از موجودی کیف پول"""
        if self.wallet_balance < amount:
            raise ValueError('موجودی کیف پول کافی نیست')
        self.wallet_balance -= amount
        self.save(update_fields=['wallet_balance'])
        # ثبت تراکنش
        UserTransaction.objects.create(
            user=self.user,
            amount=amount,
            type='payment',
            description=f'پرداخت - مبلغ {amount:,} تومان'
        )
        return self.wallet_balance

    def get_wallet_balance(self):
        """دریافت موجودی کیف پول"""
        return self.wallet_balance

    # اطلاعات شخصی
    phone = models.CharField('شماره موبایل', max_length=11, unique=True)
    first_name = models.CharField('نام', max_length=100, blank=True)
    last_name = models.CharField('نام خانوادگی', max_length=100, blank=True)
    is_phone_verified = models.BooleanField(default=False)

    # وضعیت اشتراک
    MEMBERSHIP_CHOICES = [
        ('free', 'رایگان'),
        ('gold', 'طلایی'),
        ('platinum', 'پلاتینیوم'),
    ]
    membership = models.CharField(
        'نوع اشتراک',
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='free'
    )

    # آمار
    courses_count = models.PositiveIntegerField('تعداد دوره‌ها', default=0)
    tickets_count = models.PositiveIntegerField('تعداد تیکت‌ها', default=0)
    projects_count = models.PositiveIntegerField('تعداد پروژه‌ها', default=0)
    total_payments = models.DecimalField(
        'مجموع پرداخت‌ها', max_digits=12, decimal_places=0, default=0)

    # زمان‌ها
    last_login_display = models.DateTimeField(
        'آخرین ورود', blank=True, null=True)
    created_at = models.DateTimeField('تاریخ عضویت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل کاربران'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.membership}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.user.username

    def get_membership_badge(self):
        """بازگرداندن بج اشتراک"""
        badges = {
            'free': {'color': '#64748b', 'label': 'رایگان'},
            'gold': {'color': '#eab308', 'label': 'طلایی'},
            'platinum': {'color': '#8b5cf6', 'label': 'پلاتینیوم'},
        }
        return badges.get(self.membership, badges['free'])

class Category(models.Model):
    name = models.CharField('نام', max_length=200, unique=True)
    slug = models.SlugField('اسلاگ',max_length=50,unique=True,allow_unicode=True)
    icon = models.ImageField('آیکون', upload_to='tags/', blank=True, null=True)
    description = models.TextField('توضیحات', blank=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.get_name_display()


    def get_absolute_url(self):
        return reverse('users:category_detail', args=[self.slug])

    @property
    def article_count(self):
        return self.articles.filter(is_published=True).count()


class Tag(models.Model):
    name = models.CharField('نام', max_length=200, unique=True)
    slug = models.SlugField('اسلاگ',max_length=50,unique=True,allow_unicode=True)
    icon = models.ImageField('آیکون', upload_to='tags/', blank=True, null=True)
    description = models.TextField('توضیحات', blank=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    
    class Meta:
            verbose_name = 'دسته‌بندی'
            verbose_name_plural = 'دسته‌بندی‌ها'
            ordering = ['-created_at']
    
    def __str__(self):
            return self.get_name_display()
    
    
    def get_absolute_url(self):
            return reverse('users:category_detail', args=[self.slug])
    
    @property
    def article_count(self):
            return self.articles.filter(is_published=True).count()


class Article(models.Model):
    """مدل مقاله"""
    STATUS_CHOICES=[
        ('prepublish', 'پیش نمایس'),
        ('published', 'منتشر شده'),
        ('private', 'خصوصی'),
        ('timed', 'زمانبندی شده'),
        ('deleted', 'حذف شده')
    ]
    SCHEMA_CHOICES=[
        ('article', 'مقاله'),
        ('blogposting', 'پست بلاگ'),
        ('product', 'محصول'),
        ('faq', 'سوالات متداول'),
        ('howto', 'آموزش گام به گام'),
        ('organization', 'سازمان'),
        ('localbusiness', 'کسب و کار محلی'),
        ('beadcrumb', 'مسیر ناوبری'),
        ('person', 'شخص'),
        ('review', 'نقد و بررسی')
    ]
    title = models.CharField('عنوان', max_length=250)
    slug = models.SlugField('اسلاگ', max_length=280,unique=True, allow_unicode=True)
    excerpt = models.TextField('خلاصه', max_length=500, blank=True)
    content = models.TextField('محتوا')
    image = models.ImageField('تصویر شاخص', upload_to=' blogs/', blank=True, null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='articles',verbose_name='دسته‌بندی')
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='articles',verbose_name='نویسنده')
    tags = models.ManyToManyField(Tag,related_name='articles',blank=True,verbose_name='برچسب‌ها')
    status = models.CharField('وضعیت', max_length=40, choices=STATUS_CHOICES)

    # اطلاعات مقاله
    read_time = models.PositiveSmallIntegerField('زمان مطالعه (دقیقه)', default=5)
    is_published = models.BooleanField('منتشر شده', default=False)
    is_featured = models.BooleanField('ویژه', default=False)

    # آمار
    views = models.PositiveIntegerField('بازدید', default=0)
    likes = models.PositiveIntegerField('لایک', default=0)

    # SEO
    seo_title = models.CharField('عنوان SEO', max_length=150, blank=True)
    seo_description = models.CharField('توضیحات SEO', max_length=200, blank=True)
    seo_keywords = models.CharField('کلمات کلیدی SEO', max_length=200, blank=True)
    canonical_url = models.URLField('url متعارف')
    schema = models.CharField('نشانه گذاری', max_length=50, choices=SCHEMA_CHOICES)

    
    published_date = models.DateTimeField('تاریخ انتشار',blank=True, null=True)
    publish_time = models.TimeField('ساعت انتشار', blank=True, null=True)

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at']
        

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('users:article_detail', args=[self.slug])

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

class Comment(models.Model):
    """مدل نظرات"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='مقاله'
    )
    author_name = models.CharField('نام', max_length=100)
    author_email = models.EmailField('ایمیل', blank=True)
    content = models.TextField('متن نظر')
    is_approved = models.BooleanField('تایید شده', default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='پاسخ به'
    )
    created_at = models.DateTimeField('تاریخ', auto_now_add=True)

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author_name} - {self.article.title[:30]}'


class UserCourse(models.Model):
    """
    دوره‌های ثبت‌نام شده کاربر
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_courses'
    )
    course = models.ForeignKey(
        'educate.Course',
        on_delete=models.CASCADE
    )
    progress = models.PositiveSmallIntegerField('پیشرفت', default=0)
    registered_at = models.DateTimeField('تاریخ ثبت‌نام', auto_now_add=True)
    is_completed = models.BooleanField('تکمیل شده', default=False)

    # ===== فیلدهای جدید =====
    order = models.ForeignKey(
        'educate.CourseOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_courses',
        verbose_name='سفارش مرتبط'
    )
    payment_status = models.CharField(
        'وضعیت پرداخت',
        max_length=20,
        choices=[
            ('pending', 'در انتظار پرداخت'),
            ('paid', 'پرداخت شده'),
            ('failed', 'ناموفق'),
        ],
        default='pending'
    )
    transaction_id = models.CharField(
        'شناسه پرداخت', max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)

    class Meta:
        verbose_name = 'دوره کاربر'
        verbose_name_plural = 'دوره‌های کاربران'
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.progress}%)"


class UserTicket(models.Model):
    """
    تیکت‌های پشتیبانی کاربر
    """
    STATUS_CHOICES = [
        ('open', 'باز'),
        ('in_progress', 'در حال بررسی'),
        ('closed', 'بسته'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_tickets'
    )
    title = models.CharField('عنوان', max_length=200)
    description = models.TextField('توضیحات')
    status = models.CharField('وضعیت', max_length=20,
                              choices=STATUS_CHOICES, default='open')
    priority = models.CharField('اولویت', max_length=20, default='normal')
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'تیکت کابر'
        verbose_name_plural = 'تیکت های کابران'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"


class UserReview(models.Model):
    """
    نظرات کاربران
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_reviews'
    )
    course = models.ForeignKey(
        'educate.Course',
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        'امتیاز', choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField('نظر')
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'نظر کابر'
        verbose_name_plural = 'نظزات کاربران'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}⭐)"


class UserTransaction(models.Model):
    """
    تراکنش‌های مالی کاربر
    """
    TYPE_CHOICES = [
        ('deposit', 'شارژ'),
        ('payment', 'پرداخت'),
        ('refund', 'بازگشت'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_transactions'
    )
    amount = models.DecimalField('مبلغ', max_digits=12, decimal_places=0)
    type = models.CharField('نوع', max_length=20, choices=TYPE_CHOICES)
    description = models.CharField('توضیحات', max_length=200, blank=True)
    created_at = models.DateTimeField('تاریخ', auto_now_add=True)

    class Meta:
        verbose_name = 'تراکنش کابر'
        verbose_name_plural = 'تراکنش های کابران'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount}"


class ContactRequest(models.Model):
    PROJECT_CHOICES=[
        ('company', 'سایت شرکتی'),
        ('store', 'سایت فروشگاهی'),
        ('personal', 'سایت شخصی')
    ]
    full_name = models.CharField('نام و نام خانوادگی', max_length=200)
    phone_or_email = models.CharField(max_length=150,verbose_name="شماره تماس یا ابمیل" , blank=True, null=True)
    work_name = models.CharField(max_length=100, verbose_name="نام شرکت", blank=True, null=True)
    project_choices = models.CharField(choices=PROJECT_CHOICES, max_length=40, verbose_name='نوع پروژه' , blank=True, null=True)
    message = models.TextField('توضیحات کوتاه', blank=True, null=True)
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست مشاوره'
        verbose_name_plural = 'درخواست‌های مشاوره'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name



class CourseRegistration(models.Model):
    EDUCATION_CHOICES = [
        ('diploma', 'دیپلم'),
        ('bachelor', 'لیسانس'),
        ('master', 'فوق لیسانس'),
        ('phd', 'دکترا'),
        ('other', 'سایر'),
    ]
    DOMAIN_CHOICES = [
        ('python-django', 'Python / Django'),
        ('htmlcssjs', 'HTML / CSS / JS'),
        ('ai', 'AI / هوش مصنوعی'),
        ('laravel', 'PHP / Laravel'),
    ]

    first_name = models.CharField('نام', max_length=100)
    last_name = models.CharField('نام خانوادگی', max_length=100)
    father_name = models.CharField('نام پدر', max_length=100, blank=True)
    national_id = models.CharField('کد ملی', max_length=10, blank=True)
    shenasname_no = models.CharField(
        'شماره شناسنامه', max_length=20, blank=True)
    shenasname_place = models.CharField(
        'محل صدور شناسنامه', max_length=100, blank=True)
    education_level = models.CharField(
        'آخرین مدرک تحصیلی',
        max_length=20,
        choices=EDUCATION_CHOICES,
        blank=True
    )
    major = models.CharField('رشته تحصیلی', max_length=150, blank=True)
    domains = models.CharField(
        'حوزه تخصصی',
        max_length=20,
        blank=True
    )
    mobile = models.CharField(
        'تلفن همراه', max_length=15, blank=True, unique=True, db_index=True)
    registration_date = models.CharField('تاریخ ثبت نام', max_length=20)
    status = models.CharField('وضعیت', max_length=20, choices=[(
        'pending', 'در انتظار بررسی'), ('approved', 'تایید شده'), ('rejected', 'رد شده'), ('contacted', 'تماس گرفته شده')], default='pending')

    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'ثبت‌نام دوره'
        verbose_name_plural = 'ثبت‌نام‌های دوره'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.mobile}'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_domains_list(self):
        """بازگرداندن حوزه‌های انتخابی به صورت لیست"""
        return [d.strip() for d in self.domains.split(',') if d.strip()]


class LoginModel(models.Model):
    """
    پروفایل کاربر با شماره موبایل
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='login_model'
    )
    phone = models.CharField(
        'شماره موبایل',
        max_length=11,
        unique=True,
        db_index=True
    )
    is_phone_verified = models.BooleanField(
        'شماره تایید شده',
        default=False
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = "لاگین"
        verbose_name_plural = "لاگین ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phone}"


class OTPCode(models.Model):
    """
    ذخیره کدهای تایید یکبار مصرف
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otp_codes'
    )
    phone = models.CharField('شماره موبایل', max_length=11)
    code = models.CharField('کد تایید', max_length=6)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    expires_at = models.DateTimeField('تاریخ انقضا')
    is_used = models.BooleanField('استفاده شده', default=False)

    class Meta:
        verbose_name = "کد تایید"
        verbose_name_plural = "کد های تایید"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone} - {self.code}"

    def is_valid(self):
        """بررسی اعتبار کد"""
        return not self.is_used and self.expires_at > timezone.now()


class ContactMessage(models.Model):
    SERVICE_CHOICES = [
        ('web_design', 'طراحی و توسعه وب‌سایت'),
        ('digital_marketing', 'دیجیتال مارکتینگ'),
        ('branding', 'برندینگ و خلاقیت'),
        ('seo', 'سئو و بهینه‌سازی'),
        ('consulting', 'مشاوره دیجیتال'),
    ]
    fullname = models.CharField(
        max_length=150, verbose_name='نام و نام خانوادگی')
    phone = models.CharField(max_length=11, verbose_name='شماره تماس')
    email = models.EmailField(verbose_name='آدرس ایمیل')
    service_type = models.CharField(
        max_length=20, choices=SERVICE_CHOICES, verbose_name='نوع خدمات')
    message = models.TextField(verbose_name='پیام')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "تماس با ما"
        verbose_name_plural = "تماس با ما"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.fullname} - {self.service_type}"


class Collaboration(models.Model):
    """
    مدل درخواست همکاری (ارسال رزومه)
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('reviewing', 'در حال بررسی'),
        ('accepted', 'تایید شده'),
        ('rejected', 'رد شده'),
    ]
    WORK_CHOICES = [
        ('frontend', 'توسعه دهنده فرانت اند'),
        ('backend', 'توسعه دهنده بک اند'),
        ('fullstack', 'فول استک'),
        ('designer', 'طراح UI/UX'),
    ]
    

    
    # ===== اطلاعات فرم =====
    full_name = models.CharField('نام کامل', max_length=200)
    phone = models.CharField('شماره تماس', max_length=20)
    email = models.EmailField('ایمیل', blank=True)
    message = models.TextField('پیام تکمیلی', blank=True)
    portfolio = models.URLField('نمونه کار', blank=True, null=True)
    work_choices = models.CharField('موقعیت شغلی', max_length=20, choices=WORK_CHOICES, blank=True, null=True)
    
    # ===== فایل رزومه =====
    resume_file = models.FileField(
        'فایل رزومه',
        upload_to='collaborations/resumes/%Y/%m/',
        blank=True,
        null=True,
        help_text='فایل‌های PDF، Word یا TXT (اختیاری)'
    )
    

    
    # ===== وضعیت =====
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField('یادداشت ادمین', blank=True)
    
    # ===== زمان‌ها =====
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'درخواست همکاری'
        verbose_name_plural = 'درخواست‌های همکاری'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.created_at.strftime('%Y/%m/%d')}"
    
    def get_file_name(self):
        if self.resume_file:
            return self.resume_file.name.split('/')[-1]
        return 'بدون فایل'

class StudyRequest(models.Model):
    STUDY_CHOICES=[
        ('ai', 'ai'),
        ('backend', 'backend'),
        ('frontend', 'frontend'),
        ('seo', 'seo'),
        ('wordpress', 'wordpress'),
        ('ui/ux', 'ui/ux'),
    ]
    full_name = models.CharField('نام و نام خانوادگی', max_length=200)
    phone_or_email = models.CharField(max_length=150,verbose_name="شماره تماس یا ابمیل" , blank=True, null=True)
    grade = models.CharField(max_length=100, verbose_name="تحصیلات", blank=True, null=True)
    study_choices = models.CharField(choices=STUDY_CHOICES, max_length=40, verbose_name='نوع کلاس' , blank=True, null=True)
    message = models.TextField('توضیحات کوتاه', blank=True, null=True)
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست دوره'
        verbose_name_plural = 'درخواست‌های دوره'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name