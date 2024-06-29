from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path

from administration.views import DashboardView
from customer.views import CustomerDashboardView
from . import views
from .views import RegisterView, approve_users_view, CustomLogoutView, CustomLoginView, EmployeeDashboardView, \
    redirect_to_dashboard, ChooseDashboardView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('approve_users/', approve_users_view, name='approve_users'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # path('admin_dashboard/', DashboardView.as_view(), name='admin_dashboard'),
    path('admin_dashboard/', staff_member_required(DashboardView.as_view()), name='admin_dashboard'),
    path('customer_dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('home/', redirect_to_dashboard, name='redirect_to_dashboard'),
    path('choose_dashboard/', ChooseDashboardView.as_view(), name='choose_dashboard'),

    path('employee_dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    # path('add_admin_data/', AddAdminDataView.as_view(), name='add_admin_data'),
    # path('add_admin_data', views.data_entry_view, name="add_admin_data"),

    path('user_profile', views.user_profile, name="user_profile"),
    path('user_cards', views.user_cards, name="user_cards"),

]
