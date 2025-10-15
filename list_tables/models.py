from django.db import models
from django.core.validators import MinValueValidator 
from django.core.validators import MinValueValidator, MaxValueValidator  # 添加这行
# Create your models here.


class Task_Data(models.Model):
    station_id = models.IntegerField()#id = 1 新乐光伏，id=2 巨鹿电场
    timeStamp = models.DateTimeField()
    power = models.FloatField(null=True, blank=True)
    #以上为两电场共有参数，以下为巨鹿场站特有参数
    windSpeed = models.FloatField(null=True, blank=True)
    windDirection = models.FloatField(null=True, blank=True)
    airPressure = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    windDirection_sin = models.FloatField(null=True, blank=True)
    windDirection_cos = models.FloatField(null=True, blank=True)
    windSpeed_pre_1 = models.FloatField(null=True, blank=True)
    windSpeed_pre_2 = models.FloatField(null=True, blank=True)
    windSpeed_post_1 = models.FloatField(null=True, blank=True)
    windSpeed_post_2 = models.FloatField(null=True, blank=True)
    fValue = models.FloatField(null=True, blank=True)
    windSpeed_center = models.FloatField(null=True, blank=True)
    windSpeed_spread = models.FloatField(null=True, blank=True)
    windSpeed_height = models.FloatField(null=True, blank=True)
    windSpeed_max_change = models.FloatField(null=True, blank=True)
    windSpeed_avg_change = models.FloatField(null=True, blank=True)
    windSpeed_rising_strength = models.FloatField(null=True, blank=True)
    windSpeed_falling_strength = models.FloatField(null=True, blank=True)
    windSpeed_volatility = models.FloatField(null=True, blank=True)
    month_sin = models.FloatField(null=True, blank=True)
    month_cos = models.FloatField(null=True, blank=True)
    two_days_ago_avg_power = models.FloatField(null=True, blank=True)
    two_days_ago_max_power = models.FloatField(null=True, blank=True)
    two_days_ago_min_power = models.FloatField(null=True, blank=True)
    one_day_ago_morning_avg = models.FloatField(null=True, blank=True)
    one_day_ago_morning_max = models.FloatField(null=True, blank=True)
    one_day_ago_morning_min = models.FloatField(null=True, blank=True)
    two_days_ago_power = models.FloatField(null=True, blank=True)
    hour = models.FloatField(null=True, blank=True)
    #以上为巨鹿场站特有参数，以下为新乐场站特有参数
    wspd = models.FloatField(null=True, blank=True)
    wdir = models.FloatField(null=True, blank=True)
    swdown = models.FloatField(null=True, blank=True)
    glw = models.FloatField(null=True, blank=True)
    swddni = models.FloatField(null=True, blank=True)
    swddir = models.FloatField(null=True, blank=True)
    swddif = models.FloatField(null=True, blank=True)
    td2m = models.FloatField(null=True, blank=True)
    tsd = models.FloatField(null=True, blank=True)
    dpt2m = models.FloatField(null=True, blank=True)
    psfc = models.FloatField(null=True, blank=True)
    rh2m = models.FloatField(null=True, blank=True)
    qv2m = models.FloatField(null=True, blank=True)
    clflo = models.FloatField(null=True, blank=True)
    clfhi = models.FloatField(null=True, blank=True)


class Station(models.Model):
    station_name = models.CharField(max_length=100, verbose_name='场站名称')
    unit_config = models.CharField(max_length=100, verbose_name='机组配置', null=True, blank=True)
    installed_capacity = models.CharField(max_length=100, verbose_name='装机容量', null=True, blank=True)
    latitude = models.FloatField(verbose_name='纬度', null=True, blank=True)
    longitude = models.FloatField(verbose_name='经度', null=True, blank=True)
    area_km2 = models.FloatField(verbose_name='面积(平方公里)', null=True, blank=True)
    ultra_short_term_rule = models.CharField(max_length=200, verbose_name='超短期规则', null=True, blank=True)
    day_ahead_rule = models.CharField(max_length=200, verbose_name='日前规则', null=True, blank=True)
    mid_long_term_rule = models.CharField(max_length=200, verbose_name='中长期规则', null=True, blank=True)
    csv_path = models.CharField(max_length=200, verbose_name='csv文件路径', null=True, blank=True)
    class Meta:
        db_table = 'power_station'  # 指定实际的表名
        managed = True  

    def __str__(self):
        return self.station_name

'''
class Station(models.Model):
    """风电/光伏场站基础信息模型"""
    # 基础信息字段
    station_name = models.CharField(
        max_length=100,
        verbose_name="场站名称",
        help_text="例如：新乐凤鸣光伏场站"
    )
    capacity = models.CharField(
        max_length=50,
        verbose_name="装机容量",
        help_text="例如：0.196MW*273"
    )
    total_power = models.CharField(
        max_length=50,
        verbose_name="总功率",
        help_text="例如：60.04MW"
    )
    
    # 地理坐标字段
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="纬度",
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name="经度",
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    
    # 技术指标字段
    efficiency = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="效率系数"
    )
    
    # 预测配置字段
    short_term_prediction = models.TextField(
        verbose_name="短期预测说明",
        help_text="例如：每15min执行一次，产生未来4小时（16时点）预测结果"
    )
    daily_prediction = models.TextField(
        verbose_name="日预测说明",
        help_text="例如：当日9点前执行，产生次日0时-次日24时（96时点）预测结果"
    )
    weekly_prediction = models.TextField(
        verbose_name="周预测说明",
        help_text="例如：当日9点前执行，产生次日0时-未来168小时（共7天，672个时点）预测结果"
    )
    
    # 文件路径字段（核心新增字段）
    csv_file = models.FileField(
        upload_to='power_station_csv/',
        verbose_name="CSV数据文件",
        help_text="请上传场站历史数据CSV文件",
        null=True,
        blank=True
    )
    
    # 元数据字段
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        verbose_name = "发电场站"
        verbose_name_plural = "发电场站管理"
        ordering = ['-created_at']
        db_table = 'power_station'  # 显式指定表名

    def __str__(self):
        return f"{self.name} ({self.total_power})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('power_station:detail', args=[str(self.id)])

    @property
    def csv_file_url(self):
        """获取CSV文件的完整URL"""
        if self.csv_file and hasattr(self.csv_file, 'url'):
            return self.csv_file.url
        return None
    
from django.db import models
'''

class WindFarmData(models.Model):
    date_time = models.DateTimeField()
    farm_id = models.CharField(max_length=50)
    radiation = models.FloatField(null=True, blank=True)
    surface_pressure = models.FloatField(null=True, blank=True)
    humidity2 = models.FloatField(null=True, blank=True)
    temperature2 = models.FloatField(null=True, blank=True)
    temperature10 = models.FloatField(null=True, blank=True)
    temperature30 = models.FloatField(null=True, blank=True)
    temperature50 = models.FloatField(null=True, blank=True)
    temperature70 = models.FloatField(null=True, blank=True)
    temperature80 = models.FloatField(null=True, blank=True)
    temperature90 = models.FloatField(null=True, blank=True)
    temperature110 = models.FloatField(null=True, blank=True)
    direction10 = models.FloatField(null=True, blank=True)
    direction30 = models.FloatField(null=True, blank=True)
    direction50 = models.FloatField(null=True, blank=True)
    direction70 = models.FloatField(null=True, blank=True)
    direction80 = models.FloatField(null=True, blank=True)
    direction90 = models.FloatField(null=True, blank=True)
    direction110 = models.FloatField(null=True, blank=True)
    speed10 = models.FloatField(null=True, blank=True)
    speed30 = models.FloatField(null=True, blank=True)
    speed50 = models.FloatField(null=True, blank=True)
    speed70 = models.FloatField(null=True, blank=True)
    speed80 = models.FloatField(null=True, blank=True)
    speed90 = models.FloatField(null=True, blank=True)
    speed110 = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Wind Farm Data"
        verbose_name_plural = "Wind Farm Data"
        ordering = ['-date_time']
        indexes = [
            models.Index(fields=['farm_id']),
            models.Index(fields=['date_time']),
        ]

    def __str__(self):
        return f"{self.farm_id} - {self.date_time}"
    
#以下是之前的东西

class ForecastType(models.Model):
    """预测任务类型表"""
    type_id = models.AutoField(primary_key=True, verbose_name='类型ID')
    type_name = models.CharField(max_length=50, verbose_name='类型名称')
    description = models.CharField(max_length=200, verbose_name='类型描述')
    forecast_horizon = models.IntegerField(
        verbose_name='预测时点数',
        validators=[MinValueValidator(1)]
    )
    time_interval = models.IntegerField(
        verbose_name='时间间隔(分钟)',
        validators=[MinValueValidator(1)]
    )
    api_endpoint = models.CharField(max_length=200, verbose_name='API端点')

    class Meta:
        db_table = 'forecast_type'
        verbose_name = '预测类型'
        verbose_name_plural = '预测类型'

    def __str__(self):
        return self.type_name



class WeatherData1(models.Model):
    """气象数据表1"""
    weather_id = models.AutoField(primary_key=True, verbose_name='气象ID')
    station = models.ForeignKey(
        'Station',
        on_delete=models.CASCADE,
        db_column='station_id',
        verbose_name='关联场站'
    )
    date_time = models.DateTimeField(verbose_name='时间戳')
    
    # 气象要素字段
    wspd = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='风速(m/s)'
    )
    wdir = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='风向(度)'
    )
    swdown = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地表向下短波辐射(W/m²)'
    )
    glw = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地表向上长波辐射(W/m²)'
    )
    swddni = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='直接法向短波辐射(W/m²)'
    )
    swddir = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='直接短波辐射(W/m²)'
    )
    swddif = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='散射短波辐射(W/m²)'
    )
    td2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米露点温度(°C)'
    )
    tsd = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地面温度(°C)'
    )
    dpt2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米露点温度(°C)'
    )
    psfc = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地表气压(Pa)'
    )
    rh2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米相对湿度(%)'
    )
    qv2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米水汽混合比(kg/kg)'
    )
    clflo = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='低层云量(0-1)'
    )
    clfhi = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='高层云量(0-1)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'weatherdata1'
        verbose_name = '气象数据1'
        verbose_name_plural = '气象数据1'
        unique_together = (('station', 'date_time'),)

    def __str__(self):
        return f"{self.station.station_name} - {self.date_time}"


class WeatherData2(models.Model):
    """气象数据表2"""
    weather_id = models.AutoField(primary_key=True, verbose_name='气象ID')
    station = models.ForeignKey(
        'Station',
        on_delete=models.CASCADE,
        db_column='station_id',
        verbose_name='关联场站'
    )
    date_time = models.DateTimeField(verbose_name='观测时间戳')
    
    # 地面层数据
    surface_pressure = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='地表气压(hPa)'
    )
    humidity_2m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='2米湿度(%)'
    )
    
    # 不同高度层数据
    temperature_110m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='110米温度(°C)'
    )
    wind_direction_110m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='110米风向(度)'
    )
    wind_speed_70m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='70米风速(m/s)'
    )

    class Meta:
        db_table = 'weatherdata2'
        verbose_name = '气象数据2'
        verbose_name_plural = '气象数据2'
        unique_together = (('station', 'date_time'),)

    def __str__(self):
        return f"{self.station.station_name} - {self.date_time}"
    

class ForecastTask(models.Model):
    """预测任务表"""
    FORECAST_TYPES = [
        ('ultra_short', '超短期'),
        ('short', '短期'), 
        ('medium', '中期')
    ]
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败')
    ]

    task_id = models.AutoField(primary_key=True, verbose_name='任务ID')
    station = models.ForeignKey(
        'Station',
        on_delete=models.CASCADE,
        db_column='station_id',
        verbose_name='关联场站'
    )
    forecast_type = models.CharField(
        max_length=20,
        choices=FORECAST_TYPES,
        verbose_name='预测类型'
    )
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='任务状态'
    )

    class Meta:
        db_table = 'forecast_tasks'
        verbose_name = '预测任务'
        verbose_name_plural = '预测任务'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.station.station_name}-{self.get_forecast_type_display()}"


class MeasurePowerData(models.Model):
    """实测功率数据表"""
    measurement_id = models.AutoField(primary_key=True, verbose_name='测量ID')
    station = models.ForeignKey(
        'Station',
        on_delete=models.CASCADE,
        db_column='station_id',
        verbose_name='关联场站'
    )
    timestamp = models.DateTimeField(verbose_name='时间戳')
    power_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='功率值(kW)'
    )

    class Meta:
        db_table = 'measurePowerData'
        verbose_name = '实测功率数据'
        verbose_name_plural = '实测功率数据'
        unique_together = (('station', 'timestamp'),)
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.station.station_name}-{self.timestamp}"


class MeasureWeatherData1(models.Model):
    """实测气象数据表1"""
    weather_id = models.AutoField(primary_key=True, verbose_name='气象ID')
    station = models.ForeignKey(
        'Station',
        on_delete=models.CASCADE,
        db_column='station_id',
        verbose_name='关联场站'
    )
    date_time = models.DateTimeField(verbose_name='时间戳')
    
    # 气象要素字段
    wspd = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='风速(m/s)'
    )
    wdir = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='风向(度)'
    )
    swdown = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地表向下短波辐射(W/m²)'
    )
    glw = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地表向上长波辐射(W/m²)'
    )
    swddni = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='直接法向短波辐射(W/m²)'
    )
    swddir = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='直接短波辐射(W/m²)'
    )
    swddif = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='散射短波辐射(W/m²)'
    )
    td2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米露点温度(°C)'
    )
    tsd = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地面温度(°C)'
    )
    dpt2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米露点温度(°C)'
    )
    psfc = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='地表气压(Pa)'
    )
    rh2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米相对湿度(%)'
    )
    qv2m = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='2米水汽混合比(kg/kg)'
    )
    clflo = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='低层云量(0-1)'
    )
    clfhi = models.DecimalField(
        max_digits=10, decimal_places=3,
        null=True, blank=True, verbose_name='高层云量(0-1)'
    )

    class Meta:
        db_table = 'measureWeatherData1'
        verbose_name = '实测气象数据1'
        verbose_name_plural = '实测气象数据1'
        unique_together = (('station', 'date_time'),)
        ordering = ['date_time']

    def __str__(self):
        return f"{self.station.station_name}-{self.date_time}"

from django.core.validators import MinValueValidator, MaxValueValidator

class MeasureWeatherData2(models.Model):
    """实测气象数据表2（多高度层数据）"""
    weather_id = models.AutoField(primary_key=True, verbose_name='气象记录ID')
    station = models.ForeignKey(
        'Station',
        on_delete=models.CASCADE,
        db_column='station_id',
        verbose_name='关联场站'
    )
    date_time = models.DateTimeField(verbose_name='观测时间戳')

    # 地面层数据
    surface_pressure = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name='地表气压(hPa)',
        validators=[MinValueValidator(800), MaxValueValidator(1100)]
    )
    humidity_2m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name='2米湿度(%)',
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # 不同高度层数据
    temperature_110m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name='110米温度(°C)',
        validators=[MinValueValidator(-50), MaxValueValidator(50)]
    )
    wind_direction_110m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name='110米风向(度)',
        validators=[MinValueValidator(0), MaxValueValidator(360)]
    )
    wind_speed_70m = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name='70米风速(m/s)',
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )

    class Meta:
        db_table = 'measureWeatherData2'  # 指定数据库表名
        verbose_name = '气象数据2（多高度层）'
        verbose_name_plural = '气象数据2（多高度层）'
        unique_together = (('station', 'date_time'),)  # 联合唯一约束
        ordering = ['-date_time']  # 默认按时间降序

    def __str__(self):
        return f"{self.station.station_name} - {self.date_time}"

class ShortPowerData(models.Model):
    """短期功率预测数据表"""
    forecast_id = models.AutoField(primary_key=True, verbose_name='预测记录ID')
    task = models.ForeignKey(
        'ForecastTask',
        on_delete=models.CASCADE,
        db_column='task_id',
        verbose_name='关联预测任务'
    )
    timestamp = models.DateTimeField(verbose_name='预测时间点')
    power_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='功率预测值(kW)',
        validators=[MinValueValidator(0)]
    )

    class Meta:
        db_table = 'shortPowerData'
        verbose_name = '短期功率预测数据'
        verbose_name_plural = '短期功率预测数据'
        unique_together = (('task', 'timestamp'),)
        indexes = [
            models.Index(fields=['timestamp']),  # 时间字段索引
            models.Index(fields=['task', 'timestamp'])  # 联合索引
        ]

    def __str__(self):
        return f"{self.task_id}@{self.timestamp}: {self.power_value}kW"

class ApiLog(models.Model):
    """API调用日志表"""
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH')
    ]

    log_id = models.AutoField(primary_key=True, verbose_name='日志ID')
    endpoint = models.CharField(max_length=200, verbose_name='API端点')
    request_method = models.CharField(
        max_length=10,
        choices=HTTP_METHODS,
        verbose_name='请求方法'
    )
    request_params = models.JSONField(
        null=True, blank=True,
        verbose_name='请求参数'
    )
    response_status = models.IntegerField(verbose_name='响应状态码')
    response_time = models.IntegerField(
        null=True, blank=True,
        verbose_name='响应时间(ms)'
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name='客户端IP'
    )
    user_agent = models.CharField(
        max_length=200,
        null=True, blank=True,
        verbose_name='用户代理'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'api_log'
        verbose_name = 'API调用日志'
        verbose_name_plural = 'API调用日志'
        ordering = ['-created_at']  # 最新日志在前

    def __str__(self):
        return f"{self.request_method} {self.endpoint} - {self.response_status}"
