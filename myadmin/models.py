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