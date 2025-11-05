# core/urls_search.py
from django.urls import path
from .views import search
from core.views import CustomLoginView
app_name = "search"

urlpatterns = [
    path("", search, name="search"),
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
]




    

