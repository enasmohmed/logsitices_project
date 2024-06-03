from django.urls import path

from administration.views import DashboardView

app_name = "administration"

urlpatterns = [
    path('admin_dashboard/', DashboardView.as_view(), name='admin_dashboard'),
]
