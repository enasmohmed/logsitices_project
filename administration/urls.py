from django.urls import path

from administration.views import DashboardView, AdminEditDataView, AddAdminDataView, download_excel_view, \
    download_pdf_view

app_name = "administration"

urlpatterns = [
    path('admin_dashboard/', DashboardView.as_view(), name='admin_dashboard'),
    path('data-entry/', AdminEditDataView.as_view(), name='data_entry'),
    path('add-admin-data/', AddAdminDataView.as_view(), name='add_admin_data'),
    path('admin/edit/', AdminEditDataView.as_view(), name='admin_edit'),
    path('admin/edit/download/excel/', download_excel_view, name='download_excel'),
    path('admin/edit/download/pdf/', download_pdf_view, name='download_pdf'),
]
