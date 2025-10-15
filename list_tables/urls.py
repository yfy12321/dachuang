from django.urls import path
from . import views
from . import views_for_csv
from .views_for_csv import WindPowerDataAPIView 
from django.views.generic import TemplateView

urlpatterns = [
    path('api/list', views.list_tables, name='list_tables'),#这里之前默认根路径，现在改成api/list了
    path('api/stations/', views.station_list, name='station_list'),
    path('api/stations/<int:pk>/', views.station_detail, name='station_detail'),
    path('api/check-structure/', views.check_table_structure, name='check_table_structure'),

    # ForecastType 路由
    path('api/forecast-types/', views.forecast_type_list, name='forecast_type_list'),
    path('api/forecast-types/<int:pk>/', views.forecast_type_detail, name='forecast_type_detail'),

    # 核心功能路由
     path('core-function/', TemplateView.as_view(template_name='core_function.html'), name='core-function'),
    
    # WeatherData1 路由
    path('api/weather-data1/', views.weather_data1_list, name='weather_data1_list'),
    
    # WeatherData2 路由  
    path('api/weather-data2/', views.weather_data2_list, name='weather_data2_list'),
    
    # ===== 预测任务接口 =====
    path('api/tasks/', views.forecast_task_list, name='task_list'),
    path('api/tasks/<int:pk>/', views.forecast_task_detail, name='task_detail'),
    
    # ===== 功率数据接口 =====
    path('api/power-data/', views.power_data_list, name='power_data_list'),
    
    # ===== 气象数据接口 =====
    path('api/weather-data1/', views.weather_data1_list, name='weather_data1_list'),

    # ===== 气象数据2接口 =====
    path('api/weather-data2/', views.weather_data2_list, name='weather_data2'),
    
    # ===== 短期功率预测接口 =====
    path('api/short-power/', views.short_power_data, name='short_power_data'),
    path('api/short-power/<int:task_id>/', views.short_power_data, name='task_power_data'),
    
    # ===== 日志接口 =====
    path('api/logs/', views.api_logs, name='api_logs'),
    
    # ===== 实用工具接口 =====
    path('api/wind-profile/<int:station_id>/', views.get_wind_profile, name='wind_profile'),
    

    #以下urls都是解析csv文件方法的
   # 数据API端点
   
   
    path('api/wind-power-data/', views.WindPowerDataAPIView.as_view(), name='wind-power-data'),
    path('api/daily-power-stats/', views.DailyPowerStatsAPIView.as_view(), name='daily-power-stats'),
    path('api/power-comparison/', views.PowerComparisonAPIView.as_view(), name='power-comparison'),
    path('power-dashboard/', views.power_dashboard, name='power-dashboard'),

    ## 选定场站页面相关URL
    path('api/select_filter_option/', views.select_filter_option, name='select_filter_option'),
    path('api/query_task_data/', views.query_task_data, name='query_task_data'),
    path('api/export_to_csv/', views.export_to_csv, name='export_to_csv'),
]



   







'''  path('api/data/', views_for_csv.WindFarmDataAPIView.as_view(), name='windfarm-data-api'),
    path('api/stats/', views_for_csv.WindFarmStatsAPIView.as_view(), name='windfarm-stats-api'),
    path('dashboard/', views_for_csv.wind_dashboard, name='wind-dashboard'),
    path('api/wind-data/', views_for_csv.WindDataAPIView.as_view(), name='wind-data-api'),'''

    