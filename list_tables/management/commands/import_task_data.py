from django.core.management.base import BaseCommand, CommandError
from list_tables.models import Task_Data
import pandas as pd
from django.db import transaction
from datetime import datetime
import math
import json

# python manage.py import_task_data csv_path.csv --chunksize 1000

# 选项：
# csv_path（必需）：CSV 文件路径
# --chunksize（可选，默认1000）：每次读取与插入的行数
# --encoding（可选，默认 utf-8）：CSV 编码
# --dry-run（可选）：仅解析并打印解析信息，不写入数据库
# --station-id（可选）：覆盖 CSV 中的 station_id，所有导入记录使用该值
# --preview-rows（可选，默认3）：在 --dry-run 时显示每个 chunk 的前 N 行示例

class Command(BaseCommand):
    # 从 CSV 文件批量导入数据到 Task_Data 表

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='CSV 文件路径')
        parser.add_argument('--chunksize', type=int, default=1000, help='每次批量插入的行数')
        parser.add_argument('--encoding', type=str, default='utf-8', help='CSV 文件编码')
        parser.add_argument('--dry-run', action='store_true', help='仅解析并展示统计信息，不写入数据库')
        parser.add_argument('--preview-rows', type=int, default=3, help='在 --dry-run 时显示每个 chunk 的前 N 行示例')
        parser.add_argument('--station-id', type=int, default=None, help='如果提供，则覆盖 CSV 中的 station_id，所有导入记录使用该值')

    def _parse_timestamp(self, val):
        if val is None:
            return None
        if isinstance(val, pd.Timestamp):
            return val.to_pydatetime()
        try:
            return datetime.fromisoformat(str(val))
        except Exception:
            # 最后尝试让 pandas 解析
            try:
                return pd.to_datetime(val).to_pydatetime()
            except Exception:
                return None

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        chunksize = options['chunksize']
        encoding = options['encoding']
        dry_run = options['dry_run']

        # 预计算模型的可写字段名（排除自动创建字段）
        model_fields = {f.name for f in Task_Data._meta.get_fields() if getattr(f, 'concrete', False) and not getattr(f, 'auto_created', False)}

        try:
            total = 0
            # 使用 pandas 分块读取，要求 CSV 的列名与模型字段名一致（或做适当映射）
            for chunk in pd.read_csv(csv_path, chunksize=chunksize, encoding=encoding):
                objs = []
                # 将各种缺失值（numpy.nan, pandas.NA 等）统一转换为 Python None
                chunk = chunk.where(pd.notnull(chunk), None)

                station_id_override = options.get('station_id')
                for _, row in chunk.iterrows():
                    # 把 pandas Series 转为 dict，并统一把缺失值转为 None
                    row_dict = {}
                    for k, v in row.items():
                        # pandas 的 NA/nan/None 都应该被映射为 Python None
                        if pd.isna(v):
                            row_dict[k] = None
                        else:
                            row_dict[k] = v

                    # 删除常见的无用索引列名（例如 pandas 保存索引导致的 'Unnamed: 0'）
                    row_dict.pop('Unnamed: 0', None)

                    # 应用 station_id 覆盖逻辑（若提供）
                    if station_id_override is not None:
                        # 仅设置到 kwargs 中，如果模型包含该字段
                        row_dict['station_id'] = station_id_override

                    # 如果包含 timeStamp 字段，尝试解析为 datetime
                    if 'timeStamp' in row_dict:
                        row_dict['timeStamp'] = self._parse_timestamp(row_dict.get('timeStamp'))

                    # 过滤，只保留模型中存在的字段，并再次确保值为 Python 原生类型（None 已处理）
                    kwargs = {}
                    for k, v in row_dict.items():
                        if k in model_fields:
                            # 把 pandas/ numpy 缺失值统一为 None
                            if pd.isna(v):
                                v = None
                            else:
                                # 把 numpy 的标量转换为 Python 原生类型（如果需要）
                                if hasattr(v, 'item') and not isinstance(v, (str, bytes)):
                                    try:
                                        v = v.item()
                                    except Exception:
                                        pass
                                # 如果是 float('nan')，也设为 None
                                try:
                                    if isinstance(v, float) and math.isnan(v):
                                        v = None
                                except Exception:
                                    pass
                            kwargs[k] = v

                    # 如果 station_id 在模型字段中且值非 None，尝试转换为 int
                    if 'station_id' in kwargs and kwargs.get('station_id') is not None:
                        try:
                            kwargs['station_id'] = int(kwargs['station_id'])
                        except Exception:
                            # 若转换失败，保留原值（后续数据库可能报错或校验）
                            pass

                    # 最终构建对象（避免向模型传入不存在的字段）
                    obj = Task_Data(**kwargs)
                    objs.append(obj)

                if dry_run:
                    preview = options.get('preview_rows', 3)
                    try:
                        # chunk 是 pandas DataFrame，打印前几行但用与写入相同的过滤逻辑，展示最终 kwargs 示例
                        examples = []
                        for _, r in chunk.head(preview).iterrows():
                            # 使用与写入相同的清洗逻辑：把缺失值转换为 None，过滤出模型字段
                            rdict = {}
                            for k, v in r.items():
                                if pd.isna(v):
                                    rdict[k] = None
                                else:
                                    val = v
                                    if hasattr(val, 'item') and not isinstance(val, (str, bytes)):
                                        try:
                                            val = val.item()
                                        except Exception:
                                            pass
                                    # normalize float('nan')
                                    try:
                                        if isinstance(val, float) and math.isnan(val):
                                            val = None
                                    except Exception:
                                        pass
                                    rdict[k] = val
                            rdict.pop('Unnamed: 0', None)
                            # 应用 station_id 覆盖
                            station_id_override = options.get('station_id')
                            if station_id_override is not None:
                                rdict['station_id'] = station_id_override
                            # 解析 timeStamp
                            if 'timeStamp' in rdict:
                                rdict['timeStamp'] = self._parse_timestamp(rdict.get('timeStamp'))
                            # 只保留模型字段
                            filtered = {k: v for k, v in rdict.items() if k in model_fields}
                            # 尝试转换 station_id 为 int
                            if 'station_id' in filtered and filtered.get('station_id') is not None:
                                try:
                                    filtered['station_id'] = int(filtered['station_id'])
                                except Exception:
                                    pass
                            examples.append(filtered)

                        self.stdout.write(self.style.NOTICE(f'Parsed chunk with {len(objs)} rows (dry-run) - final kwargs examples:'))
                        self.stdout.write(json.dumps(examples, ensure_ascii=False, default=str, indent=2))
                    except Exception:
                        # 回退到原始简单提示
                        self.stdout.write(self.style.SUCCESS(f'Parsed chunk with {len(objs)} rows (dry-run)'))
                else:
                    with transaction.atomic():
                        Task_Data.objects.bulk_create(objs)
                    self.stdout.write(self.style.SUCCESS(f'Inserted chunk with {len(objs)} rows'))

                total += len(objs)

            self.stdout.write(self.style.SUCCESS(f'Finished. Total rows processed: {total}'))

        except FileNotFoundError:
            raise CommandError(f'CSV 文件未找到: {csv_path}')
        except Exception as e:
            raise CommandError(str(e))
