#!/usr/bin/env python3
"""
检查power_station表的实际结构
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Power_Forecast.settings')
django.setup()

from django.db import connection

def check_table_structure():
    """检查power_station表的实际结构"""
    try:
        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'power_station'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("❌ power_station表不存在")
                return
            
            print("✅ power_station表存在")
            
            # 获取表结构
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'power_station'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print("\n📋 实际表结构:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'可空' if col[2] == 'YES' else '非空'})")
            
            # 获取数据行数
            cursor.execute("SELECT COUNT(*) FROM power_station")
            count = cursor.fetchone()[0]
            print(f"\n📊 数据行数: {count}")
            
            # 获取前3行数据作为示例
            if count > 0:
                cursor.execute("SELECT * FROM power_station LIMIT 3")
                sample_data = cursor.fetchall()
                print(f"\n📄 示例数据 (前3行):")
                for i, row in enumerate(sample_data, 1):
                    print(f"  行{i}: {row}")
            
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")

if __name__ == "__main__":
    check_table_structure() 