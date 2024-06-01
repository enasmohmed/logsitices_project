from django.urls import path

from .views import RegisterView, admin_dashboard, company_dashboard, CustomLoginView, CustomLogoutView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('company_dashboard/', company_dashboard, name='company_dashboard'),
]
