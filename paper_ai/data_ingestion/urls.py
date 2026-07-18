from django.urls import path
from .views import CSVUploadView

app_name = 'data_ingestion'

urlpatterns = [
    path('upload/', CSVUploadView.as_view(), name='upload'),
]
