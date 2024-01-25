from django.urls import path
import lifesync.calender.views as views

urlpatterns = [
    path('', views.get_calander_home, name='calender'),
]