from django.urls import path
import lifesync.todo.views as views


urlpatterns = [
    path('', views.get_to_do_lists, name='to-do'),
    path('create/', views.create_to_do_list, name='create to-do'),
    path('add/<int:id>/', views.add_to_do_item, name='add to-do'),
    path('drop/<int:id>/', views.drop_to_do_list, name='drop to-do'),
    path('delete/<int:id>/', views.delete_to_do_item, name='delete to-do'),
    path('edit/<int:id>/', views.edit_to_do_list, name='edit to-do'),
    path('update/<int:id>/', views.update_to_do_item, name='update to-do'),
    path('share/<int:id>', views.share_to_do_list, name='share to-do'),
    path('<int:id>/', views.view_to_do_list, name='view to-do'),
]