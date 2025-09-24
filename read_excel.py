import pandas as pd
import sys

# Excelファイルを読み込む
df = pd.read_excel('クリニック情報.xlsx')

print('=' * 80)
print('シート名:', pd.ExcelFile('クリニック情報.xlsx').sheet_names)
print('=' * 80)
print('データの形状:', df.shape)
print('=' * 80)
print('列名:')
for i, col in enumerate(df.columns):
    print(f"  {i+1}. {col}")
print('=' * 80)
print('\n全データ:\n')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
print(df)
print('=' * 80)

# 各セルの内容を個別に表示
for idx, row in df.iterrows():
    print(f'\n行 {idx + 1}:')
    for col in df.columns:
        print(f'\n[{col}]')
        value = row[col]
        if pd.notna(value):
            if isinstance(value, str) and '\n' in value:
                print('(複数行のテキスト)')
                for line in value.split('\n'):
                    print(f'  - {line}')
            else:
                print(f'  {value}')
        else:
            print('  (空)')