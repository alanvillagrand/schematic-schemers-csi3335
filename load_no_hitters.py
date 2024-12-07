from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:csi3335rocks@localhost/baseball_updated')

csv_file_path = 'no_hitters.csv'
df = pd.read_csv(csv_file_path)

df.insert(0, 'no_hitters_ID', range(1, len(df) + 1))

table_name = 'no_hitters'
df.to_sql(table_name, con=engine, if_exists='replace', index=False)

print(f"Data from {csv_file_path} has been successfully inserted into the {table_name} table.")