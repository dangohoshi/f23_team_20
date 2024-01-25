"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from lifesync import views
from django.contrib.auth.views import LogoutView

import lifesync.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', lifesync.views.homepage, name='homepage'),

    path('to-do/', include('lifesync.todo.urls'), name='to-do'),
    path('notes/', include('lifesync.notes.urls'), name='notes'),
    path('expense/', include('lifesync.expense.urls'), name='expense'),
    path('reminders/', include('lifesync.paymentreminders.urls'), name='reminders'),
    path('calender/', include('lifesync.calender.urls'), name='calender'),
    path('customize/', views.customize, name='customize'),
    path('select-colors/', views.select_colors, name='select-colors'),

    path('', views.login_action, name='login_route'),
    path('login', views.login_action, name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    path('about/', lifesync.views.about, name='about'),

]
