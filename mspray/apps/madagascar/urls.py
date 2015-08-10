from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<slug>\w+)$', views.DistrictView.as_view(),
        name='district')
]
