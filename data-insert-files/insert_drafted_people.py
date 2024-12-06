import pandas as pd
import pymysql
import csi3335f2024 as cfg

# Load the draft history CSV file
draft_history_file = "mlb_draft_data.csv"  # Replace with your file path
df = pd.read_csv(draft_history_file, encoding='latin-1')
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
        database=cfg.mysql['database'])

    with con.cursor() as cursor:
        # Fetch all existing people
        cursor.execute("SELECT nameFirst, nameLast, birthYear, birthMonth, birthDay, playerID FROM people;")
        people = cursor.fetchall()

        # Create a set of existing players for fast lookup
        existing_players = set(
            (
                (person[0] or "").strip().lower(),  # nameFirst (handle None)
                (person[1] or "").strip().lower(),  # nameLast (handle None)
                f"{int(person[2] or 0)}-{int(person[3] or 0):02d}-{int(person[4] or 0):02d}",  # birthYear-birthMonth-birthDay
            )
            for person in people
        )

        # Determine counts of current playerIDs
        player_id_counts = {}
        for person in people:
            player_id_counts[person[5][:-2]] = player_id_counts.get(person[5][:-2], 0) + 1

        # Prepare new player rows for insertion
        new_players = []
        players_in_csv = set()
        for _, row in df.iterrows():
            first_name, last_name = row['name_first'], row['name_last']
            name_given = row['name_given']
            birth_year, birth_month, birth_day = row['birth_year'], row['birth_month'], row['birth_day']
            weight = row.get('weight')  # Default to None if not present
            birth_country = row.get('birth_country')  # Default to None if not present
            birth_state = row.get('birth_state')  # Default to None if not present
            birth_city = row.get('birth_city')  # Default to None if not present
            key = ((first_name or "").lower(), (last_name or "").lower(), f"{int(birth_year or 0)}-{int(birth_month or 0):02d}-{int(birth_day or 0):02d}")

            if (key not in existing_players) and (str(key) not in players_in_csv):
                # Generate playerID
                if first_name or last_name:
                    base_id = f"{(last_name or "")[:5].lower():<5}{(first_name or "")[:2].lower():<2}".replace(' ', '')
                    player_count = player_id_counts.get(base_id, 0) + 1
                    player_id_counts[base_id] = player_count
                    player_id = f"{base_id}{player_count:02d}"

                    # Prepare the row for insertion
                    new_players.append((
                        player_id,  # playerID
                        first_name,  # nameFirst
                        last_name,  # nameLast
                        name_given,  # nameGiven
                        birth_year,  # birthYear
                        birth_month,  # birthMonth
                        birth_day,  # birthDay
                        birth_country,  # birthCountry
                        birth_state,  # birthState
                        birth_city,  # birthCity
                        None, None, None,  # deathYear, deathMonth, deathDay
                        None, None, None,  # deathCountry, deathState, deathCity
                        weight,  # weight
                        None,  # height (always NULL now)
                        None,  # bats
                        None,  # throws
                        None,  # debutDate
                        None  # finalGameDate
                    ))
            # Prevent players in multiple drafts from being added twice
            players_in_csv.add(str(key))

        # Insert new players into the database
        if new_players:
            insert_query = """
                INSERT IGNORE INTO people (
                    playerID, nameFirst, nameLast, nameGiven,
                    birthYear, birthMonth, birthDay,
                    birthCountry, birthState, birthCity,
                    deathYear, deathMonth, deathDay,
                    deathCountry, deathState, deathCity,
                    weight, height, bats, throws, debutDate, finalGameDate
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.executemany(insert_query, new_players)
            con.commit()
            print(f"Inserted {len(new_players)} new players into the 'people' table.")
        else:
            print("No new players to add.")

except pymysql.MySQLError as e:
    print(f"Error: {e}")

finally:
    if con:
        con.close()
        print("MySQL connection is closed.")
