from django.urls import path
import lifesync.paymentreminders.views as views

urlpatterns = [
    path('', views.get_reminders_home, name='reminders'),
    path('add-reminder-page', views.add_reminders_page, name='add-reminder-page'),
    path('add-reminder', views.add_reminder, name='add-reminder'),
    path('paid', views.update_reminder, name='paid'),
]
