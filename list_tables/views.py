from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from .models import Station

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