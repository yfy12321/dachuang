from django.db import models

# Create your models here.

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

    class Meta:
        db_table = 'power_station'  # 指定实际的表名
        managed = False  

    def __str__(self):
        return self.station_name
