import pandas as pd
import sys

file_path = 'Treasury System Database V2_Internal.xlsx'

# Get all sheet names
excel_file = pd.ExcelFile(file_path)
sheet_names = excel_file.sheet_names

print('='*80)
print('EXCEL FILE ANALYSIS: Treasury System Database V2_Internal.xlsx')
print('='*80)
print(f'\nTotal Sheets: {len(sheet_names)}')
print('\nSheet Categories:')
print('-' * 40)

# Categorize sheets
categories = {
    'Master Data': [],
    'Product Structure': [],
    'Test Cases/Scenarios': [],
    'Monthly Data': [],
    'Mapping/Reference': [],
    'Other': []
}

for name in sheet_names:
    if any(x in name.lower() for x in ['master', 'code', 'haircut', 'swift']):
        categories['Master Data'].append(name)
    elif any(x in name.lower() for x in ['product', 'structure', 'table structure']):
        categories['Product Structure'].append(name)
    elif any(x in name.lower() for x in ['case', 'test', 'mock', 'business requirement']):
        categories['Test Cases/Scenarios'].append(name)
    elif any(x in name.lower() for x in ['v4_result', 'sep', 'oct', 'nov', 'dec', '2025']):
        categories['Monthly Data'].append(name)
    elif any(x in name.lower() for x in ['mapping', 'resident', 'customer', 'agency']):
        categories['Mapping/Reference'].append(name)
    else:
        categories['Other'].append(name)

for cat, sheets in categories.items():
    if sheets:
        print(f'\n{cat}:')
        for s in sheets:
            print(f'  - {s}')

# Extract key structural sheets
print('\n' + '='*80)
print('KEY TABLE STRUCTURES')
print('='*80)

# 1. Product Table Structure
print('\n--- PRODUCT TABLE STRUCTURE ---')
try:
    df = pd.read_excel(file_path, sheet_name='Product_table structure')
    print(df.to_string(index=False))
except Exception as e:
    print(f'Error: {e}')

# 2. Haircut Table
print('\n--- HAIRCUT TABLE ---')
try:
    df = pd.read_excel(file_path, sheet_name='Haircut_table')
    print(df.to_string(index=False))
except Exception as e:
    print(f'Error: {e}')

# 3. Bank Code
print('\n--- BANK CODE REFERENCE ---')
try:
    df = pd.read_excel(file_path, sheet_name='BANK_CODE')
    print(df.head(20).to_string(index=False))
except Exception as e:
    print(f'Error: {e}')

print('\n' + '='*80)
print('Analysis complete!')
print('='*80)
