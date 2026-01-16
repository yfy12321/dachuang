from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from .models import Station, Task_Data
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ForecastTask, MeasurePowerData , ForecastTaskInformation
from django.db.models import Q
import json
from datetime import datetime
from django.shortcuts import render, HttpResponse
from .train_utils import train_model
from django.views.decorators.http import require_GET, require_POST
import threading
import time
import re
import joblib
'''
def station_list(request):
    
    获取所有场站列表 或 创建新场站
    GET /api/stations/ - 获取列表
    POST /api/stations/ - 创建新场站
    """
"""if request.method == 'GET':
        stations = Station.objects.all()
        data = [{
            "id": s.id,
            "station_name": s.station_name,
            "unit_config": s.unit_config,
            "installed_capacity": s.installed_capacity,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "area_km2": s.area_km2,
            "ultra_short_term_rule": s.ultra_short_term_rule,
            "day_ahead_rule": s.day_ahead_rule,
            "mid_long_term_rule": s.mid_long_term_rule
        } for s in stations]
        return JsonResponse(data, safe=False)  # safe=False允许返回列表

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            station = Station.objects.create(
                station_name=data.get('station_name'),
                unit_config=data.get('unit_config'),
                installed_capacity=data.get('installed_capacity'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                area_km2=data.get('area_km2'),
                ultra_short_term_rule=data.get('ultra_short_term_rule'),
                day_ahead_rule=data.get('day_ahead_rule'),
                mid_long_term_rule=data.get('mid_long_term_rule')
            )
            return JsonResponse({"id": station.id, "message": "创建成功"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

def station_detail(request, pk):
    
    获取/更新/删除单个场站
    GET /api/stations/<pk>/ - 获取详情
    PUT /api/stations/<pk>/ - 更新场站
    DELETE /api/stations/<pk>/ - 删除场站
    """
""" station = get_object_or_404(Station, pk=pk)

    if request.method == 'GET':
        data = {
            "id": station.id,
            "station_name": station.station_name,
            "unit_config": station.unit_config,
            "installed_capacity": station.installed_capacity,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "area_km2": station.area_km2,
            "ultra_short_term_rule": station.ultra_short_term_rule,
            "day_ahead_rule": station.day_ahead_rule,
            "mid_long_term_rule": station.mid_long_term_rule
        }
        return JsonResponse(data)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            for field in ['station_name', 'unit_config', 'installed_capacity', 
                         'latitude', 'longitude', 'area_km2',
                         'ultra_short_term_rule', 'day_ahead_rule', 'mid_long_term_rule']:
                if field in data:
                    setattr(station, field, data[field])
            station.save()
            return JsonResponse({"message": "更新成功"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == 'DELETE':
        station.delete()
        return JsonResponse({"message": "删除成功"}, status=204)

def station_search(request):
    
    场站搜索接口
    GET /api/stations/search/?name=<关键词>
    
name = request.GET.get('name', '')
    stations = Station.objects.filter(station_name__icontains=name)
    data = [{
        "id": s.id,
        "station_name": s.station_name,
        "latitude": s.latitude,
        "longitude": s.longitude
    } for s in stations]
    return JsonResponse(data, safe=False)"""
    

def list_tables(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
    return render(request, 'list_tables.html', {'tables': tables})

def station_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, station_name 
            FROM power_station
        """)
        stations = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    return JsonResponse(stations, safe=False)

def station_detail(request, pk):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, station_name, unit_config, installed_capacity, 
                       latitude, longitude, area_km2,
                       ultra_short_term_rule, day_ahead_rule, mid_long_term_rule
                FROM power_station 
                WHERE id = %s
            """, [pk])
            row = cursor.fetchone()
            
            if row:
                data = {
                    'id': row[0],
                    'name': row[1],
                    'unit_config': row[2],
                    'installed_capacity': row[3],
                    'latitude': row[4],
                    'longitude': row[5],
                    'area_km2': row[6],
                    'ultra_short_term_rule': row[7],
                    'day_ahead_rule': row[8],
                    'mid_long_term_rule': row[9],
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def check_table_structure(request):
    """检查power_station表的结构"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'power_station'
                ORDER BY ordinal_position
            """)
            columns = [{'name': row[0], 'type': row[1], 'nullable': row[2]} for row in cursor.fetchall()]
            
            # 获取表的前几行数据作为示例
            cursor.execute("SELECT * FROM power_station LIMIT 3")
            sample_data = []
            for row in cursor.fetchall():
                sample_data.append(list(row))
            
        return JsonResponse({
            'table_name': 'power_station',
            'columns': columns,
            'sample_data': sample_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
'''
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

#选定场站以及任务类型
@require_http_methods(["GET"])
def select_filter_option(request):
    try:
        stations = list(Station.objects.values('id', 'station_name'))
        task_types = [
            {'id': '1', 'type_name': '超短期预测'},
            {'id': '2', 'type_name': '日前预测'},
            {'id': '3', 'type_name': '中长期预测'}
        ]
        
        return JsonResponse({
            'success': True,
            'stations': stations,
            'task_types': task_types
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取选项失败: {str(e)}'
        }, status=500)

#查询特定场站及任务对应的数据
#测试代码： curl -X POST -H "Content-Type: application/json" -d '{"station_id":"2", "task_id":"1"}' http://127.0.0.1:8000/api/query_task_data/
@require_http_methods(["POST"])
@csrf_exempt
def query_task_data(request):
    try:
        data = json.loads(request.body)
        
        station_id = data.get('station_id')
        task_id = data.get('task_id')

        if task_id == '1':  # 超短期预测
            LineNum = 16
        elif task_id == '2':  # 日前预测
            LineNum = 96
        elif task_id == '3':  # 中长期预测
            LineNum = 672

        if not station_id or not task_id:
            return JsonResponse({
                'success': False,
                'message': '场站ID和任务ID为必填项'
            }, status=400)
        
        queryset = Task_Data.objects.filter(station_id=station_id)
        
        initial_task_data = list(queryset.order_by('-timeStamp')[:LineNum].values())
        
        task_data = []

        for record in initial_task_data:
            filtered_record = {k: v for k, v in record.items() if v is not None and k != 'id'}
            task_data.append(filtered_record)
        
        return JsonResponse({
            'success': True,
            'data': task_data,
            'total_count': len(task_data)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }, status=500)

# 测试：curl -X POST -H "Content-Type: application/json" -d '{"station_id":"2", "task_id":"1"}' http://127.0.0.1:8000/api/export_to_csv/ -o test.csv
#不写-o test.csv会直接在终端打印csv内容，写了会下载到当前目录

import csv
from io import StringIO

@require_http_methods(["POST"])
@csrf_exempt
def export_to_csv(request):
    """导出CSV格式"""
    # 创建StringIO对象，用于在内存中构建字符串内容
    output = StringIO()
    
    # 创建CSV写入器，指定输出目标为StringIO对象
    writer = csv.writer(output)

    data = json.loads(request.body)
        
    station_id = data.get('station_id')
    task_id = data.get('task_id')

    if task_id == '1':  # 超短期预测
        LineNum = 16
    elif task_id == '2':  # 日前预测
        LineNum = 96
    elif task_id == '3':  # 中长期预测
        LineNum = 672

    if not station_id or not task_id:
        return JsonResponse({
            'success': False,
            'message': '场站ID和任务ID为必填项'
        }, status=400)
        
    queryset = Task_Data.objects.filter(station_id=station_id)
        
    initial_task_data = list(queryset.order_by('-timeStamp')[:LineNum].values())
        
    task_data = []

    for record in initial_task_data:
        filtered_record = {k: v for k, v in record.items() if v is not None and k != 'id'}
        task_data.append(filtered_record)

    if task_data:
        headings = list(task_data[0].keys())

    writer.writerow(headings)

    for obj in task_data:
        row = obj.values()
        writer.writerow(row)

    # 创建HTTP响应对象，指定内容类型为text/csv
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    
    # 设置响应头，告诉浏览器这是附件下载，并指定文件名
    response['Content-Disposition'] = f'attachment; filename="{"Initial_Data_Export.csv"}"'
    
    # 返回HTTP响应
    return response


#以下代码使用Django的ORM框架的表达方式对直接用sql语句操作数据库的方式进行替换。
#这些方法都是为了对postgres数据库增删查改的，解析csv文件的方法见同目录下"view_for_csv.py"
# power_station 视图

def station_list(request):
    
    """获取所有场站列表 或 创建新场站
    GET /api/stations/ - 获取列表
    POST /api/stations/ - 创建新场站
    """
    if request.method == 'GET':
        stations = Station.objects.all()
        data = [{
            "id": s.id,
            "station_name": s.station_name,
            "unit_config": s.unit_config,
            "installed_capacity": s.installed_capacity,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "area_km2": s.area_km2,
            "ultra_short_term_rule": s.ultra_short_term_rule,
            "day_ahead_rule": s.day_ahead_rule,
            "mid_long_term_rule": s.mid_long_term_rule
        } for s in stations]
        return JsonResponse(data, safe=False)  # safe=False允许返回列表

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            station = Station.objects.create(
                station_name=data.get('station_name'),
                unit_config=data.get('unit_config'),
                installed_capacity=data.get('installed_capacity'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                area_km2=data.get('area_km2'),
                ultra_short_term_rule=data.get('ultra_short_term_rule'),
                day_ahead_rule=data.get('day_ahead_rule'),
                mid_long_term_rule=data.get('mid_long_term_rule')
            )
            return JsonResponse({"id": station.id, "message": "创建成功"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
          

def list_tables(request):
    """列出所有数据库表(保持原样，因为这是系统表查询)"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
    return render(request, 'list_tables.html', {'tables': tables})

def station_detail(request, pk):
    """获取单个电站详情(ORM版)"""
    try:
        station = Station.objects.get(pk=pk)
        data = {
            'id': station.id,
            'name': station.station_name,
            'unit_config': station.unit_config,
            'installed_capacity': station.installed_capacity,
            'latitude': station.latitude,
            'longitude': station.longitude,
            'area_km2': station.area_km2,
            'ultra_short_term_rule': station.ultra_short_term_rule,
            'day_ahead_rule': station.day_ahead_rule,
            'mid_long_term_rule': station.mid_long_term_rule,
        }
        return JsonResponse(data)
    except Station.DoesNotExist:
        return JsonResponse({'error': 'Station not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def check_table_structure(request):
    """检查表结构(ORM版)"""
    from django.db import connection
    
    # 获取表结构信息
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'power_station'
            ORDER BY ordinal_position
        """)
        columns = [{'name': row[0], 'type': row[1], 'nullable': row[2]} 
                 for row in cursor.fetchall()]
    
    # 获取示例数据(使用ORM)
    sample_data = Station.objects.all()[:3].values()
    
    return JsonResponse({
        'table_name': 'power_station',
        'columns': columns,
        'sample_data': list(sample_data)
    })

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ForecastType, WeatherData1, WeatherData2
import json

# ForecastType 视图
@csrf_exempt
def forecast_type_list(request):
    if request.method == 'GET':
        types = ForecastType.objects.all().values()
        return JsonResponse(list(types), safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_type = ForecastType.objects.create(
                type_name=data['type_name'],
                description=data['description'],
                forecast_horizon=data['forecast_horizon'],
                time_interval=data['time_interval'],
                api_endpoint=data['api_endpoint']
            )
            return JsonResponse({'id': new_type.type_id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def forecast_type_detail(request, pk):
    forecast_type = get_object_or_404(ForecastType, pk=pk)
    
    if request.method == 'GET':
        return JsonResponse({
            'type_id': forecast_type.type_id,
            'type_name': forecast_type.type_name,
            'description': forecast_type.description,
            'forecast_horizon': forecast_type.forecast_horizon,
            'time_interval': forecast_type.time_interval,
            'api_endpoint': forecast_type.api_endpoint
        })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            for field in ['type_name', 'description', 'forecast_horizon', 
                         'time_interval', 'api_endpoint']:
                if field in data:
                    setattr(forecast_type, field, data[field])
            forecast_type.save()
            return JsonResponse({'message': '更新成功'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        forecast_type.delete()
        return JsonResponse({'message': '删除成功'}, status=204)


# ========== ForecastTask 视图 ==========
@csrf_exempt
def forecast_task_detail(request, pk):
    """预测任务详情管理"""
    task = get_object_or_404(ForecastTask, pk=pk)
    
    if request.method == 'GET':
        return JsonResponse({
            'task_id': task.task_id,
            'station_id': task.station_id,
            'forecast_type': task.forecast_type,
            'start_time': task.start_time,
            'end_time': task.end_time,
            'status': task.status,
            'created_at': task.created_at
        })
    
    elif request.method == 'PUT':
        """更新任务状态"""
        try:
            data = json.loads(request.body)
            if 'status' in data:
                task.status = data['status']
                task.save()
            return JsonResponse({'message': '更新成功'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        task.delete()
        return JsonResponse({'message': '删除成功'}, status=204)


@csrf_exempt
def forecast_task_list(request):
    """预测任务列表接口"""
    if request.method == 'GET':
        # 支持多种查询参数
        queryset = ForecastTask.objects.all()
        
        # 筛选条件
        station_id = request.GET.get('station_id')
        if station_id:
            queryset = queryset.filter(station_id=station_id)
            
        forecast_type = request.GET.get('type')
        if forecast_type:
            queryset = queryset.filter(forecast_type=forecast_type)
            
        status = request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # 时间范围筛选
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__range=(start_date, end_date)
            )
        
        tasks = list(queryset.values())
        return JsonResponse(tasks, safe=False)
    
    elif request.method == 'POST':
        """创建新预测任务"""
        try:
            data = json.loads(request.body)
            task = ForecastTask.objects.create(
                station_id=data['station_id'],
                forecast_type=data['forecast_type'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                status=data.get('status', 'pending')
            )
            return JsonResponse({'task_id': task.task_id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
# WeatherData1 视图
@csrf_exempt
def weather_data1_list(request):
    if request.method == 'GET':
        station_id = request.GET.get('station_id')
        queryset = WeatherData1.objects.all()
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        data = list(queryset.values())
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            WeatherData1.objects.create(
                station_id=data['station_id'],
                date_time=data['date_time'],
                wspd=data.get('wspd'),
                wdir=data.get('wdir'),
                # 其他字段...
            )
            return JsonResponse({'message': '创建成功'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# WeatherData2 视图 (与WeatherData1类似)
@csrf_exempt 
def weather_data2_list(request):
    if request.method == 'GET':
        station_id = request.GET.get('station_id')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        queryset = WeatherData2.objects.all()
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        if start_time and end_time:
            queryset = queryset.filter(date_time__range=(start_time, end_time))
        
        data = list(queryset.values())
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            WeatherData2.objects.create(
                station_id=data['station_id'],
                date_time=data['date_time'],
                surface_pressure=data.get('surface_pressure'),
                # 其他字段...
            )
            return JsonResponse({'message': '创建成功'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# list_tables/views.py
@csrf_exempt
def power_data_list(request):
    """功率数据查询接口"""
    if request.method == 'GET':
        station_id = request.GET.get('station_id')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        
        queryset = MeasurePowerData.objects.all()
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        if start_time and end_time:
            queryset = queryset.filter(
                timestamp__range=(start_time, end_time))
        
        data = list(queryset.values(
            'measurement_id', 'station_id', 
            'timestamp', 'power_value'
        ))
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        """批量插入功率数据"""
        try:
            data = json.loads(request.body)
            if isinstance(data, list):  # 批量插入
                records = [
                    MeasurePowerData(
                        station_id=item['station_id'],
                        timestamp=item['timestamp'],
                        power_value=item['power_value']
                    ) for item in data
                ]
                MeasurePowerData.objects.bulk_create(records)
            else:  # 单条插入
                MeasurePowerData.objects.create(
                    station_id=data['station_id'],
                    timestamp=data['timestamp'],
                    power_value=data['power_value']
                )
            return JsonResponse({'message': '创建成功'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    



# ========== MeasureWeatherData2 气象数据接口 ==========
@csrf_exempt
def weather_data2_list(request):
    """多高度层气象数据接口"""
    if request.method == 'GET':
        # 查询参数处理
        station_id = request.GET.get('station_id')
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')
        height = request.GET.get('height')  # 可选参数：surface/70m/110m

        queryset = MeasureWeatherData2.objects.all()
        
        # 筛选条件
        if station_id:
            queryset = queryset.filter(station_id=station_id)
        if start_time and end_time:
            queryset = queryset.filter(date_time__range=(start_time, end_time))
        
        # 字段过滤
        fields = ['weather_id', 'station_id', 'date_time']
        if not height or height == 'surface':
            fields += ['surface_pressure', 'humidity_2m']
        if not height or height == '70m':
            fields += ['wind_speed_70m']
        if not height or height == '110m':
            fields += ['temperature_110m', 'wind_direction_110m']

        data = list(queryset.values(*fields))
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        """批量插入气象数据"""
        try:
            data = json.loads(request.body)
            if isinstance(data, list):
                records = [
                    MeasureWeatherData2(
                        station_id=item['station_id'],
                        date_time=item['date_time'],
                        surface_pressure=item.get('surface_pressure'),
                        humidity_2m=item.get('humidity_2m'),
                        temperature_110m=item.get('temperature_110m'),
                        wind_direction_110m=item.get('wind_direction_110m'),
                        wind_speed_70m=item.get('wind_speed_70m')
                    ) for item in data
                ]
                MeasureWeatherData2.objects.bulk_create(records)
                return JsonResponse({'message': f'成功插入{len(records)}条数据'}, status=201)
            else:
                return JsonResponse({'error': '需要数组格式数据'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# ========== ShortPowerData 功率预测接口 ==========
@csrf_exempt
def short_power_data(request):
    """短期功率预测数据接口"""
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        latest = request.GET.get('latest')  # 是否只获取最新预测
        
        queryset = ShortPowerData.objects.all()
        if task_id:
            queryset = queryset.filter(task_id=task_id)
            if latest:
                latest_time = queryset.aggregate(models.Max('timestamp'))['timestamp__max']
                queryset = queryset.filter(timestamp=latest_time)
        
        data = list(queryset.values(
            'forecast_id', 'task_id', 'timestamp', 'power_value'
        ))
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        """提交预测结果"""
        try:
            data = json.loads(request.body)
            if isinstance(data, list):
                # 批量插入
                objs = [
                    ShortPowerData(
                        task_id=item['task_id'],
                        timestamp=item['timestamp'],
                        power_value=item['power_value']
                    ) for item in data
                ]
                ShortPowerData.objects.bulk_create(objs)
                return JsonResponse({'message': '批量创建成功'}, status=201)
            else:
                # 单条创建
                obj = ShortPowerData.objects.create(
                    task_id=data['task_id'],
                    timestamp=data['timestamp'],
                    power_value=data['power_value']
                )
                return JsonResponse({'forecast_id': obj.forecast_id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# ========== ApiLog 日志接口 ==========
def api_logs(request):
    """API日志查询接口"""
    # 权限检查（示例）
    if not request.user.is_staff:
        return JsonResponse({'error': '无权访问'}, status=403)
    
    # 查询参数
    endpoint = request.GET.get('endpoint')
    status = request.GET.get('status')
    days = int(request.GET.get('days', 7))  # 默认查最近7天
    
    queryset = ApiLog.objects.filter(
        created_at__gte=datetime.now()-timedelta(days=days)
    )
    
    if endpoint:
        queryset = queryset.filter(endpoint__icontains=endpoint)
    if status:
        queryset = queryset.filter(response_status=status)
    
    logs = list(queryset.values(
        'log_id', 'endpoint', 'request_method',
        'response_status', 'response_time', 'created_at'
    ).order_by('-created_at')[:100])  # 限制返回100条
    
    return JsonResponse(logs, safe=False)

# ========== 实用工具接口 ==========
def get_wind_profile(request, station_id):
    """获取风速垂直剖面数据"""
    latest_data = MeasureWeatherData2.objects.filter(
        station_id=station_id
    ).order_by('-date_time').first()
    
    if not latest_data:
        return JsonResponse({'error': '无数据'}, status=404)
    
    profile = {
        'surface': latest_data.wind_speed_70m * 0.8 if latest_data.wind_speed_70m else None,
        '70m': latest_data.wind_speed_70m,
        '110m': latest_data.wind_speed_70m * 1.2 if latest_data.wind_speed_70m else None,
        'timestamp': latest_data.date_time
    }
    return JsonResponse(profile)


import os
import pandas as pd
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render

# 假设CSV文件路径 - 您需要根据实际情况修改这个路径
CSV_FILE_PATH = os.path.join(settings.MEDIA_ROOT, '新乐凤鸣光伏电站_results.csv')

class WindPowerDataAPIView(View):
    """风电场功率预测与实际数据API视图"""
    
    def get(self, request, *args, **kwargs):
        try:
            # 1. 读取CSV文件
            df = pd.read_csv(CSV_FILE_PATH)
            
            # 2. 转换时间格式
            df['timeStamp'] = pd.to_datetime(df['timeStamp'])
            
            # 3. 处理请求参数 - 时间范围筛选
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            
            if start_date and end_date:
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1)
                df = df[(df['timeStamp'] >= start_date) & (df['timeStamp'] <= end_date)]
            
            # 4. 返回结构化数据
            response_data = {
                'timestamps': df['timeStamp'].dt.strftime('%Y-%m-%dT%H:%M:%S').tolist(),
                'predicted_power': df['pred'].round(2).tolist(),
                'actual_power': df['power'].round(2).tolist(),
                'time_range': {
                    'start': df['timeStamp'].min().strftime('%Y-%m-%d'),
                    'end': df['timeStamp'].max().strftime('%Y-%m-%d')
                },
                'stats': {
                    'max_predicted': df['pred'].max(),
                    'max_actual': df['power'].max(),
                    'avg_predicted': df['pred'].mean(),
                    'avg_actual': df['power'].mean()
                }
            }
            
            return JsonResponse(response_data)
            
        except FileNotFoundError:
            return JsonResponse({'error': 'CSV文件未找到'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class DailyPowerStatsAPIView(View):
    """每日功率统计API"""
    
    def get(self, request, *args, **kwargs):
        try:
            df = pd.read_csv(CSV_FILE_PATH)
            df['timeStamp'] = pd.to_datetime(df['timeStamp'])
            
            # 按日期分组计算统计信息
            df['date'] = df['timeStamp'].dt.date
            daily_stats = df.groupby('date').agg({
                'pred': ['max', 'mean', 'sum'],
                'power': ['max', 'mean', 'sum']
            }).round(2)
            
            # 扁平化多级列索引
            daily_stats.columns = [
                'pred_max', 'pred_mean', 'pred_total',
                'power_max', 'power_mean', 'power_total'
            ]
            
            daily_stats = daily_stats.reset_index()
            daily_stats['date'] = daily_stats['date'].astype(str)
            
            return JsonResponse({
                'daily_stats': daily_stats.to_dict('records')
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class PowerComparisonAPIView(View):
    """预测与实际功率对比分析API"""
    
    def get(self, request, *args, **kwargs):
        try:
            df = pd.read_csv(CSV_FILE_PATH)
            df['timeStamp'] = pd.to_datetime(df['timeStamp'])
            
            # 计算预测误差
            df['error'] = df['pred'] - df['power']
            df['abs_error'] = abs(df['error'])
            df['error_percentage'] = (df['abs_error'] / df['power'].replace(0, 0.001)) * 100
            
            # 按小时分析误差
            df['hour'] = df['timeStamp'].dt.hour
            hourly_stats = df.groupby('hour').agg({
                'error': 'mean',
                'abs_error': 'mean',
                'error_percentage': 'mean'
            }).round(2).reset_index()
            
            response_data = {
                'overall_accuracy': {
                    'mae': df['abs_error'].mean(),
                    'mse': (df['error'] ** 2).mean(),
                    'mape': df['error_percentage'].mean()
                },
                'hourly_accuracy': hourly_stats.to_dict('records'),
                'recent_data': df.tail(24).to_dict('records')  # 最近24小时数据
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def power_dashboard(request):
    """功率预测可视化仪表板"""
    station_name = request.GET.get('station', '')
    station_type = request.GET.get('type', '')
    
    try:
        # 根据场站名称和类型加载相应的CSV文件
        if station_name:
            csv_file_path = os.path.join(settings.MEDIA_ROOT, f'{station_name}_results.csv')
        else:
            csv_file_path = os.path.join(settings.MEDIA_ROOT, 'XL_results.csv')
        
        df = pd.read_csv(csv_file_path)
        df['timeStamp'] = pd.to_datetime(df['timeStamp'])
        
        context = {
            'station_name': station_name,
            'station_type': station_type,
            'min_date': df['timeStamp'].min().strftime('%Y-%m-%d'),
            'max_date': df['timeStamp'].max().strftime('%Y-%m-%d'),
            'total_records': len(df),
            'date_range': f"{df['timeStamp'].min().strftime('%Y-%m-%d')} 至 {df['timeStamp'].max().strftime('%Y-%m-%d')}"
        }
    except FileNotFoundError:
        context = {
            'error': f'找不到{station_name}的数据文件',
            'station_name': station_name,
            'station_type': station_type
        }
    except Exception as e:
        context = {
            'error': str(e),
            'station_name': station_name,
            'station_type': station_type
        }
    
    # 修改模板路径为相对路径
    return render(request, 'dashboard.html', context)

# ======== 模型训练接口 ========


@csrf_exempt
@require_POST
def train_start(request):
    """
    启动模型训练
    在用户完成所有选择后，启动一次模型训练与预测任务。
    
    请求参数(JSON):
    {
      "station_id": "2",
      "task_id": "1", 
      "model_type": "lstm",
      "test_start_time": "2023-01-01 00:00"
    }
    
    返回示例:
    {
      "success": true,
      "message": "模型训练已启动",
      "task_id": 12
    }
    """
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        
        # 获取参数
        station_id = data.get('station_id')
        station_id = int(station_id)
        task_id = data.get('task_id')
        task_id = int(task_id)
        model_type = data.get('model_type')
        test_start_time = data.get('test_start_time')
        
        # 参数校验
        if not all([station_id, task_id, model_type, test_start_time]):
            return JsonResponse({
                "success": False,
                "message": "缺少必要参数: station_id, task_id, model_type, test_start_time"
            }, status=400)
        
        # 将test_start_time转换为datetime对象
        try:
            test_start_dt = datetime.strptime(test_start_time, '%Y-%m-%d %H:%M')
        except ValueError:
            return JsonResponse({
                "success": False,
                "message": "时间格式错误，应为 YYYY-MM-DD HH:MM"
            }, status=400)
        
        # 根据model_type确定forecast_type
        if task_id == 1:  # 超短期预测
            forecast_type = 'ultra_short'
        elif task_id == 2:  # 短期预测
            forecast_type = 'short'
        elif task_id == 3:  # 中期预测
            forecast_type = 'medium'
        else:
            return JsonResponse({
                "success": False,
                "message": "无效的task_id"
            }, status=400)

        # 创建预测任务记录
        # 获取对应的Station对象
        try:
            station = Station.objects.get(id=station_id)
        except Station.DoesNotExist:
            return JsonResponse({
                "success": False,
                "message": f"场站ID {station_id} 不存在"
            }, status=400)
        
        forecast_task = ForecastTaskInformation.objects.create(
            station=station,
            forecast_type=forecast_type,
            model_type=model_type,
            start_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            end_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),  # 预测任务默认结束时间为开始时间,模型训练完成后要修改
            test_start_time=test_start_dt,
            status='running'
        )
        
        # 异步执行训练

        thread = threading.Thread(
            target=train_model,
            args=(station_id, model_type, test_start_time, forecast_task.task_id)
        )
        thread.daemon = True  # 设置为守护线程
        thread.start()


        # 返回成功响应
        return JsonResponse({
                "success": True,
                "message": "模型训练已启动",
                "task_id": forecast_task.task_id
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "请求体不是有效的JSON格式"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"启动训练失败: {str(e)}"
        }, status=500)

@require_GET
def train_status(request):
    """
    查询模型训练状态（前端轮询）
    
    请求参数(Query):
    task_id: 模型训练任务ID
    
    返回示例（未完成）:
    {
      "success": true,
      "status": "running"
    }
    
    返回示例（已完成）:
    {
      "success": true,
      "status": "finished",
      "result_id": 12
    }
    """
    try:
        # 获取查询参数
        task_id = request.GET.get('task_id')
        task_id = int(task_id)
        
        # 参数校验
        if not task_id:
            return JsonResponse({
                "success": False,
                "message": "缺少必要参数"
            }, status=400)
        
        # 查找匹配的预测任务
        try:
            # 根据station_id查找最新的预测任务
            forecast_task = ForecastTaskInformation.objects.filter(task_id=task_id).first()

            
            if not forecast_task:
                # 如果没有找到任务，返回错误信息
                return JsonResponse({
                    "success": False,
                    "message": "未找到对应的训练任务"
                }, status=404)
            
            # 根据任务状态返回结果
            if forecast_task.status == 'completed':
                # 任务已完成，返回finished状态和结果ID
                return JsonResponse({
                    "success": True,
                    "status": "finished",
                    "result_id": forecast_task.task_id
                })
            elif forecast_task.status == 'failed':
                # 任务失败
                return JsonResponse({
                    "success": True,
                    "status": "failed",
                    "error_message": forecast_task.error_message
                })
            else:
                # 任务仍在运行中
                return JsonResponse({
                    "success": True,
                    "status": "running"
                })
                
        except ForecastTaskInformation.DoesNotExist:
            # 没有找到对应的任务
            return JsonResponse({
                "success": False,
                "message": "未找到对应的训练任务"
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"查询失败: {str(e)}"
        }, status=500)

@require_GET
def train_result(request):
    """
    查询指定预测结果的模型训练指标。
    通过 GET 请求的 query parameter 传入 result_id。
    例如: /api/train/result/?result_id=123
    """

    result_id = request.GET.get('result_id') 
    
    if not result_id:
        return JsonResponse({
            "success": False,
            "error": "缺少必需的参数 'result_id'"
        }, status=400)
    
    try:
        result_id = int(result_id)
        forecast_task=ForecastTaskInformation.objects.get(task_id=result_id)

        metrics_data = {
            "MAE": forecast_task.mae,
            "RMSE": forecast_task.rmse,
            "MAPE": forecast_task.mape
        }

        return JsonResponse({
            "success": True,
            "metrics": metrics_data
        })
    except ValueError:
        return JsonResponse({
            "success": False,
            "error": f"无效的结果ID: '{result_id}'"
        }, status=400)
        
    except ForecastTaskInformation.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": f"未找到ID为 {result_id} 的任务"
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": "服务器内部错误"
        }, status=500)


@csrf_exempt
@require_POST
def predict_choose(request):
    """
    预测模型
    
    请求参数(JSON):
    {
        "station_id": 123,  # 场站ID
        "model_type": "linear",  # 模型类型
        "test_start_time": "2023-01-01 00:00"  # 测试集开始时间
        "forecast_task_id": 123  # 预测任务ID
    }
    """
    try: 
        data = json.loads(request.body)
        station_id = data.get('station_id')
        model_type = data.get('model_type')
        forecast_task_id = data.get('forecast_task_id')
        test_start_time = data.get('test_start_time')
        safe_test_start_time = test_start_time.replace(" ", "_").replace(":", "-")


         # 构建模型路径
        model_dir = os.path.join(settings.BASE_DIR, 'saved_models')
        model_filename = f"model_station_{station_id}_{model_type}_{safe_test_start_time}_{forecast_task_id}.pkl"
        model_path = os.path.join(model_dir, model_filename)

        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            return JsonResponse({
                "message": "模型文件不存在"
            }, status=404)
        
        model = joblib.load(model_path)

        # 提示使用的特征
        if station_id == 1:
            features = ['wspd', 'wdir', 'swdown', 'glw', 'td2m', 'psfc', 'rh2m']
        elif station_id == 2:
            features = ['windSpeed', 'windDirection', 'temperature', 'humidity', 'airPressure']
        else:
            return JsonResponse({
                "message": "未知的场站ID"
            }, status=400)
        
        return JsonResponse({
            "message": "模型加载成功",
            "model_path": model_path,
            "features": features
        })
    except Exception as e:
        return JsonResponse({
            "message": f"预测失败: {str(e)}"
        }, status=500)
    

@csrf_exempt
def predict_use(request):
    """
    使用指定模型进行预测
    GET: 传入模型路径
    POST: 传入数据文件路径进行预测
    """
    if request.method == 'GET':
        # 通过GET参数获取模型路径
        model_path = request.GET.get('model_path')
        
        if not model_path:
            return JsonResponse({
                'success': False,
                'error': '缺少model_path参数'
            }, status=400)
        
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            return JsonResponse({
                'success': False,
                'error': '指定的模型文件不存在'
            }, status=404)
        
        # 可以返回模型的一些基本信息
        return JsonResponse({
            'success': True,
            'message': '模型已准备好,请传入数据文件路径进行预测',
            'model_path': model_path
        })
    
    elif request.method == 'POST':
        try:
            # 解析JSON数据
            data = json.loads(request.body)
            model_path = request.GET.get('model_path')  # 仍然从GET参数获取模型路径
            data_file = data.get('data_file')
            
            # 参数校验
            if not model_path:
                return JsonResponse({
                    'success': False,
                    'error': '缺少model_path参数(请通过GET参数传递)'
                }, status=400)
            
            if not data_file:
                return JsonResponse({
                    'success': False,
                    'error': '缺少data_file参数'
                }, status=400)
            
            # 检查模型文件是否存在
            if not os.path.exists(model_path):
                return JsonResponse({
                    'success': False,
                    'error': '指定的模型文件不存在'
                }, status=404)
            
            # 检查数据文件是否存在
            if not os.path.exists(data_file):
                return JsonResponse({
                    'success': False,
                    'error': '指定的数据文件不存在'
                }, status=404)
            
            # 加载模型
            model = joblib.load(model_path)
            
            # 读取数据文件
            df = pd.read_csv(data_file)
            
            # 根据场站ID选择合适的特征列
            # 这里假设可以根据文件名或路径推断场站ID
            # 或者您可以在GET/POST参数中传递场站ID
            station_id = None
            if 'station_1' in model_path or '新乐' in model_path:
                station_id = 1
            elif 'station_2' in model_path or '巨鹿' in model_path:
                station_id = 2
            
            # 选择特征
            if station_id == 1:
                # 新乐光伏特征列
                feature_columns = ['wspd', 'wdir', 'swdown', 'glw', 'td2m', 'psfc', 'rh2m']
            elif station_id == 2:
                # 巨鹿电场特征列
                feature_columns = ['windSpeed', 'windDirection', 'temperature', 'humidity', 'airPressure']

            # 从模型路径中提取任务ID
            task_id_match = re.search(r'_(\d+)\.pkl$', model_path)
            forecast_task_id = None
            if task_id_match:
                forecast_task_id = int(task_id_match.group(1))

            
            # 确保特征列存在于数据中
            missing_columns = [col for col in feature_columns if col not in df.columns]
            if missing_columns:
                return JsonResponse({
                    'success': False,
                    'error': f'数据文件缺少以下特征列: {missing_columns}'
                }, status=400)
            
            # 提取特征数据
            x = df[feature_columns]
            
            # 进行预测
            predictions = model.predict(x)
            
            # 将预测结果添加到DataFrame
            df['predicted_power'] = predictions
            
            # 生成结果文件路径
            result_file = data_file.replace('.csv', f'_task_{forecast_task_id}_predictions.csv')
            df.to_csv(result_file, index=False)
            
            # 返回结果
            return JsonResponse({
                'success': True,
                'message': '预测完成',
                'result_file': result_file,
                'predictions': predictions.tolist(),
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': '请求体不是有效的JSON格式'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'预测过程中发生错误: {str(e)}'
            }, status=500)
    
    else:
        return JsonResponse({
            'success': False,
            'error': '只支持GET和POST方法'
        }, status=405)

