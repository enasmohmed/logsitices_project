from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("", views.index, name="index"),
    # path('export_to_excel/', views.export_to_excel, name='export_to_excel'),
]
