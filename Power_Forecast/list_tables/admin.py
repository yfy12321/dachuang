'''
from django.contrib import admin

# Register your models here.
#以下为ds 8.4修改  里面字段有问题，还得改
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from .models import Station

# 自定义数字范围过滤器（替代旧的NumberFieldListFilter）
class EfficiencyFilter(SimpleListFilter):
    title = '效率系数范围'
    parameter_name = 'efficiency'

    def lookups(self, request, model_admin):
        return (
            ('0-1', '0~1'),
            ('1-1.5', '1~1.5'),
            ('1.5-2', '1.5~2'),
            ('2+', '2以上'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == '0-1':
            return queryset.filter(efficiency__gte=0, efficiency__lte=1)
        elif value == '1-1.5':
            return queryset.filter(efficiency__gt=1, efficiency__lte=1.5)
        elif value == '1.5-2':
            return queryset.filter(efficiency__gt=1.5, efficiency__lte=2)
        elif value == '2+':
            return queryset.filter(efficiency__gt=2)
        return queryset


@admin.register(Station)

class PowerStationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'formatted_capacity',
        'total_power',
        'location_coordinates',
        'efficiency',
        'csv_download_link',
        'created_at'
    )
    
    search_fields = ('station_name', 'capacity', 'total_power')
    
    # 使用自定义过滤器替代NumberFieldListFilter
    list_filter = (
        'created_at',
        EfficiencyFilter,  # 替换原来的NumberFieldListFilter
    )
    
    
    # 分页设置
    list_per_page = 20
    
    # 字段分组显示（编辑页）
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'capacity', 'total_power')
        }),
        ('地理坐标', {
            'fields': ('latitude', 'longitude'),
            'description': '精确到小数点后6位'
        }),
        ('技术指标', {
            'fields': ('efficiency',)
        }),
        ('预测配置', {
            'fields': (
                'short_term_prediction',
                'daily_prediction',
                'weekly_prediction'
            ),
            'classes': ('collapse',)  # 可折叠
        }),
        ('数据文件', {
            'fields': ('csv_file',)
        }),
    )
    
    # 自定义方法
    def formatted_capacity(self, obj):
        return f"{obj.capacity} 装机"
    formatted_capacity.short_description = '装机容量'
    
    def location_coordinates(self, obj):
        return f"({obj.latitude}, {obj.longitude})"
    location_coordinates.short_description = '经纬度'
    
    def csv_download_link(self, obj):
        if obj.csv_file:
            return format_html(
                '<a href="{}" download>⬇️ 下载</a> | '
                '<a href="{}" target="_blank">🔍 预览</a>',
                obj.csv_file.url,
                obj.csv_file.url
            )
        return "-"
    csv_download_link.short_description = '数据文件'
    csv_download_link.allow_tags = True
'''
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
from .models import Station

class EfficiencyFilter(SimpleListFilter):
    title = '效率系数范围'
    parameter_name = 'efficiency'

    def lookups(self, request, model_admin):
        return (
            ('0-1', '0~1'),
            ('1-1.5', '1~1.5'),
            ('1.5-2', '1.5~2'),
            ('2+', '2以上'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == '0-1':
            return queryset.filter(efficiency__gte=0, efficiency__lte=1)
        elif value == '1-1.5':
            return queryset.filter(efficiency__gt=1, efficiency__lte=1.5)
        elif value == '1.5-2':
            return queryset.filter(efficiency__gt=1.5, efficiency__lte=2)
        elif value == '2+':
            return queryset.filter(efficiency__gt=2)
        return queryset

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = (
        'station_name',  # 使用实际字段名
        'formatted_capacity',
        'unit_config',
        'location_coordinates',
        'area_km2',
        'csv_path',
       
    )
    
    search_fields = ('station_name', 'unit_config', 'installed_cap')
    
 
    list_per_page = 20
    
    fieldsets = (
        ('基础信息', {
            'fields': (
                'station_name', 
                'unit_config',
                'installed_cap',
                'area_km2'
            )
        }),
        ('地理坐标', {
            'fields': ('latitude', 'longitude'),
            'description': '精确到小数点后6位'
        }),
        ('预测规则配置', {
            'fields': (
                'ultra_short_term_rule',
                'day_ahead_rule',
                'mid_long_term_rule'
            ),
            'classes': ('collapse',)
        }),
        ('数据文件', {
            'fields': ('csv_path',)
        }),
    )
    
    # 自定义方法
    def formatted_capacity(self, obj):
        return f"{obj.installed_cap}MW"  # 使用installed_cap字段
    formatted_capacity.short_description = '装机容量'
    
    def location_coordinates(self, obj):
        return f"({obj.latitude}, {obj.longitude})"
    location_coordinates.short_description = '经纬度'
    
    def csv_download_link(self, obj):
        if obj.csv_path:
            return format_html(
                '<a href="{}" download>⬇️ 下载</a>',
                obj.csv_path
            )
        return "-"
    csv_download_link.short_description = '数据文件'