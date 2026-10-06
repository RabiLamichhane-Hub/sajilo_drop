from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name="upload"),
    path('content/', views.content, name="content"),
    path('files/', views.get_files, name="get_files"),
    path("upload-file/", views.upload_file, name="upload_file"),
    path("delete-file/<int:file_id>/", views.delete_file, name="delete_file"),
]