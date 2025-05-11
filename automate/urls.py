from django.contrib import admin
from django.urls import path, include
from automate_app import views

urlpatterns = [
    path("", views.single, name="single"),

    path("multiple/", views.multiple, name="multiple"),
    
    path('admin/', admin.site.urls),
]