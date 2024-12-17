from django.urls import path

from skin_c_detection import views

urlpatterns = [
    path('', views.index, name='index'),
]
