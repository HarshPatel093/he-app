from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('create/', views.create_user, name='create_user'),
    path("manage-users/", views.manage_users, name="manage_users"),
    path("delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("edit-user/<int:user_id>/", views.edit_user, name="edit_user"),
    path('dashboard/client/profile' , views.client_profile, name='client_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout')
]
