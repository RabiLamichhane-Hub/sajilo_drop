from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/',views.upload, name="upload"),
    path('content/', views.content, name = "content"),
    path("redis-test/", views.redis_test, name="redis_test"),
    path("jsonldcreate/", views.create_jsonld, name="create_jsonld"),
    path("jsonldsuccess/", views.jsonld_success, name="jsonld_success"),
]