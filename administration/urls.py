from django.urls import path

from administration.views import DashboardView

app_name = "administration"

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
]
