import pandas as pd
import os

# Read the Excel file
file_path = r'c:\Users\varayut.tun\Documents\Antigravity\TR Dev2026\data\source\Treasury_System_Database_V2_Internal.xlsx'
df = pd.read_excel(file_path, sheet_name='All Table_V4_Clean', header=None)

# Output file path
output_path = r'c:\Users\varayut.tun\Documents\Antigravity\TR Dev2026\data\extracted'
os.makedirs(output_path, exist_ok=True)
output_file = os.path.join(output_path, 'table_structures.md')

# Store extracted tables
tables = []

i = 0
while i < len(df):
    row = df.iloc[i]
    col0 = row[0]
    
    # Check if this is a table name row (non-null in column 0, not header row)
    if pd.notna(col0) and str(col0).strip() not in ['', 'Column Name', 'Timestamp update as of']:
        col0_str = str(col0).strip()
        # Skip timestamp rows and other metadata
        if col0_str and not col0_str.startswith('20'):
            # This is likely a table name
            table_name = col0_str
            
            # Look for description in next row
            description = ''
            if i + 1 < len(df):
                next_row = df.iloc[i + 1]
                if pd.notna(next_row[0]):
                    desc_text = str(next_row[0]).strip()
                    if desc_text and desc_text != table_name:
                        description = desc_text
            
            # Skip header row (find 'Column Name' row)
            header_row_idx = None
            for j in range(i, min(i + 5, len(df))):
                check_row = df.iloc[j]
                if pd.notna(check_row[0]) and 'Column Name' in str(check_row[0]):
                    header_row_idx = j
                    break
            
            if header_row_idx:
                # Extract columns starting from header_row_idx + 1
                columns = []
                k = header_row_idx + 1
                while k < len(df):
                    col_row = df.iloc[k]
                    if pd.notna(col_row[0]):
                        col_name = str(col_row[0]).strip()
                        if col_name and col_name not in ['Column Name']:
                            data_type = str(col_row[1]) if pd.notna(col_row[1]) else ''
                            col_desc = str(col_row[2]) if pd.notna(col_row[2]) else ''
                            example = str(col_row[3]) if pd.notna(col_row[3]) else ''
                            pk_fk = str(col_row[4]) if pd.notna(col_row[4]) else ''
                            allow_null = str(col_row[5]) if pd.notna(col_row[5]) else ''
                            
                            columns.append({
                                'name': col_name,
                                'data_type': data_type,
                                'description': col_desc,
                                'example': example,
                                'pk_fk': pk_fk,
                                'allow_null': allow_null
                            })
                        k += 1
                    else:
                        # Empty row - check if next row is a new table
                        if k + 1 < len(df) and pd.notna(df.iloc[k + 1][0]):
                            next_val = str(df.iloc[k + 1][0]).strip()
                            if next_val and next_val not in ['Column Name', 'Timestamp update as of'] and not next_val.startswith('20'):
                                break
                        k += 1
                
                tables.append({
                    'name': table_name,
                    'description': description,
                    'columns': columns
                })
                i = k
                continue
    
    i += 1

# Write to markdown file
with open(output_file, 'w', encoding='utf-8') as f:
    for table in tables:
        f.write(f"## Table: {table['name']}\n\n")
        f.write(f"**Description:** {table['description']}\n\n")
        f.write("| Column Name | Data Type | Description | Example | PK/FK | Allow Null |\n")
        f.write("|-------------|-----------|-------------|---------|-------|------------|\n")
        
        for col in table['columns']:
            # Clean up multiline descriptions
            desc = col['description'].replace('\n', ' ').replace('|', '\\|')
            name = col['name'].replace('|', '\\|')
            data_type = col['data_type'].replace('|', '\\|')
            example = col['example'].replace('|', '\\|')
            pk_fk = col['pk_fk'].replace('|', '\\|')
            allow_null = col['allow_null'].replace('|', '\\|')
            f.write(f"| {name} | {data_type} | {desc} | {example} | {pk_fk} | {allow_null} |\n")
        
        f.write('\n')

print(f"Extracted {len(tables)} tables to {output_file}")
for t in tables:
    print(f"  - {t['name']} ({len(t['columns'])} columns)")
