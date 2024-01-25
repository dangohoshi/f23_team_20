from django.urls import path
import lifesync.notes.views as views


urlpatterns = [
    path('', views.get_categories, name='notes'),
    path('add/', views.add_category, name='add category'),
    path('email/', views.email, name='email'),
    path('category/<int:id>/', views.view_category, name='view category'),
    path('view/<int:id>/', views.view_note, name='view note'),
    path('share/<int:id>', views.share, name='share note'),
    path('category/<int:id>/create/', views.create_note, name='create note'),
    path('view/<int:id>/edit/', views.edit_note, name='edit note'),
]