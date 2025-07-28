from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_tables, name='list_tables'),
    path('api/stations/', views.station_list, name='station_list'),
    path('api/stations/<int:pk>/', views.station_detail, name='station_detail'),
    path('api/check-structure/', views.check_table_structure, name='check_table_structure'),
]