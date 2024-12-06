import pandas as pd
import pymysql
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data-insert-files')))
import csi3335f2024 as cfg

file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

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
            print(sql)

            # Insert each row
            for index, row in df.iterrows():
                # year is stored in debut date instead
                if (isinstance(row['debut'], str) and row['debut'] >= '2023') or (row['debut'] is None):
                    cursor.execute(sql, row.to_list())

            con.commit()
            print("Data inserted successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        con.rollback()
    finally:
        con.close()

def insert_csv_to_db_halloffame_votedby(con, csv_file_path, table_name, columns, ignoreColumns):
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
            sql1 = """DELETE FROM halloffame WHERE votedBy LIKE '%Veterans%'"""
            sql2 = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

            cursor.execute(sql1)

            # Insert each row where player was voted by veterans
            count = 0
            for index, row in df.iterrows():
                if 'Veterans' in row['votedBy']:
                    count += 1
                    cursor.execute(sql2, row.to_list())

            con.commit()
            print("Data inserted successfully.")
            print(count)

    except Exception as e:
        print(f"An error occurred: {e}")
        con.rollback()
    finally:
        con.close()

def insert_csv_to_db_projWL(con, csv_file_path, table_name, columns, ignoreColumns):
    try:
        with con.cursor() as cursor:
            # Read the CSV file
            df = pd.read_csv(csv_file_path, encoding='latin-1')
            df = df.drop(columns=ignoreColumns)
            df = df.replace({float("NaN"): None})

            # Generate SQL statement
            sql = f"UPDATE {table_name} SET team_projW = %s, team_projL = %s WHERE yearID > 2022 AND teamID = %s"

            # Insert each row
            count = 0
            for index, row in df.iterrows():
                if row['yearID'] > 2022:
                    count += 1
                    projw = round((row['R']**1.81 / (row['R']**1.81 + row['RA']**1.81)) * row['G'])
                    projl = row['G'] - projw
                    cursor.execute(sql, [projw, projl, row['teamID']])

            con.commit()
            print("Data inserted successfully.")
            print(count)

    except Exception as e:
        print(f"An error occurred: {e}")
        con.rollback()
    finally:
        con.close()

def insert_csv_to_db_everything(con, csv_file_path, table_name, columns, ignoreColumns):
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
            count = 0
            for index, row in df.iterrows():
                count += 1
                cursor.execute(sql, row.to_list())

            con.commit()
            print("Data inserted successfully.")
            print(count)

    except Exception as e:
        print(f"An error occurred: {e}")
        con.rollback()
    finally:
        con.close()

def insert_csv_to_db(con, csv_file_path, table_name, columns, ignoreColumns):
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
                if row['yearID'] > 2022:
                    count += 1
                    cursor.execute(sql, row.to_list())

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
folder = 'lahman_1871-2023_csv/'

# People
if arg == 'People' or arg == 'all':
    file = folder + 'People.csv'
    table = 'people'
    columns = ['playerID', 'birthYear', 'birthMonth', 'birthDay', 'birthCity', 'birthCountry', 'birthState',
               'deathYear', 'deathMonth', 'deathDay', 'deathCountry', 'deathState', 'deathCity', 'nameFirst',
               'nameLast', 'nameGiven', 'weight', 'height', 'bats', 'throws', 'debutDate', 'finalGameDate']
    ignoreColumns = ['ID', 'bbrefID', 'retroID']
    insert_csv_to_db_people(con, file, table, columns, ignoreColumns)

# AllstarFull
if arg == 'AllStarFull' or arg == 'all':
    file = folder + 'AllStarFull.csv'
    table = 'AllStarFull'
    columns = ['playerID', 'yearID', 'gameID', 'teamID', 'lgID', 'GP', 'startingPos']
    ignoreColumns = ['gameNum']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# Appearances
if arg == 'Appearances' or arg == 'all':
    file = folder + 'Appearances.csv'
    table = 'Appearances'
    columns = ['yearID','teamID','playerID','G_all','GS','G_batting','G_defense','G_p','G_c','G_1b','G_2b',
               'G_3b','G_ss','G_lf','G_cf','G_rf','G_of','G_dh','G_ph','G_pr']
    ignoreColumns = ['lgID']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# Awards (Might need to create entirely new table)
if arg == 'Awards' or arg == 'all':
    file = folder + 'Appearances.csv'
    table = 'AwardsManagers'
    columns = ['playerID','awardID','yearID','lgID','tie','notes']
    ignoreColumns = []
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

    # No Platinum Glove
    # Reliever of the Year, TSN Reliever of the Year doesn't go far back enough
    # BBWAA Needs newest info from 2017-2023

# Batting
if arg == 'Batting' or arg == 'all':
    file = folder + 'Batting.csv'
    table = 'Batting'
    columns = ['playerID','yearID','stint','teamID','b_G','b_AB','b_R','b_H','b_2B','b_3B','b_HR','b_RBI','b_SB','b_CS',
               'b_BB','b_SO','b_IBB','b_HBP','b_SH','b_SF','b_GIDP']
    ignoreColumns = ['G_old', 'G_batting', 'lgID']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# Batting
if arg == 'BattingPost' or arg == 'all':
    file = folder + 'BattingPost.csv'
    table = 'BattingPost'
    columns = ['yearID','round','playerID','teamID','b_G','b_AB','b_R','b_H','b_2B','b_3B','b_HR','b_RBI','b_SB','b_CS',
               'b_BB','b_SO','b_IBB','b_HBP','b_SH','b_SF','b_GIDP']
    ignoreColumns = ['lgID']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# Fielding
if arg == 'Fielding' or arg == 'all':
    file = folder + 'Fielding.csv'
    table = 'Fielding'
    columns = ['playerID','yearID','stint','teamID','position','f_G','f_GS','f_InnOuts','f_PO','f_A','f_E','f_DP','f_PB',
               'f_WP','f_SB','f_CS','f_ZR']
    ignoreColumns = ['lgID']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# FieldingPost
if arg == 'FieldingPost' or arg == 'all':
    file = folder + 'FieldingPost.csv'
    table = 'FieldingPost'
    columns = ['playerID','yearID','teamID','round','position','f_G','f_GS','f_InnOuts','f_PO','f_A','f_E','f_DP',
               'f_TP','f_PB']
    ignoreColumns = ['lgID', 'SB', 'CS']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# HallOfFame
if arg == 'HallOfFame' or arg == 'all':
    file = folder + 'HallOfFame.csv'
    table = 'HallOfFame'
    columns = ['playerID','yearID','votedBy','ballots','needed','votes','inducted','category','note']
    ignoreColumns = []
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

    # Replaces "Veterans" with more specific title
    # Had to alter HallOfFame attribute "notes" to account for longer notes (300 chars)
    insert_csv_to_db_halloffame_votedby(con, file, table, columns, ignoreColumns)

# Manually added 1 new Park

# HomeGames (Had to change yearID to yearkey in function)
if arg == 'HomeGames' or arg == 'all':
    file = folder + 'HomeGames.csv'
    table = 'HomeGames'
    columns = ['yearID','teamID','parkID','firstGame','lastGame','games','openings','attendance']
    ignoreColumns = ['leaguekey']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# Managers
if arg == 'Managers' or arg == 'all':
    file = folder + 'Managers.csv'
    table = 'Managers'
    columns = ['playerID','yearID','teamID','inSeason','manager_G','manager_W','manager_L','teamRank','plyrMgr']
    ignoreColumns = ['lgID']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# Pitching
if arg == 'Pitching' or arg == 'all':
    file = folder + 'Pitching.csv'
    table = 'Pitching'
    columns = ['playerID','yearID','stint','teamID','p_W','p_L','p_G','p_GS','p_CG','p_SHO','p_SV','p_IPouts',
               'p_H','p_ER','p_HR','p_BB','p_SO','p_BAOpp','p_ERA','p_IBB','p_WP','p_HBP','p_BK','p_BFP','p_GF','p_R',
               'p_SH','p_SF','p_GIDP']
    ignoreColumns = ['lgID']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# PitchingPost
if arg == 'PitchingPost' or arg == 'all':
    file = folder + 'PitchingPost.csv'
    table = 'PitchingPost'
    columns = ['playerID','yearID','round','teamID','p_W','p_L','p_G','p_GS','p_CG','p_SHO','p_SV','p_IPouts',
               'p_H','p_ER','p_HR','p_BB','p_SO','p_BAOpp','p_ERA','p_IBB','p_WP','p_HBP','p_BK','p_BFP','p_GF','p_R',
               'p_SH','p_SF','p_GIDP']
    ignoreColumns = ['lgID']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# SeriesPost
if arg == 'SeriesPost' or arg == 'all':
    file = folder + 'SeriesPost.csv'
    table = 'SeriesPost'
    columns = ['yearID','round','teamIDwinner','teamIDloser','wins','losses','ties']
    ignoreColumns = ['lgIDloser','lgIDwinner']
    insert_csv_to_db(con, file, table, columns, ignoreColumns)

# Teams
if arg == 'Teams' or arg == 'all':
    file = folder + 'Teams.csv'
    table = 'Teams'
    columns = ['yearID','lgID','teamID','franchID','divID','team_rank','team_G','team_G_home','team_W','team_L',
               'DivWin','WCWin','LgWin','WSWin','team_R','team_AB','team_H','team_2B','team_3B','team_HR','team_BB',
               'team_SO','team_SB','team_CS','team_HBP','team_SF','team_RA','team_ER','team_ERA','team_CG','team_SHO',
               'team_SV','team_IPouts','team_HA','team_HRA','team_BBA','team_SOA','team_E','team_DP','team_FP',
               'team_name','park_name','team_attendance','team_BPF','team_PPF']
    ignoreColumns = ['teamIDBR','teamIDlahman45','teamIDretro']
    # insert_csv_to_db(con, file, table, columns, ignoreColumns)

    # Need to calculate projected wins/losses
    insert_csv_to_db_projWL(con, file, table, columns, ignoreColumns)

# Drafts
if arg == 'Drafts' or arg == 'all':
    file = 'additional_data/draft_data/mlb_draft_data_playerIDs.csv'
    table = 'Drafts'
    columns = ['playerID','draftYear','draftRound','draftPick']
    ignoreColumns = ['id','name_first','name_last','name_given','team_name','school_name','birth_date','birth_city','birth_country','birth_state','weight','birth_year','birth_month','birth_day']
    insert_csv_to_db_everything(con, file, table, columns, ignoreColumns)

# CareerWAR
if arg == 'CareerWar' or arg == 'all':
    file = file_path + 'additional_data/WAR/career_war.csv'
    table = 'CareerWar'
    columns = ['war', 'playerID']
    ignoreColumns = ['Rk','Player']
    insert_csv_to_db_everything(con, file, table, columns, ignoreColumns)

# SeasonWAR
if arg == 'SeasonWar' or arg == 'all':
    file = 'additional_data/WAR/season_war.csv'
    table = 'CareerWar'
    columns = ['war', 'yearID', 'playerID']
    ignoreColumns = ['Rk','Player']
    insert_csv_to_db_everything(con, file, table, columns, ignoreColumns)