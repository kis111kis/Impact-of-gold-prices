"""
Загрузка данных через Yahoo Finance (бесплатно)
Для автоматического обновления данных

Требуется: pip install yfinance pandas numpy
"""

import sys
import os

# Fix Windows console encoding for Russian text
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Yahoo Finance tickers - МАКРОЭКОНОМИЧЕСКИЕ ПОКАЗАТЕЛИ
YAHOO_TICKERS_MACRO = {
    'GC=F': 'Gold',        # Золото
    '^GSPC': 'SP500',      # S&P 500  
    'DX-Y.NYB': 'USD',     # Индекс доллара
    'CL=F': 'Oil',         # Нефть
    '^VIX': 'Vix',         # VIX
    '^TNX': 'Rates',       # Доходность 10-летних облигаций
}

# Yahoo Finance tickers - ИНДЕКСЫ ЗОЛОТОДОБЫЧИ (GDM, MSCI, MVG, XGD, GDX, FTGM, HUI, XAU)
YAHOO_TICKERS_MINING = {
    'GDX': 'GDX',          # VanEck Gold Miners ETF -> GDM
    'MSCI': 'MSCI',        # MSCI ACWI IMI -> MSCI
    '^MVG': 'MVG',          # MVIS Global Junior Gold Miners -> MVG
    'XGD.TO': 'XGD',       # iShares S&P/TSX Global Gold Mining -> XGD
    'GDMNTR': 'GDM',         # US Global GO GOLD -> GDX (альтернатива)
    '^GMIN.FGI': 'FTGM',        # FTSE Gold Mines -> FTGM
    'HUI': 'HUI',          # VanEck Gold Miners BUGS -> HUI
    # 'XAU': 'XAU',          # Philadelphia Gold & Silver -> XAU
}

# Try to import yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("WARNING: yfinance not installed. Run: pip install yfinance")


def load_from_yahoo(ticker, start_date, end_date):
    """Загрузка данных через Yahoo Finance с поддержкой MultiIndex"""
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        data = yf.download(ticker, start=start_str, end=end_str, progress=False)
        
        if data.empty:
            return None
        
        # Сбрасываем индекс, чтобы Date стала колонкой
        data = data.reset_index()
        
        # Обработка MultiIndex в колонках
        if isinstance(data.columns, pd.MultiIndex):
            # Создаем плоские имена колонок: "Close_HUI", "High_HUI", ...
            new_columns = ['Date']  # начинаем с Date
            for i in range(1, len(data.columns)):
                price_level = data.columns[i][0]  # 'Close', 'High', etc.
                ticker_level = data.columns[i][1]  # 'HUI', 'XAU', etc.
                new_columns.append(f"{price_level}_{ticker_level}")
            data.columns = new_columns
        else:
            # Если колонки уже плоские, просто переименовываем первую в Date если нужно
            if data.columns[0] != 'Date':
                data = data.rename(columns={data.columns[0]: 'Date'})
        
        # Создаем результат
        # Ищем колонку с Close
        close_col = None
        for col in data.columns:
            if 'Close' in col:
                close_col = col
                break
        
        if close_col is None:
            return None
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(data['Date']),
            'Price': data[close_col],
        })
        
        # Опционально добавляем остальные колонки, если они нужны
        open_col = next((col for col in data.columns if 'Open' in col), None)
        high_col = next((col for col in data.columns if 'High' in col), None)
        low_col = next((col for col in data.columns if 'Low' in col), None)
        volume_col = next((col for col in data.columns if 'Volume' in col), None)
        
        if open_col:
            df['Open'] = data[open_col]
        if high_col:
            df['High'] = data[high_col]
        if low_col:
            df['Low'] = data[low_col]
        if volume_col:
            df['Volume'] = data[volume_col]
        
        df = df.sort_values('Date').reset_index(drop=True)
        return df
        
    except Exception as e:
        print(f"Error loading {ticker}: {e}")
        return None

def load_fresh_data(data_type='all', start_date=None, end_date=None, use_yahoo=True):
    """
    Main function to load fresh data with calibration factors
    to match Investing.com data format
    """
    from datetime import datetime
    
    # Калибровочные коэффициенты для Yahoo данных (подобраны по твоему сравнению)
    SCALING_FACTORS = {
        'HUI': 3333.0,      # Yahoo даёт в долях, Investing в пунктах
        'MSCI': 14.44,      # Масштабирование MSCI
        'GDX': 1.0,         # Пока без изменений
        'XGD': 1.0,         # Пока без изменений
        'MVG': 1.0,         # Не загружался
        'FTGM': 1.0,        # Не загружался
        'GDM': 1.0,         # Не загружался
    }

    if end_date is None:
        end_date = datetime(2026, 2, 21)
    elif isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)
    
    if start_date is None:
        start_date = end_date - timedelta(days=365*20)
    
    print("="*60)
    print("LOADING DATA")
    print("="*60)
    print(f"Period: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
    print(f"Data type: {data_type}")
    print(f"Yahoo Finance available: {YFINANCE_AVAILABLE}")
    print("="*60)
    
    if use_yahoo and YFINANCE_AVAILABLE:
        print("\nUsing Yahoo Finance (FREE)")
        
        if data_type == 'macro':
            tickers = YAHOO_TICKERS_MACRO
        elif data_type == 'mining':
            tickers = YAHOO_TICKERS_MINING
        else:
            tickers = {**YAHOO_TICKERS_MACRO, **YAHOO_TICKERS_MINING}
        
        load_func = lambda t: load_from_yahoo(t, start_date, end_date)
    else:
        print("\nERROR: Yahoo Finance not available")
        return None
    
    all_data = {}
    
    for ticker, name in tickers.items():
        print(f"Loading {ticker} ({name})...")
        df = load_func(ticker)
        if df is not None:
            # Применяем калибровку для индексов золотодобычи
            if name in SCALING_FACTORS and SCALING_FACTORS[name] != 1.0:
                old_mean = df['Price'].mean()
                df['Price'] = df['Price'] * SCALING_FACTORS[name]
                new_mean = df['Price'].mean()
                print(f"   📊 Scaled {name}: {old_mean:.4f} -> {new_mean:.2f} (x{SCALING_FACTORS[name]})")
            
            all_data[name] = df
            print(f"   OK: {len(df)} records")
        else:
            print(f"   FAILED")
    
    if all_data:
        merged_df = None
        for name, df in all_data.items():
            df_renamed = df[['Date', 'Price']].rename(columns={'Price': name})
            if merged_df is None:
                merged_df = df_renamed
            else:
                merged_df = pd.merge(merged_df, df_renamed, on='Date', how='outer')
        
        merged_df = merged_df.sort_values('Date').reset_index(drop=True)
        
        print(f"\nTotal: {len(merged_df)} records")
        print(f"Period: {merged_df['Date'].min()} - {merged_df['Date'].max()}")
        print(f"Columns: {list(merged_df.columns)}")
        
        return merged_df
    
    return None


if __name__ == "__main__":
    print("Testing data loader...")
    df = load_fresh_data(data_type='all')
    
    if df is not None:
        print("\nFirst rows:")
        print(df.head())
