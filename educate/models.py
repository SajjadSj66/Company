from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# ============================
# مدل‌های دوره (همانند قبل)
# ============================
class Course(models.Model):
    CATEGORY_CHOICES = [
        ('fullstack', 'برنامه‌نویسی Full-Stack'),
        ('ui_ux', 'طراحی رابط کاربری (UI/UX)'),
        ('digital_business', 'مدیریت کسب و کار دیجیتال'),
    ]

    title = models.CharField('عنوان دوره', max_length=200)
    slug = models.SlugField('اسلاگ', unique=True, blank=True, allow_unicode=True)
    category = models.CharField('دسته‌بندی', max_length=50, choices=CATEGORY_CHOICES)
    short_description = models.CharField('توضیح کوتاه', max_length=300)
    description = models.TextField('توضیحات کامل', blank=True)
    practical_percentage = models.PositiveSmallIntegerField('درصد بخش عملی', default=70)
    image = models.ImageField('تصویر دوره', upload_to='courses/', blank=True, null=True)
    price = models.DecimalField('قیمت (تومان)', max_digits=10, decimal_places=0, default=0)
    is_popular = models.BooleanField('دوره محبوب', default=True)
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'دوره'
        verbose_name_plural = 'دوره‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:detail', args=[self.slug])


class CourseFeature(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='features')
    title = models.CharField('عنوان ویژگی', max_length=100)
    icon = models.CharField('آیکون', max_length=50, blank=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# ============================
# مدل‌های سبد خرید و سفارش
# ============================
class Cart(models.Model):
    """
    سبد خرید هر کاربر. هر کاربر فقط یک سبد خرید دارد (OneToOne).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='کاربر'
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'

    def __str__(self):
        return f"سبد خرید {self.user.username}"

    def total_price(self) -> Decimal:
        """جمع کل قیمت سبد خرید بر اساس آیتم‌ها."""
        total = sum(item.total_price() for item in self.items.all())
        return total

    def total_items(self) -> int:
        """تعداد کل آیتم‌ها (تعداد دوره‌ها، نه تعداد واحدها)."""
        return self.items.count()

    def clear(self):
        """خالی کردن سبد خرید (حذف همه آیتم‌ها)."""
        self.items.all().delete()


class CartItem(models.Model):
    """
    آیتم داخل سبد خرید: یک دوره خاص با تعداد مشخص.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سبد خرید'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='دوره'
    )
    quantity = models.PositiveIntegerField('تعداد', default=1)

    class Meta:
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم‌های سبد خرید'
        unique_together = ('cart', 'course')  # جلوگیری از تکراری شدن دوره در یک سبد

    def __str__(self):
        return f"{self.course.title} (تعداد: {self.quantity})"

    def total_price(self) -> Decimal:
        """قیمت کل این آیتم = قیمت دوره * تعداد"""
        return self.course.price * self.quantity

    def clean(self):
        # اعتبارسنجی: تعداد نباید صفر یا منفی باشد
        if self.quantity < 1:
            raise ValidationError({'quantity': 'تعداد باید حداقل ۱ باشد.'})
        # در صورت لزوم: حداکثر تعداد مجاز (مثلاً 10)
        if self.quantity > 10:
            raise ValidationError({'quantity': 'حداکثر تعداد مجاز ۱۰ عدد است.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # اجرای اعتبارسنجی قبل از ذخیره
        super().save(*args, **kwargs)


class Order(models.Model):
    """
    سفارش نهایی ثبت شده توسط کاربر. شامل اطلاعات صورتحساب و وضعیت پرداخت.
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'پرداخت ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازگشت وجه'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='کاربر'
    )
    # اطلاعات کاربر در زمان ثبت سفارش (برای جلوگیری از تغییرات بعدی پروفایل)
    full_name = models.CharField('نام کامل', max_length=150)
    email = models.EmailField('ایمیل')
    phone = models.CharField('شماره تلفن', max_length=15)
    address = models.TextField('آدرس')
    postal_code = models.CharField('کد پستی', max_length=10)
    city = models.CharField('شهر', max_length=100, blank=True)
    state = models.CharField('استان', max_length=100, blank=True)

    # اطلاعات مالی و وضعیت
    total_amount = models.DecimalField('مبلغ کل', max_digits=10, decimal_places=0, default=0)
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField('شناسه پرداخت', max_length=100, blank=True)

    # زمان‌ها
    created_at = models.DateTimeField('تاریخ ثبت سفارش', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش #{self.id} - {self.full_name}"

    def calculate_total_amount(self):
        """محاسبه مجموع مبالغ آیتم‌های سفارش (در صورت وجود آیتم‌ها)."""
        total = sum(item.total_price() for item in self.items.all())
        return total

    def save(self, *args, **kwargs):
        # اگر مبلغ کل صفر است و سفارش در حال ایجاد است، از آیتم‌ها محاسبه کن
        if not self.pk and not self.total_amount:
            # توجه: در زمان ایجاد سفارش، آیتم‌ها هنوز اضافه نشده‌اند، بنابراین اینجا کاری نمی‌کنیم.
            # بهتر است در ویو پس از اضافه کردن آیتم‌ها، total_amount را محاسبه کنیم.
            pass
        super().save(*args, **kwargs)

    def mark_as_paid(self, transaction_id=None):
        """تغییر وضعیت به پرداخت شده و ثبت زمان و کد رهگیری."""
        self.status = 'paid'
        if transaction_id:
            self.transaction_id = transaction_id
        from django.utils import timezone
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'transaction_id', 'paid_at'])


class OrderItem(models.Model):
    """
    آیتم‌های سفارش: دوره و قیمت در زمان خرید (ثبت نهایی قیمت).
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='دوره'
    )
    price_at_purchase = models.DecimalField(
        'قیمت هنگام خرید',
        max_digits=10,
        decimal_places=0,
        help_text='قیمت دوره در زمان ثبت سفارش'
    )
    quantity = models.PositiveIntegerField('تعداد', default=1)

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
        unique_together = ('order', 'course')  # جلوگیری از تکراری شدن دوره در یک سفارش

    def __str__(self):
        return f"{self.course.title} - {self.order.id}"

    def total_price(self) -> Decimal:
        return self.price_at_purchase * self.quantity