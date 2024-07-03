from django.urls import path

from customer.views import CustomerDashboardView, CustomerEditDataView, AddCustomerDataView

app_name = "customer"

urlpatterns = [
    path('customer_dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('data-entry/', CustomerEditDataView.as_view(), name='data_entry'),
    path('add-customer-data/', AddCustomerDataView.as_view(), name='add_customer_data'),
]
