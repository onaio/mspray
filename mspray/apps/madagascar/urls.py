from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.DistrictView.as_view(), name='index'),
    url(r'^(?P<district_name>\w+)$', views.DistrictView.as_view(),
        name='district'),
    url(r'^(?P<district_name>\w+)/(?P<slug>\w+)$',
        views.TargetAreaView.as_view(),
        name='target_area'),
]
