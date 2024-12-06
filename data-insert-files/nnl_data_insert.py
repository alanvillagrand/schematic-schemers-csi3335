import pandas as pd
import pymysql
import csi3335f2024 as cfg
import nls_teams as nls
import sys

# Separate function for people table since it requires more specific parameters
def insert_csv_to_db_people(con, csv_file_path, table_name, columns, ignoreColumns):
    try:
        with con.cursor() as cursor:
            # Set columns and placeholders for prepared statement
            cols = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            # Read the CSV file
            df = pd.read_csv(csv_file_path, encoding='latin-1')
            df = df.drop(columns=ignoreColumns)
            df = df.replace({float("NaN"): None})

            # Generate SQL statement
            sql = f"INSERT IGNORE INTO {table_name} ({cols}) VALUES ({placeholders})"

            # Insert each row
            player_ids = set()
            count = 0
            for index, row in df.iterrows():
                if row['Player-additional'] not in player_ids:
                    count += 1
                    name = row['Player'].split()
                    name_first = name[0]
                    name_last = name[-1] if len(name) > 1 else ""
                    cursor.execute(sql, [name_first, name_last, row['Player'], row['Player-additional']])

                    player_ids.add(row['Player-additional'])


            con.commit()
            print("Data inserted successfully.")
            print(count)

    except Exception as e:
        print(f"An error occurred: {e}")
        con.rollback()
    finally:
        con.close()


def insert_csv_to_db_teams(con, csv_file_path_1, csv_file_path_2, table_name, columns_batting, columns_pitching,
                           ignoreColumns_batting, ignoreColumns_pitching):
    try:
        with con.cursor() as cursor:
            # Set columns and placeholders for prepared statement
            columns = columns_batting + columns_pitching
            cols = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            # Read the batting CSV file
            batting_df = pd.read_csv(csv_file_path_1, encoding='latin-1')
            batting_df = batting_df.drop(columns=ignoreColumns_batting)
            batting_df = batting_df.replace({float("NaN"): None})

            # Read the batting CSV file
            pitching_df = pd.read_csv(csv_file_path_2, encoding='latin-1')
            pitching_df = pitching_df.drop(columns=ignoreColumns_pitching)
            pitching_df = pitching_df.replace({float("NaN"): None})

            # Generate SQL statement
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

            # Insert each row
            count = 0
            for (index, row_b), (index, row_p) in zip(batting_df.iterrows(), pitching_df.iterrows()):
                count += 1
                team = row_b['Team']
                team = team[:2] if team[:2] in nls.teams else team[:3]
                row_b['Lg'] = row_b['Lg'][:3]

                # Change to correct franchise ID
                franch_id = team
                if franch_id == 'BRG': franch_id = 'BGI'
                if franch_id == 'CLS': franch_id = 'CST'
                if franch_id == 'HAR' or franch_id == 'SNS' or franch_id == 'SL3' or franch_id == 'AB3':
                    franch_id = 'SOH'
                if franch_id == 'CC': franch_id = 'IC'
                if franch_id == 'CCB': franch_id = 'CBE'
                if franch_id == 'CBR': franch_id = 'JRC'
                if franch_id == 'BCA': franch_id = 'IAB'
                if franch_id == 'PC': franch_id = 'TC'
                if franch_id == 'WEG' or franch_id == 'CEG':
                    franch_id = 'BEG'
                if franch_id == 'BE': franch_id = 'NE'
                if franch_id == 'AB2': franch_id = 'ID'
                if franch_id == 'LOW': franch_id = 'LVB'
                if franch_id == 'DM': franch_id = 'DYM'
                if franch_id == 'WP': franch_id = 'WMP'
                if franch_id == 'CS': franch_id = 'CSW'
                if franch_id == 'SLG': franch_id = 'SLS'

                row_p['IP'] = (row_p['IP'] or 0) / 3

                rows = row_b.to_list() + row_p.to_list()
                rows.insert(2, nls.teams[franch_id])
                rows.insert(3, franch_id)

                cursor.execute(sql, rows)

            con.commit()
            print("Data inserted successfully.")
            print(count)

    except Exception as e:
        print(f"An error occurred: {e}")
        con.rollback()
    finally:
        con.close()


def insert_csv_to_db_bpf(con, csv_file_path, table_name, columns, ignoreColumns):
    try:
        with con.cursor() as cursor:
            # Set columns and placeholders for prepared statement
            cols = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            # Read the CSV file
            df = pd.read_csv(csv_file_path, encoding='latin-1')
            df = df.drop(columns=ignoreColumns)
            df = df.replace({float("NaN"): None})

            # Generate SQL statement
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

            # Insert each row
            count = 0
            for index, row in df.iterrows():
                count += 1

                team = row['Team']
                row['Team'] = team[:2] if team[:2] in nls.teams else team[:3]

                if 'IP' in row:
                    row['IP'] = (row['IP'] or 0) / 3

                rows = row.to_list()
                rows.append(1)

                cursor.execute(sql, rows)

            con.commit()
            print("Data inserted successfully.")
            print(count)

    except Exception as e:
        print(f"An error occurred: {e}")
        con.rollback()
    finally:
        con.close()


# Main program
arg = sys.argv[1]

# Connect to the database
con = pymysql.connect(host=cfg.mysql['host'],
                      user=cfg.mysql['user'],
                      password=cfg.mysql['password'],
                      database=cfg.mysql['database'])

folder = 'additional_data/NNL/'


# People
if arg == 'People' or arg == 'all':
    file = folder + 'nls_batting.csv'
    table = 'People'
    columns = ['nameFirst','nameLast','nameGiven','playerID']
    ignoreColumns = ['Rk','HR','Season','Age','Team','Lg','G','PA','AB','R','H','1B','2B','3B','HR','RBI','SB','CS',
                     'BB','SO','BA','OBP','SLG','OPS','OPS+','TB','GIDP','HBP','SH','SF','IBB','Pos']
    insert_csv_to_db_people(con, file, table, columns, ignoreColumns)

# Teams
if arg == 'Teams' or arg == 'all':
    table = 'Teams'
    # Team Batting
    file_1 = folder + 'nls_teams_batting.csv'
    columns_1 = ['yearID', 'teamID', 'team_name', 'franchID', 'lgID', 'team_G', 'team_W', 'team_L', 'team_AB', 'team_R', 'team_H',
                 'team_2B','team_3B','team_HR', 'team_SB', 'team_CS', 'team_BB', 'team_SO','team_SF']
    ignoreColumns_1 = ['Rk','IBB','R/Gm','GIDP','HBP','OPS','OPS+','SLG','OBP','LOB','SH','RBI','1B','PA', 'BA','Bat#','WL%',
                       'TB']

    # Team pitching
    file_2 = folder + 'nls_teams_pitching.csv'
    columns_2 = ['team_ERA','team_CG','team_SHO','team_SV','team_IPouts','team_HA','team_RA','team_E','team_HRA',
                 'team_BBA','team_SOA','team_HBP','team_FP']
    ignoreColumns_2 = ['Rk','GP','W','L','Rk','G','Season','Team','Lg','WHIP','H9','HR9','BB9','SO9','SO/BB','ERA+','BK',
                       'WL%','WP','BF', 'IBB']
    insert_csv_to_db_teams(con, file_1, file_2, table, columns_1, columns_2, ignoreColumns_1, ignoreColumns_2)

# Batting
if arg == 'Batting' or arg == 'all':
    file = folder + 'nls_batting.csv'
    table = 'Batting'
    columns = ['b_HR','yearID','teamID','b_G','b_AB','b_R','b_H','b_2B','b_3B','b_RBI','b_SB','b_CS','b_BB','b_SO',
               'b_GIDP','b_HBP','b_SH','b_SF','b_IBB','playerID','stint']
    ignoreColumns = ['Rk','Player','Age','Lg','Pos','SLG','BA','OBP','OPS','OPS+','TB','PA','1B','HR.1']
    insert_csv_to_db_bpf(con, file, table, columns, ignoreColumns)

# Pitching
if arg == 'Pitching' or arg == 'all':
    file = folder + 'nls_pitching.csv'
    table = 'Pitching'
    columns = ['yearID','teamID','p_W','p_L','p_ERA','p_G','p_GS','p_CG','p_SHO','p_SV','p_IPOuts','p_H','p_R','p_ER',
               'p_HR','p_BB','p_IBB','p_SO','p_HBP','p_BK','p_WP','p_BFP','playerID','stint']
    ignoreColumns = ['Rk','Player','Age','Lg','W-L%','Dec','ERA+','FIP','WHIP','H9','HR9','BB9','SO9','SO/BB','Pos']
    insert_csv_to_db_bpf(con, file, table, columns, ignoreColumns)