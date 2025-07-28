#!/usr/bin/env python3
"""
测试数据库连接和power_station表结构
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Power_Forecast.settings')
django.setup()

from django.db import connection

def test_connection():
    """测试数据库连接"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ 数据库连接成功")
            print(f"数据库版本: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def check_power_station_table():
    """检查power_station表"""
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
                return False
            
            print("✅ power_station表存在")
            
            # 获取表结构
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'power_station'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print("\n📋 表结构:")
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
            
            return True
            
    except Exception as e:
        print(f"❌ 检查power_station表失败: {e}")
        return False

def main():
    print("🔍 测试数据库连接和power_station表...")
    print("=" * 50)
    
    if not test_connection():
        return
    
    print()
    if not check_power_station_table():
        return
    
    print("\n✅ 所有测试通过！")

if __name__ == "__main__":
    main() 