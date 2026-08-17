from django.contrib.sitemaps import Sitemap
from users.models import Article  # یا هر مدلی که صفحات عمومی داره

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at