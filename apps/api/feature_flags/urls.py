from django.urls import path
from . import views

urlpatterns = [
    path('flags/', views.get_feature_flags, name='feature-flags'),
]
