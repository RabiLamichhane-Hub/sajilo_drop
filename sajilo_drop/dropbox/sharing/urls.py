from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/',views.upload, name="upload"),
    path('content/', views.content, name = "content"),
    path("redis-test/", views.redis_test, name="redis_test"),
    path("upload/", views.upload, name="upload"),
    path("upload-file/", views.upload_file, name="upload_file"),
    path("delete-file/<int:file_id>/", views.delete_file, name="delete_file"
),
]