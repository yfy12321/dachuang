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
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, HttpResponse
from .train_utils import train_model
from .db_utils import ensure_sequence_exists
from django.views.decorators.http import require_GET, require_POST
import threading
import time
import re
import joblib
import math
import pandas as pd
import os
from django.conf import settings

# ... (这里应该有其他所有函数，但文件被意外覆盖了)
# 请从备份恢复原文件，然后添加下面的函数

@require_GET
def train_prediction_data(request):
    """
    获取训练任务的预测数据用于可视化
    GET /api/train/prediction-data/?task_id=123
    """
    task_id = request.GET.get('task_id')
    
    if not task_id:
        return JsonResponse({
            "success": False,
            "error": "缺少必需的参数 'task_id'"
        }, status=400)
    
    try:
        task_id = int(task_id)
        forecast_task = ForecastTaskInformation.objects.get(task_id=task_id)
        
        if forecast_task.status != 'completed':
            return JsonResponse({
                "success": False,
                "error": "训练任务尚未完成"
            }, status=400)
        
        # 重新加载模型并获取预测数据
        station_id = forecast_task.station.id
        model_type = forecast_task.model_type
        test_start_time = forecast_task.test_start_time
        
        # 从数据库获取数据
        qs = Task_Data.objects.filter(station_id=station_id).order_by('timeStamp')
        df = pd.DataFrame(list(qs.values()))
        
        # 选择特征
        if station_id == 1:
            feature_columns = ['wspd', 'wdir', 'swdown', 'glw', 'td2m', 'psfc', 'rh2m']
        elif station_id == 2:
            feature_columns = ['windSpeed', 'windDirection', 'temperature', 'humidity', 'airPressure']
        else:
            return JsonResponse({
                "success": False,
                "error": "不支持的场站ID"
            }, status=400)
        
        x = df[feature_columns]
        y = df["power"]
        
        # 划分训练集和测试集
        train_mask = df['timeStamp'] < test_start_time
        test_mask = df['timeStamp'] >= test_start_time
        
        x_test = x[test_mask]
        y_test = y[test_mask]
        timestamps = df[test_mask]['timeStamp'].tolist()
        
        # 加载模型
        safe_test_start_time = test_start_time.strftime('%Y-%m-%d %H:%M').replace(" ", "_").replace(":", "-")
        model_dir = os.path.join(settings.BASE_DIR, 'saved_models')
        model_filename = f"model_station_{station_id}_{model_type}_{safe_test_start_time}_{task_id}.pkl"
        model_path = os.path.join(model_dir, model_filename)
        
        if not os.path.exists(model_path):
            return JsonResponse({
                "success": False,
                "error": "模型文件不存在"
            }, status=404)
        
        model = joblib.load(model_path)
        y_pred = model.predict(x_test)
        
        # 格式化时间戳
        formatted_timestamps = [ts.strftime('%Y-%m-%d %H:%M:%S') if hasattr(ts, 'strftime') else str(ts) for ts in timestamps]
        
        return JsonResponse({
            "success": True,
            "data": {
                "timestamps": formatted_timestamps,
                "actual": y_test.tolist(),
                "predicted": y_pred.tolist(),
                "metrics": {
                    "mae": float(forecast_task.mae) if forecast_task.mae else None,
                    "rmse": float(forecast_task.rmse) if forecast_task.rmse else None,
                    "mape": float(forecast_task.mape) if forecast_task.mape else None
                }
            }
        })
        
    except ForecastTaskInformation.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": f"未找到ID为 {task_id} 的任务"
        }, status=404)
    except Exception as e:
        import traceback
        return JsonResponse({
            "success": False,
            "error": f"获取预测数据失败: {str(e)}",
            "traceback": traceback.format_exc()
        }, status=500)
