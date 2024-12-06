import pandas as pd
import pymysql
import csi3335f2024 as cfg  # Replace with your config module

# Load the draft history CSV file
df = pd.read_csv("mlb_draft_data.csv" , encoding='latin-1')
df = df.replace({float("NaN"): None})

# Clean up player names to ensure consistent formatting
df['name_first'] = df['name_first'].str.strip()
df['name_last'] = df['name_last'].str.strip()

# Parse birth_date string into components
df['birth_year'] = df['birth_date'].str.slice(0, 4)
df['birth_month'] = df['birth_date'].str.slice(5, 7)
df['birth_day'] = df['birth_date'].str.slice(8, 10)

try:
    con = pymysql.connect(
        host=cfg.mysql['host'],
        user=cfg.mysql['user'],
        password=cfg.mysql['password'],
        database=cfg.mysql['database']
    )

    with con.cursor() as cursor:
        # Fetch all existing players
        cursor.execute("SELECT nameFirst, nameLast, birthYear, birthMonth, birthDay, playerID FROM people;")
        people = cursor.fetchall()

        # Create a dictionary of existing players for fast lookup
        people_dict = {
            (
                (person[0] or "").strip().lower(),
                (person[1] or "").strip().lower(),
                f"{int(person[2] or 0)}-{int(person[3] or 0):02d}-{int(person[4] or 0):02d}"
            ): person[5]
            for person in people
        }

    # Match playerIDs with draft history
    def find_player_id(row):
        key = (
            (row["name_first"] or "").strip().lower(),
            (row["name_last"] or "").strip().lower(),
            f"{int(row['birth_year'] or 0)}-{int(row['birth_month'] or 0):02d}-{int(row['birth_day'] or 0):02d}"
        )
        return people_dict.get(key)

    df["playerID"] = df.apply(find_player_id, axis=1)

    # Reorder columns to make playerID the leftmost column
    columns = ["playerID"] + [col for col in df.columns if col != "playerID"]
    df = df[columns]

    # Save the updated DataFrame to a new CSV file
    df.to_csv("drafts_with_playerID.csv", index=False)
    print(f"Draft file with playerID column")

except pymysql.MySQLError as e:
    print(f"Database error: {e}")

finally:
    if con:
        con.close()
        print("MySQL connection is closed.")
