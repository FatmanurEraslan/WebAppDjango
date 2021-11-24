from django.urls import path
from pages.views import index

app_name = 'pages'
urlpatterns = [
    path('', index, name='index'),
]
