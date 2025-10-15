import pandas as pd

df1 = pd.read_csv('/Users/cyqsnd/Desktop/dachuang/dachuang-data/场站数据/新乐场站/气象预报数据-DXwind_P0test024_weather_short.csv')
df2 = pd.read_csv('/Users/cyqsnd/Desktop/dachuang/dachuang-data/场站数据/新乐场站/p历史功率记录-owerHis.csv')

df1_unique = df1.drop_duplicates(subset='timeStamp')
df2_unique = df2.drop_duplicates(subset='timeStamp')

# 按 timeStamp 合并
merged = pd.merge(df1_unique, df2_unique, on=['timeStamp'], how='inner')

# 导出合并后的 CSV
merged.to_csv('新乐场站.csv', index=False)