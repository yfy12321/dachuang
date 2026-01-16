"""
数据库工具函数
"""
from django.db import connection


def ensure_sequence_exists(table_name, column_name, sequence_name=None):
    """
    确保 PostgreSQL 序列存在并正确关联到字段
    
    Args:
        table_name: 表名
        column_name: 列名
        sequence_name: 序列名（可选，如果不提供则自动生成）
    """
    if sequence_name is None:
        sequence_name = f"{table_name}_{column_name}_seq"
    
    with connection.cursor() as cursor:
        # 检查序列是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_sequences 
                WHERE schemaname = 'public' AND sequencename = %s
            )
        """, [sequence_name])
        
        sequence_exists = cursor.fetchone()[0]
        
        if not sequence_exists:
            # 创建序列
            cursor.execute(f"""
                CREATE SEQUENCE IF NOT EXISTS {sequence_name}
                START WITH 1
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1
            """)
        
        # 检查字段的默认值是否设置为序列
        cursor.execute(f"""
            SELECT column_default 
            FROM information_schema.columns 
            WHERE table_name = %s 
            AND column_name = %s
        """, [table_name, column_name])
        
        result = cursor.fetchone()
        current_default = result[0] if result else None
        
        # 如果默认值不是序列，则设置它
        expected_default = f"nextval('{sequence_name}'::regclass)"
        if current_default != expected_default:
            cursor.execute(f"""
                ALTER TABLE {table_name} 
                ALTER COLUMN {column_name} 
                SET DEFAULT nextval('{sequence_name}'::regclass)
            """)
        
        # 确保序列的当前值至少等于表中最大的值
        cursor.execute(f"""
            SELECT COALESCE(MAX({column_name}), 0) 
            FROM {table_name}
        """)
        max_value = cursor.fetchone()[0] or 0
        
        if max_value > 0:
            cursor.execute(f"""
                SELECT setval('{sequence_name}', {max_value}, true)
            """)
        
        connection.commit()
        return True
