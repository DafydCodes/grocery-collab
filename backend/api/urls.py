from django.urls import path
from . import views

urlpatterns = [
    path('auth/register', views.register),
    path('auth/login', views.login),
    path('lists', views.lists),
    path('lists/<int:list_id>/items', views.add_item),
    path('lists/<int:list_id>/members', views.add_member),
    path('items/<int:item_id>/complete', views.complete_item),
    path('items/<int:item_id>', views.delete_item),
]