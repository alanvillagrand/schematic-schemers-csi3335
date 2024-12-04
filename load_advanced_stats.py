from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:csi3335rocks@localhost/baseball_updated')

csv_file_path = 'advanced_stats.csv'
df = pd.read_csv(csv_file_path)

df.insert(0, 'advanced_stats_ID', range(1, len(df) + 1))

table_name = 'advanced_stats'
df.to_sql(table_name, con=engine, if_exists='replace', index=False)

print(f"Data from {csv_file_path} has been successfully inserted into the {table_name} table.")