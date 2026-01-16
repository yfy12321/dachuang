"""
修复 forecast_tasks_information 表的 task_id 序列

使用方法:
    python manage.py fix_task_id_sequence
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '修复 forecast_tasks_information 表的 task_id 序列'

    def handle(self, *args, **options):
        table_name = 'forecast_tasks_information'
        column_name = 'task_id'
        sequence_name = f'{table_name}_{column_name}_seq'
        
        with connection.cursor() as cursor:
            try:
                # 1. 检查序列是否存在
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_sequences 
                        WHERE schemaname = 'public' AND sequencename = %s
                    )
                """, [sequence_name])
                
                sequence_exists = cursor.fetchone()[0]
                
                if not sequence_exists:
                    self.stdout.write(self.style.WARNING(f'序列 {sequence_name} 不存在，正在创建...'))
                    # 创建序列
                    cursor.execute(f"""
                        CREATE SEQUENCE {sequence_name}
                        START WITH 1
                        INCREMENT BY 1
                        NO MINVALUE
                        NO MAXVALUE
                        CACHE 1
                    """)
                    self.stdout.write(self.style.SUCCESS(f'序列 {sequence_name} 已创建'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'序列 {sequence_name} 已存在'))
                
                # 2. 设置字段默认值为序列
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ALTER COLUMN {column_name} 
                    SET DEFAULT nextval('{sequence_name}'::regclass)
                """)
                self.stdout.write(self.style.SUCCESS(f'已设置 {column_name} 字段的默认值为序列'))
                
                # 3. 同步序列值（确保序列值至少等于表中最大值）
                cursor.execute(f"""
                    SELECT COALESCE(MAX({column_name}), 0) 
                    FROM {table_name}
                """)
                max_value = cursor.fetchone()[0] or 0
                
                if max_value > 0:
                    cursor.execute(f"""
                        SELECT setval('{sequence_name}', {max_value}, true)
                    """)
                    self.stdout.write(self.style.SUCCESS(f'已同步序列值到 {max_value}'))
                else:
                    # 如果表为空，确保序列从1开始
                    cursor.execute(f"""
                        SELECT setval('{sequence_name}', 1, false)
                    """)
                    self.stdout.write(self.style.SUCCESS('序列已重置为1'))
                
                connection.commit()
                self.stdout.write(self.style.SUCCESS('序列修复完成！'))
                
            except Exception as e:
                connection.rollback()
                self.stdout.write(self.style.ERROR(f'修复序列时出错: {str(e)}'))
                raise
