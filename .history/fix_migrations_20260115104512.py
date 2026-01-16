import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from datetime import datetime

cursor = connection.cursor()

# 标记有问题的迁移为已应用
migrations_to_mark = [
    '0004_task_data',
    '0005_alter_task_data_id',
    '0006_alter_task_data_id',
    '0007_task_data_wdir_task_data_wspd',
    '0008_forecasttaskinformation',
    '0009_forecasttaskinformation_error_message'
]

for migration in migrations_to_mark:
    try:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            ['list_tables', migration, datetime.now()]
        )
        print(f"✓ 标记 {migration} 为已应用")
    except Exception as e:
        print(f"✗ {migration}: {str(e)}")

connection.commit()
cursor.close()

print("\n迁移标记完成！")
