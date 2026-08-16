from django import forms
from .models import *
from django.utils.text import slugify
from users.models import Tag , Category, Article

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'slug', 'icon', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام برچسب را وارد کنید'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسلاگ (در صورت خالی بودن خودکار ساخته می‌شود)'
            }),
            'icon': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'توضیحاتی درباره این برچسب'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        if not slug and name:
            slug = slugify(name, allow_unicode=True)
        return slug

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'icon', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام برچسب را وارد کنید'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسلاگ (در صورت خالی بودن خودکار ساخته می‌شود)'
            }),
            'icon': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'توضیحاتی درباره این برچسب'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        if not slug and name:
            slug = slugify(name, allow_unicode=True)
        return slug

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'excerpt', 'content', 'image',
            'category', 'author', 'tags', 'status',
            'read_time','seo_title', 'seo_description', 'seo_keywords',
            'canonical_url', 'schema',
            'published_date', 'publish_time',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان مقاله را وارد کنید'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسلاگ (در صورت خالی بودن خودکار ساخته می‌شود)'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'خلاصه‌ای کوتاه از مقاله'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control editor',  # می‌تونی برای CKEditor/TinyMCE استفاده کنی
                'rows': 15,
                'placeholder': 'محتوای کامل مقاله'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'author': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'seo_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان سئو (اختیاری)'
            }),
            'seo_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'توضیحات متا (اختیاری)'
            }),
            'seo_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'کلمات کلیدی با کاما جدا شوند'
            }),
            'canonical_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/article-slug'
            }),
            'schema': forms.Select(attrs={
                'class': 'form-select'
            }),
            'published_date': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثلاً 1403/05/20 '
            }),
            'publish_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثلاً 14:30'
            }),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        if not slug and title:
            slug = slugify(title, allow_unicode=True)
        return slug

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        published_date = cleaned_data.get('published_date')

        if status == 'timed' and not published_date:
            self.add_error(
                'published_date',
                'برای وضعیت «زمانبندی شده» باید تاریخ انتشار مشخص شود.'
            )
        return cleaned_data


class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ["title", "file", "folder"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "عنوان فایل (اختیاری)"
            }),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "folder": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        max_size_mb = 50
        if file and file.size > max_size_mb * 1024 * 1024:
            raise forms.ValidationError(f"حجم فایل نباید بیشتر از {max_size_mb} مگابایت باشد.")
        return file


class MediaSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "جستجوی فایل..."
    }))
    file_type = forms.ChoiceField(
        required=False,
        choices=[("", "همه نوع‌ها")] + list(MediaFile.FileType.choices),
        widget=forms.Select(attrs={"class": "form-select"})
    )

class CommentStatusForm(forms.ModelForm):
    """برای تغییر وضعیت (تأیید/رد) از پنل مدیریت"""
    class Meta:
        model = Comment
        fields = ["status"]


class CommentSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control", "placeholder": "جستجوی دیدگاه..."
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "همه وضعیت‌ها")] + list(Comment.Status.choices),
        widget=forms.Select(attrs={"class": "form-select"})
    )

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            "site_title", "tagline",
            "site_url", "wordpress_url",
            "admin_email",
            "allow_registration",
            "language", "timezone",
            "favicon",
        ]
        widgets = {
            "site_title": forms.TextInput(attrs={"class": "form-control"}),
            "tagline": forms.TextInput(attrs={"class": "form-control"}),
            "site_url": forms.URLInput(attrs={"class": "form-control", "dir": "ltr"}),
            "wordpress_url": forms.URLInput(attrs={"class": "form-control", "dir": "ltr"}),
            "admin_email": forms.EmailInput(attrs={"class": "form-control", "dir": "ltr"}),
            "allow_registration": forms.CheckboxInput(attrs={"class": "form-check-input toggle-switch"}),
            "language": forms.Select(attrs={"class": "form-select"}),
            "timezone": forms.Select(attrs={"class": "form-select"}),
            "favicon": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".png,.ico"}),
        }

    def clean_favicon(self):
        favicon = self.cleaned_data.get("favicon")
        if favicon and hasattr(favicon, "size"):
            max_size_mb = 1
            if favicon.size > max_size_mb * 1024 * 1024:
                raise forms.ValidationError(f"حجم فایل نباید بیشتر از {max_size_mb} مگابایت باشد.")
            valid_ext = (".png", ".ico")
            if not favicon.name.lower().endswith(valid_ext):
                raise forms.ValidationError("فرمت فایل باید PNG یا ICO باشد.")
        return favicon