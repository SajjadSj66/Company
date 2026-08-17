import os
from django.db import models
from users.models import Category
from shop.models import Template
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError


User = get_user_model()


def media_upload_path(instance, filename):
    return f"media_library/{instance.category or 'general'}/{filename}"


class MediaFolder(models.Model):
    name = models.CharField(_("نام پوشه"), max_length=100)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        related_name="children", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("پوشه رسانه")
        verbose_name_plural = _("پوشه‌های رسانه")

    def __str__(self):
        return self.name


class MediaFile(models.Model):
    class FileType(models.TextChoices):
        IMAGE = "image", _("تصویر")
        VIDEO = "video", _("ویدیو")
        PDF = "pdf", _("پی‌دی‌اف")
        OTHER = "other", _("سایر")

    title = models.CharField(_("عنوان"), max_length=255, blank=True)
    file = models.FileField(_("فایل"), upload_to=media_upload_path)
    file_type = models.CharField(
        _("نوع فایل"), max_length=10,
        choices=FileType.choices, editable=False
    )
    size = models.PositiveIntegerField(_("حجم (بایت)"), editable=False, default=0)
    folder = models.ForeignKey(
        MediaFolder, null=True, blank=True,
        related_name="files", on_delete=models.SET_NULL,
        verbose_name=_("پوشه")
    )
    uploaded_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("آپلود کننده")
    )
    created_at = models.DateTimeField(_("تاریخ آپلود"), auto_now_add=True)

    class Meta:
        verbose_name = _("فایل رسانه")
        verbose_name_plural = _("کتابخانه رسانه")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.filename

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def size_display(self):
        size = self.size
        for unit in ["بایت", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != "بایت" else f"{size} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size
            ext = os.path.splitext(self.file.name)[1].lower().lstrip(".")
            if ext in ("jpg", "jpeg", "png", "webp", "gif", "svg"):
                self.file_type = self.FileType.IMAGE
            elif ext in ("mp4", "mov", "avi", "mkv", "webm"):
                self.file_type = self.FileType.VIDEO
            elif ext == "pdf":
                self.file_type = self.FileType.PDF
            else:
                self.file_type = self.FileType.OTHER
        super().save(*args, **kwargs)



class Comment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("در انتظار بازبینی")
        APPROVED = "approved", _("تأیید شده")
        SPAM = "spam", _("هرزنامه")

    # نویسنده دیدگاه (اگر کاربر مهمان بود، می‌تونی این رو null بذاری و اسم رو جدا ذخیره کنی)
    author = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("نویسنده")
    )
    guest_name = models.CharField(_("نام مهمان"), max_length=100, blank=True)

    # ارتباط عمومی با هر مدلی (مقاله، محصول و ...) که دیدگاه روش ثبت شده
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    body = models.TextField(_("نوشته"))
    status = models.CharField(
        _("وضعیت"), max_length=10,
        choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(_("تاریخ"), auto_now_add=True)
    reviewed_at = models.DateTimeField(_("تاریخ بازبینی"), null=True, blank=True)

    class Meta:
        verbose_name = _("دیدگاه")
        verbose_name_plural = _("دیدگاه‌ها")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.display_name}: {self.body[:30]}"

    @property
    def display_name(self):
        return self.author.get_full_name() if self.author else self.guest_name or "ناشناس"


LANGUAGE_CHOICES = [
    ("fa", _("فارسی")),
    ("en", _("English")),
    ("ar", _("عربی")),
]

TIMEZONE_CHOICES = [
    ("Asia/Tehran", _("تهران")),
    ("Asia/Dubai", _("دبی")),
    ("Europe/Berlin", _("برلین")),
    ("UTC", "UTC"),
]


class SiteSettings(models.Model):
    site_title = models.CharField(_("عنوان سایت"), max_length=100)
    tagline = models.CharField(_("شعار"), max_length=200, blank=True)

    site_url = models.URLField(_("آدرس سایت (URL)"))
    wordpress_url = models.URLField(_("آدرس وردپرس (URL)"), blank=True)

    admin_email = models.EmailField(_("ایمیل مدیر"))

    allow_registration = models.BooleanField(_("اجازه ثبت‌نام به کاربران جدید"), default=False)

    language = models.CharField(_("زبان سایت"), max_length=10, choices=LANGUAGE_CHOICES, default="fa")
    timezone = models.CharField(_("منطقه زمانی"), max_length=50, choices=TIMEZONE_CHOICES, default="Asia/Tehran")

    favicon = models.ImageField(_("Favicon سایت"), upload_to="site/", blank=True, null=True)

    updated_at = models.DateTimeField(_("آخرین بروزرسانی"), auto_now=True)

    class Meta:
        verbose_name = _("تنظیمات سایت")
        verbose_name_plural = _("تنظیمات سایت")

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        self.pk = 1  # همیشه فقط یک رکورد (singleton)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # جلوگیری از حذف تنظیمات

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1, defaults={
            "site_title": "",
            "site_url": "",
            "admin_email": "",
        })
        return obj

    def clean(self):
        if self.favicon:
            valid_ext = (".png", ".ico")
            if not self.favicon.name.lower().endswith(valid_ext):
                raise ValidationError({"favicon": _("فرمت فایل باید PNG یا ICO باشد.")})


class Writen(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="templates")


class ReadingSettings(models.Model):
    class HomepageDisplay(models.TextChoices):
        LATEST_POSTS = "latest_posts", _("آخرین نوشته‌ها")
        STATIC_PAGE = "static_page", _("صفحه ثابت")

    homepage_display = models.CharField(
        _("صفحه نخست نمایش می‌دهد"),
        max_length=20,
        choices=HomepageDisplay.choices,
        default=HomepageDisplay.LATEST_POSTS,
    )
    posts_per_page = models.PositiveIntegerField(
        _("تعداد نوشته در هر صفحه"), default=10
    )

    # این فیلد کل سایت رو کنترل می‌کنه
    allow_search_indexing = models.BooleanField(
        _("قابلیت مشاهده برای موتورهای جستجو"),
        default=True,
        help_text=_("در صورت غیرفعال بودن، کل صفحات سایت از ایندکس گوگل و سایر موتورهای جستجو خارج می‌شوند."),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("تنظیمات خواندن")
        verbose_name_plural = _("تنظیمات خواندن")

    def __str__(self):
        return "تنظیمات خواندن"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete("reading_settings")  # کش رو پاک کن تا تغییرات فوری اعمال بشه

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        from django.core.cache import cache
        obj = cache.get("reading_settings")
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            cache.set("reading_settings", obj, 3600)
        return obj


class SEOSettings(models.Model):
    # ---------- بخش اول: تنظیمات عمومی سئو ----------
    class TitleSeparator(models.TextChoices):
        DASH = "-", "- (خط تیره)"
        PIPE = "|", "| (پایپ)"
        DOT = "•", "• (نقطه)"
        COLON = ":", ": (دو نقطه)"

    title_separator = models.CharField(
        _("جداکننده عنوان"), max_length=5,
        choices=TitleSeparator.choices, default=TitleSeparator.DASH,
    )

    # این فیلد یک "قالب" هست، یعنی متنی که کاربر خودش می‌نویسه
    # می‌تونی بعداً پلیس‌هولدرهایی مثل {site_name} رو هم توش پشتیبانی کنی
    homepage_title_template = models.CharField(
        _("قالب عنوان سئوی صفحه اصلی"), max_length=255
    )
    homepage_meta_description = models.TextField(
        _("توضیحات سئوی صفحه اصلی"), max_length=320,
        help_text=_("حداکثر ۱۶۰ تا ۳۲۰ کاراکتر توصیه می‌شود.")
    )

    # ---------- بخش دوم: شبکه‌های اجتماعی و Open Graph ----------
    og_image = models.ImageField(
        _("تصویر پیش‌فرض اشتراک‌گذاری (OG Image)"),
        upload_to="seo/og/", blank=True, null=True,
        help_text=_("اندازه پیشنهادی ۱۲۰۰×۶۳۰ پیکسل")
    )
    instagram_url = models.URLField(_("اینستاگرام"), blank=True)
    linkedin_url = models.URLField(_("لینکدین"), blank=True)

    # ---------- بخش سوم: نقشه سایت و ربات‌ها ----------
    sitemap_auto_generate = models.BooleanField(
        _("تولید خودکار XML Sitemap"), default=True,
        help_text=_("ساخت و به‌روزرسانی خودکار sitemap.xml")
    )
    # این تنها منبع تصمیم‌گیری درباره ایندکس شدن کل سایت است
    allow_search_indexing = models.BooleanField(
        _("قابلیت مشاهده برای موتورهای جستجو"), default=True,
        help_text=_("در صورت غیرفعال بودن، کل سایت noindex می‌شود.")
    )
    robots_txt_content = models.TextField(
        _("ویرایشگر Robots.txt"), blank=True,
        default="User-agent: *\nAllow: /\n",
        help_text=_("این متن فقط زمانی اعمال می‌شود که «قابلیت مشاهده» فعال باشد.")
    )

    # ---------- بخش چهارم: Schema پیش‌فرض سازمان ----------
    class SchemaType(models.TextChoices):
        ORGANIZATION = "Organization", _("سازمان (Organization)")
        LOCAL_BUSINESS = "LocalBusiness", _("کسب‌وکار محلی (LocalBusiness)")
        PERSON = "Person", _("شخص (Person)")
        WEBSITE = "WebSite", _("وب‌سایت (WebSite)")

    schema_type = models.CharField(
        _("نوع Schema سازمان"), max_length=20,
        choices=SchemaType.choices, default=SchemaType.ORGANIZATION,
    )
    schema_phone = models.CharField(
        _("شماره تماس سازمان"), max_length=20, blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("تنظیمات سئو")
        verbose_name_plural = _("تنظیمات سئو")

    def __str__(self):
        return "تنظیمات سئو"

    # ---------- الگوی Singleton (مثل تنظیمات قبلی) ----------
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete("seo_settings")

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        from django.core.cache import cache
        obj = cache.get("seo_settings")
        if obj is None:
            obj, _created = cls.objects.get_or_create(pk=1)
            cache.set("seo_settings", obj, 3600)
        return obj

    def clean(self):
        if self.schema_phone and not self.schema_phone.startswith("+"):
            raise ValidationError({
                "schema_phone": _("شماره باید با کد کشور شروع شود، مثل +98...")
            })