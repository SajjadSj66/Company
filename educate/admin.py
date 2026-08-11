from django.contrib import admin
from .models import *


class CourseFeatureInline(admin.TabularInline):
    model = CourseFeature
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'teacher', 'practical_percentage',
                    'price', 'discount_percent', 'is_popular', 'is_active')
    list_filter = ('category', 'is_popular', 'is_active', 'teacher')
    search_fields = ('title', 'short_description', 'teacher')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseFeatureInline]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'category', 'short_description', 'description')
        }),
        ('درصد عملی و مدرس و تصویر', {
            'fields': ('practical_percentage', 'teacher', 'image')
        }),
        ('قیمت و تخفیف و وضعیت', {
            'fields': ('price', 'discount_percent', 'is_popular', 'is_active')
        })
    )


@admin.register(CourseFeature)
class CourseFeatureAdmin(admin.ModelAdmin):
    list_display = ('course', 'title')
    list_filter = ('course',)

@admin.register(SeoSignUp)
class SeoSignUpAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'educate']
    search_fields = ['full_name', 'phone']


@admin.register(AiSignUp)
class AiSignUpAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'educate']
    search_fields = ['full_name', 'phone']


@admin.register(WordpressSignUp)
class WordpressSignUpAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'educate']
    search_fields = ['full_name', 'phone']


@admin.register(UiSignUp)
class UiSignUpAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'educate']
    search_fields = ['full_name', 'phone']


@admin.register(BackSignUp)
class BackSignUpAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'educate']
    search_fields = ['full_name', 'phone']


@admin.register(FrontSignUp)
class FrontSignUpAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'educate']
    search_fields = ['full_name', 'phone']