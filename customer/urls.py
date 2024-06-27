from django.urls import path

from customer.views import CustomerDashboardView, DataEntryView
from . import views

app_name = "customer"

urlpatterns = [
    path('customer_dashboard/', CustomerDashboardView.as_view(), name='customer_dashboard'),
    path('data-entry/', DataEntryView.as_view(), name='data_entry'),
    path('export-excel/', views.export_to_excel, name='export_to_excel'),
    path('export-pdf/', views.export_to_pdf, name='export_to_pdf'),
]
