from django.urls import path

from arogya_ai.views import views, auth

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('login/', auth.login, name='login'),
    path('register/', auth.register, name='register'),
    path('logout/', auth.logout, name='logout'),

    path('setup/', views.setup, name='setup'),

    path('telemedicine/', views.telemedicine, name='telemedicine'),
    path('booking/', views.booking, name='booking'),
    path('reminder/', views.reminder, name='reminder'),
    path('search/', views.search, name='search'),
    path('ocr/', views.ocr, name='ocr'),
    path('detection/', views.detection, name='detection'),
    path('advice/', views.advice, name='advice'),
    path('payment/', views.payment, name='payment'),


]
