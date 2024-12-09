# schematic-schemers-csi3335
Web database application that plays the immaculate grid

# New Data Imports
All files used to update data are found in the directory 'data-insert-files'.

### Lahman 2023 Data:
 
- All new 2023 data found in the lahman csvs were imported using the python file 'data_insert.py'
- Exception: Parks table, where the 1 new park was added manually
- To add new 2023 data the user must run this script with the desired table to update as an argument
- Usage: `python3 data_insert.py <table_name>`

### Draft Data

- **New Table: Drafts, Updated Tables: People**
- All draft data used is from the MLB's stats api, which was then put in the csv 'mlb_draft_data.csv' located in the
directory 'additional_data/draft_data/'
- For example, https://statsapi.mlb.com/api/v1/draft/2023 will provide all data needed from the 2023 draft
- This was used to gather draft data from 1965, when the drafts began, to 2023
- Since this data does not use the same playerIDs as our database, python script 'add_player_id_to_drafts.py' was created
to match these players found in the new draft data with our players currently in the People table. If they were not in
the People table yet, a new playerID was created, and they were inserted into the table
- With all drafted players matched with a valid playerID, they were added to the csv 'mlb_draft_data_playerIDS.csv' located
in the directory 'additional_data/draft_data/'
- A new 'Drafts' table was created
- Finally, the user can add all draft data to the database using the same 'data_insert.py' script used before

### Negro League Data
- **Updated Tables: Leagues, Franchises, Appearances, Batting, Pitching, People, and Teams**
- All Negro League data used is from Sports Reference's StatHead website https://stathead.com/baseball/
- This website allowed us to filter and export data into csvs from the 7 recognized Negro Leagues (Negro American League, 
Negro National League II, East-West League, Negro Southern League, Negro National League I, American Negro League, 
Eastern Colored League)
- These csvs can be found in the 'data-insert-files/additional_data/NNL' directory
- The leagues themselves were inserted manually into the Leagues table
- Using these csvs and the 'nnl_data_insert.py' script, the Appearances, Batting, Pitching, People, and Teams tables can be updated to
include all recorded Negro League players and teams

### Wins Above Replacement Data
- **New Tables: SeasonWar, CareerWar**
- All WAR data used is from Sports Reference's StatHead website https://stathead.com/baseball/
- This website allowed us to filter and export data into csvs located in the 'data-insert-files/additional_data/WAR' directory
- SeasonWar and CareerWar are simple tables which map a player to their war in that season or in their career, where SeasonWar
includes an additional column 'yearID'
- Using these csvs alongside the 'data_insert.py' script, WAR data can be added to the SeasonWar and CareerWar tables 

### No Hitters Data
- **New Table: No_Hitters**
- This csv can be found in the 'data-insert-files/additional_data/no_hitters' directory
- Using this csv and the 'load_no_hitters.py' script, the user can create the No_Hitters table and insert the new rows
- No_Hitters contains important information for over 300 recorded No Hitters

### More Stats Data
- **New Table: League_Stats, Advanced_Stats**
- All data used for League Stats is from FanGraphs' website https://www.fangraphs.com/ and Baseball Reference's StatHead website https://stathead.com/baseball/,
alongside https://github.com/Neil-Paine-1/MLB-WAR-data-historical/blob/master/jeffbagwell_war_historical_2023.csv, which averages
these two website's data together
- This data was exported into csvs located in 'data-insert-files/addition_data/more_stats'
- League Stats provides more stats for leagues that are not found in the current Leagues table
- Advanced Stats provides more stats for players that are not found in the current Batting, Pitching, and Fielding tables

### Immaculate Grid Teams Data
- **New Table: ImmaculateGridTeams**
- All Immaculate Grid Teams data comes from https://www.immaculategrid.com/ when you click on a team for extra info
- This table simply maps all modern and active team names to every team immaculate grid considers as the same
- For example, Immaculate Grid considers today's "Baltimore Orioles" to be equivalent to the "St. Louis Browns" from 
1902-1953 and the "Milwaukee Brewers" from 1901-1901