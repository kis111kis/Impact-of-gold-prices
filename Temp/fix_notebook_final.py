import json

# Read notebook - use relative path from project root
import os
os.chdir('/home/lisa/DIPLOMA/RANEPA')
with open('Panel_regression.ipynb', 'r') as f:
    nb = json.load(f)

# Find where to insert the old loading cells
new_cells = []

for i, cell in enumerate(nb['cells']):
    source = ''.join(cell.get('source', []))
    
    # Keep everything except current data loading
    if i == 3 and ('load_fresh_data' in source or 'merged_df' in source):
        # Replace with both options
        new_source = '''# =============================================================================
# ВЫБОР ИСТОЧНИКА ДАННЫХ
# =============================================================================
# Раскомментируйте ОДИН из вариантов ниже:

# ВАРИАНТ 1: Загрузка из Yahoo Finance (новые данные)
# from data_loader import load_fresh_data
# merged_df = load_fresh_data(data_type='all', use_yahoo=True)

# ВАРИАНТ 2: Загрузка из файлов (старые данные из data2)
import pandas as pd
import glob

files_config = [
    {"path": "data2/Прошлые данные - Arca Gold Miners.csv", "col_name": "GDM", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - MSCI ACWI IMI.csv", "col_name": "MSCI", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - MVIS Global Junior Gold Miners TR Net.csv", "col_name": "MVG", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - XAU_USD.csv", "col_name": "XGD", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - GDX.csv", "col_name": "GDX", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - FTSE Gold Mines.csv", "col_name": "FTGM", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - Arca Gold BUGS.csv", "col_name": "HUI", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - Philadelphia Gold_Silver.csv", "col_name": "XAU", "date_format": "%d.%m.%Y"},
]

# Макро данные (эти одинаковые)
macro_files = [
    {"path": "data2/Прошлые данные - XAU_USD.csv", "col_name": "Gold", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - S&P 500.csv", "col_name": "SP500", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - Индекс USD.csv", "col_name": "USD", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - Фьючерс на нефть Brent.csv", "col_name": "Oil", "date_format": "%d.%m.%Y"},
    {"path": "data2/Прошлые данные - CBOE Volatility Index.csv", "col_name": "Vix", "date_format": "%d.%m.%Y"},
    {"path": "data2/United States 10-Year Bond Yield Historical Data (2).csv", "col_name": "Rates", "date_format": "%d.%m.%Y"},
]

# Загрузка данных
dataframes = {}
for config in files_config + macro_files:
    try:
        df = pd.read_csv(config["path"])
        df['Date'] = pd.to_datetime(df['Date'], format=config["date_format"])
        price_col = 'Price' if 'Price' in df.columns else 'Цена'
        dataframes[config["col_name"]] = df[['Date', price_col]].rename(columns={price_col: config["col_name"]})
        print(f"Loaded {config['col_name']}: {len(dataframes[config['col_name']])} records")
    except Exception as e:
        print(f"Error loading {config['col_name']}: {e}")

# Объединение
merged_df = None
for name, df in dataframes.items():
    if merged_df is None:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on='Date', how='outer')

merged_df = merged_df.sort_values('Date').reset_index(drop=True)
print(f"Total: {len(merged_df)} records")
print(f"Columns: {list(merged_df.columns)}")
'''
        cell['source'] = [new_source]
        print(f"Updated cell {i}")
    
    new_cells.append(cell)

nb['cells'] = new_cells

# Save
with open('Panel_regression.ipynb', 'w') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Notebook updated with both options!")
