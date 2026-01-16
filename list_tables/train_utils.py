import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from .models import Task_Data, ForecastTaskInformation
import os
from django.conf import settings
from django.utils import timezone
import joblib
import time
from datetime import datetime



def train_model(station_id, model_type, test_start_time, forecast_task_id):

    #获取预测任务对应数据
    forecast_task = ForecastTaskInformation.objects.get(task_id=forecast_task_id)


    #从数据库获取数据
    qs = Task_Data.objects.filter(station_id=station_id).order_by('timeStamp')

    if not qs.exists():
        forecast_task.status = 'failed'
        forecast_task.error_message = f"场站 {station_id} 暂无数据"
        forecast_task.save()
        return {"error": f"场站 {station_id} 暂无数据"}
    
    #转换为dataframe
    df = pd.DataFrame(list(qs.values()))

    #选择特征
    if station_id == 1:  
        # 新乐光伏
        feature_columns = ['wspd', 'wdir', 'swdown', 'glw', 'td2m', 'psfc', 'rh2m']
        x = df[feature_columns]

    elif station_id == 2:
        #巨鹿电场
        feature_columns = ['windSpeed', 'windDirection', 'temperature', 'humidity', 'airPressure']
        x = df[feature_columns]

    else:
        forecast_task.status = 'failed'
        forecast_task.error_message = "不支持的场站ID"
        forecast_task.save()

        return {"error": "不支持的场站ID"}
    
    
    #目标变量
    y=df["power"]

    #划分训练集和数据集
    try:
        train_mask = df['timeStamp'] < test_start_time
        test_mask = df['timeStamp'] >= test_start_time
        
        x_train = x[train_mask]
        x_test = x[test_mask]
        y_train = y[train_mask]
        y_test = y[test_mask]
        
        # 检查分割后的数据集是否为空
        if len(x_train) == 0:
            forecast_task.status = 'failed'
            forecast_task.error_message = "根据指定的时间点分割后，训练集为空"
            forecast_task.save()
            return {"error": "根据指定的时间点分割后，训练集为空"}
            
        if len(x_test) == 0:
            forecast_task.status = 'failed'
            forecast_task.error_message = "根据指定的时间点分割后，测试集为空"
            forecast_task.save()
            return {"error": "根据指定的时间点分割后，测试集为空"}
            
    except Exception as e:
        forecast_task.status = 'failed'
        forecast_task.error_message = f"处理测试集起点时间时出错: {str(e)}"
        forecast_task.save()
        return {"error": f"处理测试集起点时间时出错: {str(e)}"}


    # 训练模型
    if model_type == 'linear':
        model = LinearRegression()
    elif model_type == 'random_forest':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    else:
        forecast_task.status = 'failed'
        forecast_task.error_message = "不支持的模型类型"
        forecast_task.save()
        return {"error": "不支持的模型类型"}
    
    model.fit(x_train, y_train)

    #模型预测和评价
    y_pred = model.predict(x_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    # 计算MAPE（避免分母为0）
    mask = y_test != 0
    if mask.any():
        mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
        # 处理Infinity和NaN
        if np.isinf(mape) or np.isnan(mape):
            mape = None
    else:
        mape = None
    #将结果保存入数据库
    forecast_task.end_time = timezone.now()
    forecast_task.status = 'completed'
    forecast_task.mae = mae
    forecast_task.rmse = rmse
    forecast_task.mape = mape
    forecast_task.save()

    # 保存训练好的模型
    model_dir = os.path.join(settings.BASE_DIR, 'saved_models')
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    safe_test_start_time = test_start_time.replace(" ", "_").replace(":", "-")
    model_filename = f"model_station_{station_id}_{model_type}_{safe_test_start_time}_{forecast_task_id}.pkl"
    model_path = os.path.join(model_dir, model_filename)
    try:
        joblib.dump(model, model_path)
    except Exception as e:
        forecast_task.status = 'failed'
        forecast_task.error_message = f"保存模型时出错: {str(e)}"
        forecast_task.save()
        return {"error": f"保存模型时出错: {str(e)}"}

    return {"message": "模型训练完成"}


