from django.urls import path

from administration.views import DashboardView
from customer.views import CustomerDashboardView
from . import views
from .views import RegisterView, CustomLoginView, CustomLogoutView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('admin_dashboard/', DashboardView.as_view(), name='index'),
    path('customer_dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    # path('company_dashboard/', company_dashboard, name='company_dashboard'),

    path('user_profile', views.user_profile, name="user_profile"),
    path('edit_profile', views.edit_profile, name="edit_profile"),
    path('user_cards', views.user_cards, name="user_cards"),

]
