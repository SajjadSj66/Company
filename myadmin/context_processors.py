from .models import *



def reading_settings(request):
    settings_obj = ReadingSettings.load()
    return {
        "SEO_INDEXABLE": settings_obj.allow_search_indexing,
    }

def seo_context(request):
    seo = SEOSettings.load()
    return {
        "SEO_INDEXABLE": seo.allow_search_indexing,
        "SEO_TITLE": seo.homepage_title_template,
        "SEO_DESCRIPTION": seo.homepage_meta_description,
        "SEO_OG_IMAGE": seo.og_image.url if seo.og_image else None,
    }