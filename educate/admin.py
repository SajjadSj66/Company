from django.contrib import admin
from .models import Course, CourseFeature

class CourseFeatureInline(admin.TabularInline):
    model = CourseFeature
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'practical_percentage', 'price', 'is_popular', 'is_active')
    list_filter = ('category', 'is_popular', 'is_active')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseFeatureInline]
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'category', 'short_description', 'description')
        }),
        ('درصد عملی و تصویر', {
            'fields': ('practical_percentage', 'image')
        }),
        ('قیمت و وضعیت', {
            'fields': ('price', 'is_popular', 'is_active')
        })
    )

@admin.register(CourseFeature)
class CourseFeatureAdmin(admin.ModelAdmin):
    list_display = ('course', 'title')
    list_filter = ('course',)