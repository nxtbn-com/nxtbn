from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from nxtbn.seo import views as seo_views


urlpatterns = [
    path("robots.txt", seo_views.robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": seo_views.site_maps}, name="sitemap_xml"),
]