import sys, os
sys.path.insert(0, 'backend')
from services.ingestion.loader import CSVLoader
from services.ingestion.transformers import transform_mapping_row

loader = CSVLoader(data_dir='data/atlas_dataset')
df = loader.load_csv('problem_company_mapping.csv')
print('Columns:', df.columns.tolist())
print('Total rows:', len(df))
print()

for i, row in df.iterrows():
    rd = transform_mapping_row(row)
    names = rd['company_names']
    prob = rd['problem_category']
    prob_short = prob[:40] if prob else None
    print(f'Row {i}: {len(names)} vendors | problem={prob_short}')
    for n in names:
        print(f'  - {repr(n)}')
