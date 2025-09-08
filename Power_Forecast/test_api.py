#!/usr/bin/env python3
"""
测试API接口
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🔍 测试API接口...")
    print("=" * 50)
    
    # 测试1: 检查表结构
    print("1. 测试表结构检查接口...")
    try:
        response = requests.get(f"{base_url}/tables/api/check-structure/")
        if response.status_code == 200:
            data = response.json()
            print("✅ 表结构检查成功")
            print(f"   表名: {data['table_name']}")
            print(f"   字段数: {len(data['columns'])}")
        else:
            print(f"❌ 表结构检查失败: {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"❌ 表结构检查异常: {e}")
    
    print()
    
    # 测试2: 获取场站列表
    print("2. 测试场站列表接口...")
    try:
        response = requests.get(f"{base_url}/tables/api/stations/")
        if response.status_code == 200:
            stations = response.json()
            print(f"✅ 场站列表获取成功，共 {len(stations)} 个场站")
            for station in stations[:3]:  # 显示前3个
                print(f"   - {station['id']}: {station['name']}")
        else:
            print(f"❌ 场站列表获取失败: {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"❌ 场站列表获取异常: {e}")
    
    print()
    
    # 测试3: 获取场站详情
    print("3. 测试场站详情接口...")
    try:
        response = requests.get(f"{base_url}/tables/api/stations/1/")
        if response.status_code == 200:
            station = response.json()
            print("✅ 场站详情获取成功")
            print(f"   场站名称: {station['name']}")
            print(f"   装机容量: {station['install_capacity']}")
            print(f"   总容量: {station['total_capacity']}")
        else:
            print(f"❌ 场站详情获取失败: {response.status_code}")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"❌ 场站详情获取异常: {e}")

if __name__ == "__main__":
    test_api() 