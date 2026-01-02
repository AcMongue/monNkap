from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('statistics/', views.statistics_view, name='statistics'),
]
