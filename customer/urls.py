from django.urls import path

from customer.views import CustomerDashboardView, CustomerEditDataView, AddCustomerDataView
from . import views

app_name = "customer"

urlpatterns = [
    path('customer_dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('data-entry/', CustomerEditDataView.as_view(), name='data_entry'),
    path('add-customer-data/', AddCustomerDataView.as_view(), name='add_customer_data'),
    path('export-excel/', views.export_to_excel, name='export_to_excel'),
    path('export-pdf/', views.export_to_pdf, name='export_to_pdf'),
]
