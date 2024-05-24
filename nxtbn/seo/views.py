from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.contrib.sites.models import Site
from nxtbn.post.models import Post
from nxtbn.product.models import Product

def robots_txt(request):
    current_site = Site.objects.get_current()  # Gets the current site based on SITE_ID
    site_domain = current_site.domain
    sitemap_path = reverse("sitemap_xml")
    sitemap_url = f"https://{site_domain}{sitemap_path}"

    content = (
        "# We use nxtbn - Next Billion Native Commerce as our e-commerce platform that scales.\n"
        "User-agent: *\n"
        "Disallow: /docs/\n" 
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        "Allow: /\n"  # Allow everything else
        f"Sitemap: {sitemap_url}\n"
    )
    
    return HttpResponse(content, content_type="text/plain")



class StaticViewSitemap(Sitemap): # added for the demonstration only
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return [
            'home',
            # 'about',
            # 'contact'
        ]  # Names of views or URL names / doesn't exist yet, just for placeholder

    def location(self, item):
        return reverse(item)



class ProductSitemap(Sitemap):
    changefreq = "weekly" 
    priority = 0.7

    def items(self):
        return Product.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.last_modified


class PostSitemap(Sitemap):
    changefreq = "weekly" 
    priority = 0.7

    def items(self):
        return Post.objects.all().order_by("id")

    def lastmod(self, obj):
        return obj.last_modified



site_maps = {
    'static': StaticViewSitemap(),
    'product': ProductSitemap(),
    'post': PostSitemap(),
}