from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://jakemauldin:password@localhost/baseball_test')

csv_file_path = 'league_stats_sorted.csv'
df = pd.read_csv(csv_file_path)

table_name = 'league_stats'
df.to_sql(table_name, con=engine, if_exists='replace', index=False)

print(f"Data from {csv_file_path} has been successfully inserted into the {table_name} table.")