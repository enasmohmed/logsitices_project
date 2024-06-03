from django.urls import path

from customer.views import CustomerDashboardView

app_name = "customer"

urlpatterns = [
    path('customer_dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
]
