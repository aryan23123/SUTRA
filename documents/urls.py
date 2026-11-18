from django.urls import path

from . import views

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('records/<int:record_id>/upload/', views.upload_document, name='document_upload'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
    path('<int:pk>/delete/', views.document_delete, name='document_delete'),
]
