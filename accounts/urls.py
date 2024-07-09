from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.urls import path

from administration.views import DashboardView
from customer.views import CustomerDashboardView
from . import views
from .views import RegisterView, CustomLogoutView, CustomLoginView, EmployeeDashboardView, \
    redirect_to_dashboard, ChooseDashboardView, ApproveUsersView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('approve_users/', ApproveUsersView.as_view(), name='approve_users'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path('admin_dashboard/', staff_member_required(DashboardView.as_view()), name='admin_dashboard'),
    path('customer_dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('home/', redirect_to_dashboard, name='redirect_to_dashboard'),
    path('choose_dashboard/', ChooseDashboardView.as_view(), name='choose_dashboard'),

    path('employee_dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),

    path('user_profile', views.user_profile, name="user_profile"),
    path('user_cards', views.user_cards, name="user_cards"),

    # تغيير كلمة المرور
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),

    # إعادة تعيين كلمة المرور
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
