from django.urls import path
import lifesync.expense.views as views

urlpatterns = [
    path('', views.get_expense_home, name='expense'),
    path('add-expense', views.add_expense, name='add-expense'),
    path('report', views.generate_report, name='report'),
    path('view-expense', views.get_expense_table, name='view-expense'),
    path('delete-expense', views.delete_expense, name='delete-expense'),
]