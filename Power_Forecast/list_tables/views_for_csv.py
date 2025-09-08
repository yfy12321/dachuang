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
    
    return render(request, 'power_visualization/dashboard.html', context)