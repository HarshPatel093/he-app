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
    path("dashboard/admin/manage-users/", views.manage_users, name="manage_users"),
    path("delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("edit-user/<int:user_id>/", views.edit_user, name="edit_user"),
    path('dashboard/client/profile' , views.client_profile, name='client_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/client/feedback', views.client_feedback, name = 'client_feedback'),
    path("dashboard/admin/clients-list/", views.clients_list, name="clients_list"),
    path("client/<int:client_id>/", views.client_detail, name="client_detail"),
    path('dashboard/admin/profile/', views.admin_profile, name='admin_profile'),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html", email_template_name="registration/password_reset_email.txt", html_email_template_name="registration/password_reset_email.html", subject_template_name="registration/password_reset_subject.txt"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),

    path("client/<int:client_id>/edit-goals/", views.edit_goals, name="edit_goals"),
    path("dashboard/staff/profile", views.staff_profile, name="staff_profile"),

    path("dashboard/admin/staff/", views.shift_list, name="shift_list"),
    path('dashboard/admin/staff/allocate-shift/', views.allocate_shift, name='allocate_shift'),path("shift/<int:shift_id>/edit/", views.edit_shift, name="edit_shift"),
    path("shift/<int:shift_id>/delete/", views.delete_shift, name="delete_shift"),
    path("shifts/all/", views.all_shifts, name="all_shifts"),

]