from flask import Blueprint, request, render_template

from app.services.immaculateGridQueries import get_players_team_team, get_players_careerBattingAVG_team, \
    get_players_careerStatBatting_team, get_players_careerStatPitching_team, get_players_seasonStatBatting_team, \
    get_players_seasonStatPitching_team, get_players_seasonBattingAVG_team, get_players_seasonBatting3030_team, \
    get_players_stdAward_team, get_players_hof_team, get_players_allstar_team, get_players_ws_team, \
    get_players_position_team, get_players_careerStatBatting_careerStatBatting, \
    get_players_careerStatPitching_careerStatPitching, get_players_careerStatBatting_careerStatPitching, \
    get_players_careerBattingAVG_careerStatBatting, get_players_careerBattingAVG_careerStatPitching, \
    get_players_careerPitchingERA_careerStatPitching, get_players_careerPitchingERA_careerStatBatting, \
    get_players_careerPitchingERA_careerStatAVG, get_players_careerStatBatting_seasonStatBatting, \
    get_players_careerStatBatting_seasonPitchingERA, get_players_careerStatPitching_seasonPitchingERA, \
    get_players_careerStatBatting_seasonStatPitching, get_players_careerStatPitching_seasonStatBatting, \
    get_players_careerStatPitching_seasonStatPitching, get_players_careerPitchingERA_seasonStatPitching, \
    get_players_careerPitchingERA_seasonStatBatting, get_players_careerPitchingERA_seasonPitchingERA, \
    get_players_careerPitchingERA_seasonStatAVG, get_players_careerPitchingERA_seasonBatting3030, \
    get_players_careerBattingAVG_seasonStatBatting, get_players_careerBattingAVG_seasonBatting3030, \
    get_players_careerBattingAVG_seasonBattingAVG, get_players_careerBattingAVG_seasonPitchingERA, \
    get_players_careerBattingAVG_seasonStatPitching, get_players_careerStatBatting_seasonBattingAVG, \
    get_players_careerStatPitching_seasonBattingAVG, get_players_careerStatBatting_seasonBatting3030, \
    get_players_careerStatPitching_seasonBatting3030, get_players_careerStatPitching_hof, \
    get_players_careerStatBatting_hof, get_players_careerStatPitching_allStar, get_players_careerStatBatting_allStar, \
    get_players_careerStatPitching_stdAward, get_players_careerStatBatting_stdAward, \
    get_players_careerBattingAVG_stdAward, get_players_careerBattingAVG_allStar, get_players_careerBattingAVG_hof, \
    get_players_careerPitchingERA_hof, get_players_careerPitchingERA_allStar, get_players_careerPitchingERA_stdAward, \
    get_players_careerBattingAVG_position, get_players_careerStatBatting_position, \
    get_players_careerStatPitching_position, get_players_careerPitchingERA_position, get_players_careerStatPitching_pob, \
    get_players_careerStatBatting_pob, get_players_careerBattingAVG_pob, get_players_careerPitchingERA_pob, \
    get_players_careerStatPitching_country, get_players_careerStatBatting_country, get_players_careerBattingAVG_country, \
    get_players_careerPitchingERA_country, get_players_careerStatBatting_draftPick, \
    get_players_careerStatPitching_draftPick, get_players_careerBattingAVG_draftPick, \
    get_players_careerPitchingERA_draftPick, get_players_seasonStatBatting_seasonStatBatting, \
    get_players_seasonStatPitching_seasonStatPitching, get_players_seasonStatPitching_seasonStatBatting, \
    get_players_seasonStatPitching_seasonStatAVG, get_players_seasonStatBatting_seasonStatAVG, \
    get_players_seasonBatting3030_seasonStatAVG, get_players_seasonPitchingERA_seasonStatAVG, \
    get_players_seasonPitchingERA_seasonBatting3030, get_players_seasonStatBatting3030_seasonStatBatting, \
    get_players_seasonStatBatting3030_seasonStatPitching, get_players_seasonPitchingERA_seasonStatPitching, \
    get_players_seasonPitchingERA_seasonStatBatting, get_players_seasonStatBatting_stdAward, \
    get_players_seasonStatPitching_stdAward, get_players_seasonStatBatting_ws, get_players_seasonStatBatting_allStar, \
    get_players_seasonStatPitching_allStar, get_players_seasonBattingAVG_stdAward, get_players_seasonBattingAVG_allStar, \
    get_players_seasonBattingAVG_hof, get_players_seasonStatBatting_hof, get_players_seasonStatPitching_hof, \
    get_players_seasonStatERA_stdAward, get_players_seasonStatERA_allStar, get_players_seasonStatERA_hof, \
    get_players_seasonBatting3030_stdAward, get_players_seasonBatting3030_hof, get_players_seasonBatting3030_allStar, \
    get_players_seasonWAR_hof, get_players_seasonStatBatting_position, get_players_seasonStatPitching_position, \
    get_players_seasonPitchingERA_position, get_players_seasonBattingAVG_position, \
    get_players_seasonBatting3030_position, get_players_seasonWAR_position, get_players_seasonStatBatting_pob, \
    get_players_seasonStatPitching_pob, get_players_seasonPitchingERA_pob, get_players_seasonBattingAVG_pob, \
    get_players_seasonBatting3030_pob, get_players_seasonStatBatting_country, get_players_seasonStatPitching_country, \
    get_players_seasonBattingAVG_country, get_players_seasonPitchingERA_country, get_players_seasonBatting3030_country, \
    get_players_draftPick_seasonStatPitching, get_players_draftPick_seasonStatBatting, \
    get_players_draftPick_seasonBattingAVG, get_players_draftPick_seasonPitchingERA, \
    get_players_draftPick_seasonBatting3030, get_players_stdAward_stdAward, get_players_allStar_hof, \
    get_players_hof_stdAward, get_players_allStar_stdAward, get_players_pob_hof, get_players_pob_allStar, \
    get_players_pob_stdAward, get_players_country_stdAward, get_players_country_hof, get_players_country_allStar, \
    get_players_draftPick_hof, get_players_draftPick_allStar, get_players_draftPick_stdAward, \
    get_players_position_position, get_players_pob_position, get_players_country_position, \
    get_players_draftPick_country, get_players_draftPick_pob, get_players_draftPick_position, \
    get_players_stdAward_position, get_players_hof_position, get_players_allstar_position, \
    get_players_careerPitchingERA_team, get_players_exclusive_to_team, get_players_seasonPitchingERA_team, \
    get_players_pob_team, get_players_careerStatWAR_team, get_players_seasonStatWAR_team, get_players_hof_onlyOneTeam, \
    get_players_allStar_onlyOneTeam, get_players_stdAward_onlyOneTeam, get_players_careerBattingAVG_onlyOneTeam, \
    get_players_careerStatBatting_onlyOneTeam, get_players_careerStatPitching_onlyOneTeam, \
    get_players_careerPitchingERA_onlyOneTeam, get_players_careerStatWAR_onlyOneTeam, get_players_position_onlyOneTeam, \
    get_players_country_team, get_players_pob_onlyOneTeam, get_players_country_onlyOneTeam, \
    get_players_seasonStatBatting_onlyOneTeam, get_players_seasonStatPitching_onlyOneTeam, \
    get_players_seasonBattingAVG_onlyOneTeam, get_players_seasonBatting3030_onlyOneTeam, \
    get_players_seasonPitchingERA_onlyOneTeam, get_players_careerPitchingERA_careerStatWAR, \
    get_players_careerBattingAVG_careerStatWAR, get_players_careerStatWAR_careerStatPitching, \
    get_players_careerStatWAR_careerStatBatting, get_players_careerStatWAR_seasonBatting3030, \
    get_players_careerStatWAR_seasonBattingAVG, get_players_careerStatWAR_seasonPitchingERA, \
    get_players_careerStatWAR_seasonStatPitching, get_players_careerStatWAR_seasonStatBatting

bp = Blueprint('search', __name__)



@bp.route('/search_players', methods=['POST'])
def search_players():
    standard_seasonStatBatting = [
        "HR",
        "RBI",
        "R",
        "H",
        "SB"
    ]
    standard_careerStatBatting = [
        "HR",
        "H"
    ]

    standard_seasonStatPitching = [
        "SV",
        "W",
        "SO"
    ]
    standard_careerStatPitching = [
        "SV",
        "W",
        "SO"
    ]

    standard_awards = [
        "Gold Glove",
        "Cy Young Award",
        "Silver Slugger",
        "Rookie of the Year",
        "Most Valuable Player",
    ]

    def convert_to_number(value):
        value = value.replace('+', '')  # Remove the '+' if it exists
        try:
            if '.' in value:
                return float(value)  # Convert to float if it contains a decimal point
            return int(value)  # Otherwise, convert to int
        except ValueError:
            raise ValueError(f"Invalid number format: {value}")

    # Extract dropdown values
    option1 = request.form.get('option1')
    option1_details = request.form.get('dropdown1_details')
    option2 = request.form.get('option2')
    option2_details = request.form.get('dropdown2_details')

    # Validate input
    if not option1 or not option2:
        return "Please select an option from both dropdowns.", 400

    results = []



    if option1 == "teams" and option2 == "teams":
        # Query players who played on both selected teams
        if option1_details != "Only One Team" and option2_details != "Only One Team":
            results = get_players_team_team(option1_details, option2_details)

        elif option1_details == "Only One Team":
            results = get_players_exclusive_to_team(option2_details)
        else:
            results = get_players_exclusive_to_team(option1_details)

    elif (option1 == "career statistic" and option2 == "teams") or (option1 == "teams" and option2 == "career statistic"):
        print("IN TEAMS CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        team = option2_details if option1 == "career statistic" else option1_details
        stat_range = request.form.get(f'dropdown2_{career_stat}_specific') if option1 == "teams" else request.form.get(
            f'dropdown1_{career_stat}_specific')
        if career_stat != "ERA":
            stat_range = convert_to_number(stat_range)

        # Handling different career statistics based on user input
        if career_stat == "AVG" and team != "Only One Team":
            results = get_players_careerBattingAVG_team(stat_range, team)
        elif career_stat in standard_careerStatBatting and team != "Only One Team":
            results = get_players_careerStatBatting_team(career_stat, team, stat_range)
        elif career_stat in standard_careerStatPitching and team != "Only One Team":
            results = get_players_careerStatPitching_team(career_stat, team, stat_range)
        elif career_stat == "ERA" and team != "Only One Team":
            results = get_players_careerPitchingERA_team(team)
        elif career_stat == "WAR" and team != "Only One Team":
            results = get_players_careerStatWAR_team(team, stat_range)

        elif career_stat == "AVG" and team == "Only One Team":
            results = get_players_careerBattingAVG_onlyOneTeam(stat_range)
        elif career_stat in standard_careerStatBatting and team == "Only One Team":
            results = get_players_careerStatBatting_onlyOneTeam(career_stat, stat_range)
        elif career_stat in standard_careerStatPitching and team == "Only One Team":
            results = get_players_careerStatPitching_onlyOneTeam(career_stat, stat_range)
        elif career_stat == "ERA" and team == "Only One Team":
            results = get_players_careerPitchingERA_onlyOneTeam()
        elif career_stat == "WAR" and team == "Only One Team":
            results = get_players_careerStatWAR_onlyOneTeam(stat_range)




    elif (option1 == "teams" and option2 == "seasonal statistic") or (option1 == "seasonal statistic" and option2 == "teams"):
        if option1 == "teams":
            team = option1_details
            stat = option2_details
        else:
            team = option2_details
            stat = option1_details

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "teams" else request.form.get(
            f'dropdown1_{stat}_specific')

        if stat != "ERA" and stat != "30+HR/30+SB":
            stat_range = convert_to_number(stat_range)

        if stat in standard_seasonStatBatting and team != "Only One Team":
            results = get_players_seasonStatBatting_team(stat, team, stat_range)

        elif stat in standard_seasonStatPitching and team != "Only One Team":
            results = get_players_seasonStatPitching_team(stat, team, stat_range)

        elif stat == "AVG" and team != "Only One Team":
            results = get_players_seasonBattingAVG_team(stat_range, team)

        elif stat == "30+HR/30+SB" and team != "Only One Team":
            results = get_players_seasonBatting3030_team(team)

        elif stat == "ERA" and team != "Only One Team":
            results = get_players_seasonPitchingERA_team(team)

        elif stat == "WAR" and team != "Only One Team":
            results = get_players_seasonStatWAR_team(team, stat_range)

        elif stat in standard_seasonStatBatting and team == "Only One Team":
            results = get_players_seasonStatBatting_onlyOneTeam(stat, stat_range)

        elif stat in standard_seasonStatPitching and team == "Only One Team":
            results = get_players_seasonStatPitching_onlyOneTeam(stat, stat_range)

        elif stat == "AVG" and team == "Only One Team":
            results = get_players_seasonBattingAVG_onlyOneTeam(stat_range)

        elif stat == "30+HR/30+SB" and team == "Only One Team":
            results = get_players_seasonBatting3030_onlyOneTeam()

        elif stat == "ERA" and team == "Only One Team":
            results = get_players_seasonPitchingERA_onlyOneTeam()





    elif (option1 == "awards" and option2 == "teams") or (option1 == "teams" and option2 == "awards"):
        # Extract the award and team details
        award = option1_details if option1 == "awards" else option2_details
        team = option1_details if option1 == "teams" else option2_details

        if award in standard_awards and team != "Only One Team":
            results = get_players_stdAward_team(award, team)

        elif award == "Hall of Fame" and team != "Only One Team":
            results = get_players_hof_team(team)

        elif award == "All Star" and team != "Only One Team":
            results = get_players_allstar_team(team)

        elif award == "World Series" and team != "Only One Team":
            results = get_players_ws_team(team)

        elif award == "Hall of Fame" and team == "Only One Team":
            results = get_players_hof_onlyOneTeam()

        elif award == "All Star" and team == "Only One Team":
            results = get_players_allStar_onlyOneTeam()

        elif award in standard_awards and team == "Only One Team":
            results = get_players_stdAward_onlyOneTeam(award)



    elif (option1 == "positions" and option2 == "teams") or (option1 == "teams" and option2 == "positions"):
        # Extract the position and team details
        position = option1_details if option1 == "positions" else option2_details
        team = option1_details if option1 == "teams" else option2_details
        if team != "Only One Team":
            results = get_players_position_team(position, team)
        else:
            results = get_players_position_onlyOneTeam(position)

    elif (option1 == "pob" and option2 == "teams") or (option1 == "teams" and option2 == "pob"):
        team= option1_details if option1 == "teams" else option2_details
        pob= option1_details if option1 == "pob" else option2_details
        if pob == "Outside of USA" and team != "Only One Team":
            results = get_players_pob_team(team)
        elif pob != "Outside of USA" and team != "Only One Team":
            results = get_players_country_team(team, pob)
        elif pob == "Outside of USA" and team == "Only One Team":
            results = get_players_pob_onlyOneTeam()
        elif pob != "Outside of USA" and team == "Only One Team":
            results = get_players_country_onlyOneTeam(pob)



    elif option1 == "career statistic" and option2 == "career statistic":
        stat1 = option1_details
        stat2 = option2_details
        stat_range1 = request.form.get(f'dropdown1_{stat1}_specific')
        stat_range2 = request.form.get(f'dropdown2_{stat2}_specific')



        if stat1 != "ERA":
            stat_range1 = convert_to_number(stat_range1)
        if stat2 != "ERA":
            stat_range2 = convert_to_number(stat_range2)

        if stat1 in standard_careerStatBatting and stat2 in standard_careerStatBatting:
            results = get_players_careerStatBatting_careerStatBatting(stat1, stat_range1, stat2, stat_range2)
        elif stat1 in standard_careerStatPitching and stat2 in standard_careerStatPitching:
            results =get_players_careerStatPitching_careerStatPitching(stat1, stat_range1, stat2, stat_range2)
        elif (stat1 in standard_careerStatBatting and stat2 in standard_careerStatPitching) or (stat1 in standard_careerStatPitching and stat2 in standard_careerStatBatting):
            if stat1 in standard_careerStatBatting:
                results = get_players_careerStatBatting_careerStatPitching(stat1, stat_range1, stat2, stat_range2)
            else:
                results = get_players_careerStatBatting_careerStatPitching(stat2, stat_range2, stat1, stat_range1)

        elif (stat1 == "AVG" and stat2 in standard_careerStatBatting) or (stat1 in standard_careerStatBatting and stat2 == "AVG"):
            if stat1 == "AVG":
                results = get_players_careerBattingAVG_careerStatBatting(stat_range1, stat2, stat_range2)
            else:
                results = get_players_careerBattingAVG_careerStatBatting(stat_range2, stat1, stat_range1)
        elif (stat1 == "AVG" and stat2 in standard_careerStatPitching) or (stat1 in standard_careerStatPitching and stat2 == "AVG"):
            if stat1 == "AVG":
                results= get_players_careerBattingAVG_careerStatPitching(stat_range1, stat2, stat_range2)
            else:
                results = get_players_careerBattingAVG_careerStatPitching(stat_range2, stat1, stat_range1)
        elif (stat1 == "ERA" and stat2 in standard_careerStatPitching) or (stat1 in standard_careerStatPitching and stat2 == "ERA"):
            if stat1 == "ERA":
                results = get_players_careerPitchingERA_careerStatPitching(stat2, stat_range2)
            else:
                results = get_players_careerPitchingERA_careerStatPitching(stat1, stat_range1)
        elif (stat1 == "ERA" and stat2 in standard_careerStatBatting) or (stat1 in standard_careerStatBatting and stat2 == "ERA"):
            if stat1 == "ERA":
                results = get_players_careerPitchingERA_careerStatBatting(stat2, stat_range2)
            else:
                results = get_players_careerPitchingERA_careerStatBatting(stat1, stat_range1)
        elif (stat1 == "AVG" and stat2 == "ERA") or (stat1 == "ERA" and stat2 == "AVG"):
            if stat1 == "AVG":
                results = get_players_careerPitchingERA_careerStatAVG(stat_range1)
            else:
                results = get_players_careerPitchingERA_careerStatAVG(stat_range2)
        elif (stat1 == "WAR" and stat2 == "ERA") or (stat1 == "ERA" and stat2 == "WAR"):
            if stat1 == "WAR":
                results = get_players_careerPitchingERA_careerStatWAR(stat_range1)
            else:
                results = get_players_careerPitchingERA_careerStatWAR(stat_range2)

        elif (stat1 == "WAR" and stat2 == "AVG") or (stat1 == "AVG" and stat2 == "WAR"):
            if stat1 == "WAR":
                results = get_players_careerBattingAVG_careerStatWAR(stat_range2, stat_range1)
            else:
                results = get_players_careerBattingAVG_careerStatWAR(stat_range1, stat_range2)

        elif (stat1 == "WAR" and stat2 in standard_careerStatPitching) or (stat1 in standard_careerStatPitching and stat2 == "WAR"):
            if stat1 == "WAR":
                results = get_players_careerStatWAR_careerStatPitching(stat_range1, stat2, stat_range2)
            else:
                results = get_players_careerStatWAR_careerStatPitching(stat_range2, stat1, stat_range1)

        elif (stat1 == "WAR" and stat2 in standard_careerStatBatting) or (stat1 in standard_careerStatBatting and stat2 == "WAR"):
            if stat1 == "WAR":
                results = get_players_careerStatWAR_careerStatBatting(stat_range1, stat2, stat_range2)
            else:
                results = get_players_careerStatWAR_careerStatBatting(stat_range2, stat1, stat_range1)






    elif (option1 == "career statistic" and option2 == "seasonal statistic") or \
            (option1 == "seasonal statistic" and option2 == "career statistic"):
        # Determine which is career and which is seasonal
        if option1 == "career statistic":
            career_stat, seasonal_stat = option1_details, option2_details
            career_range = request.form.get(f'dropdown1_{career_stat}_specific')
            seasonal_range = request.form.get(f'dropdown2_{seasonal_stat}_specific')
        else:
            seasonal_stat, career_stat = option1_details, option2_details
            seasonal_range = request.form.get(f'dropdown1_{seasonal_stat}_specific')
            career_range = request.form.get(f'dropdown2_{career_stat}_specific')

        if career_stat != "ERA":
            career_range1 = convert_to_number(career_range)
        if seasonal_stat != "ERA" and seasonal_stat != "30+HR/30+SB":
            seasonal_range2 = convert_to_number(seasonal_range)

        # Check statistics and fetch results
        if career_stat in standard_careerStatBatting and seasonal_stat in standard_seasonStatBatting:
            results = get_players_careerStatBatting_seasonStatBatting(career_stat, career_range1, seasonal_stat, seasonal_range2)

        elif career_stat in standard_careerStatBatting and seasonal_stat == "ERA":
            results = get_players_careerStatBatting_seasonPitchingERA(career_stat, career_range1)

        elif career_stat in standard_careerStatPitching and seasonal_stat == "ERA":
            results = get_players_careerStatPitching_seasonPitchingERA(career_stat, career_range1)

        elif career_stat in standard_careerStatBatting and seasonal_stat in standard_seasonStatPitching:
            results = get_players_careerStatBatting_seasonStatPitching(career_stat, career_range1, seasonal_stat, seasonal_range2)

        elif career_stat in standard_careerStatPitching and seasonal_stat in standard_seasonStatBatting:
            results = get_players_careerStatPitching_seasonStatBatting(career_stat, career_range1, seasonal_stat, seasonal_range2)

        elif career_stat in standard_careerStatPitching and seasonal_stat in standard_seasonStatPitching:
            results = get_players_careerStatPitching_seasonStatPitching(career_stat, career_range1, seasonal_stat, seasonal_range2)

        elif career_stat == "ERA" and seasonal_stat in standard_seasonStatPitching:
            results = get_players_careerPitchingERA_seasonStatPitching(seasonal_stat, seasonal_range2)

        elif career_stat == "ERA" and seasonal_stat in standard_seasonStatBatting:
            results = get_players_careerPitchingERA_seasonStatBatting(seasonal_stat, seasonal_range2)

        elif career_stat == "ERA" and seasonal_stat == "ERA":
            results = get_players_careerPitchingERA_seasonPitchingERA()

        elif career_stat == "ERA" and seasonal_stat == "AVG":
            results = get_players_careerPitchingERA_seasonStatAVG(seasonal_range2)

        elif career_stat == "ERA" and seasonal_stat == "30+HR/30+SB":
            results = get_players_careerPitchingERA_seasonBatting3030()

        elif career_stat == "AVG" and seasonal_stat in standard_seasonStatBatting:
            results = get_players_careerBattingAVG_seasonStatBatting(seasonal_stat, seasonal_range2, career_range1)

        elif career_stat == "AVG" and seasonal_stat == "30+HR/30+SB":
            results = get_players_careerBattingAVG_seasonBatting3030(career_range1)

        elif career_stat == "AVG" and seasonal_stat == "AVG":
            results = get_players_careerBattingAVG_seasonBattingAVG(career_range1, seasonal_range2)

        elif career_stat == "AVG" and seasonal_stat == "ERA":
            results = get_players_careerBattingAVG_seasonPitchingERA(career_range1)

        elif career_stat == "AVG" and seasonal_stat in standard_seasonStatPitching:
            results = get_players_careerBattingAVG_seasonStatPitching(seasonal_stat, seasonal_range2, career_range1)

        elif career_stat in standard_careerStatBatting and seasonal_stat == "AVG":
            results = get_players_careerStatBatting_seasonBattingAVG(career_stat, career_range1, seasonal_range2)

        elif career_stat in standard_careerStatPitching and seasonal_stat == "AVG":
            results = get_players_careerStatPitching_seasonBattingAVG(career_stat, career_range1, seasonal_range2)

        elif career_stat in standard_careerStatBatting and seasonal_stat == "30+HR/30+SB":
            results = get_players_careerStatBatting_seasonBatting3030(career_stat, career_range1)

        elif career_stat in standard_careerStatPitching and seasonal_stat == "30+HR/30+SB":
            results = get_players_careerStatPitching_seasonBatting3030(career_stat, career_range1)

        elif career_stat == "WAR" and seasonal_stat == "30+HR/30+SB":
            results = get_players_careerStatWAR_seasonBatting3030(career_range1)

        elif career_stat == "WAR" and seasonal_stat == "AVG":
            results = get_players_careerStatWAR_seasonBattingAVG(career_range1, seasonal_range2)

        elif career_stat == "WAR" and seasonal_stat == "ERA":
            results = get_players_careerStatWAR_seasonPitchingERA(career_range1)

        elif career_stat == "WAR" and seasonal_stat in standard_seasonStatPitching:
            results = get_players_careerStatWAR_seasonStatPitching(career_range1, seasonal_stat, seasonal_range2)

        elif career_stat == "WAR" and seasonal_stat in standard_seasonStatBatting:
            results = get_players_careerStatWAR_seasonStatBatting(career_range1, seasonal_stat, seasonal_range2)











    elif (option1 == "career statistic" and option2 == "awards") or (option1 == "awards" and option2 == "career statistic"):
        print("IN AWARDS CSTATS")
        # Extract the award and career statistic details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        award = option2_details if option1 == "career statistic" else option1_details
        stat_range = request.form.get(f'dropdown2_{career_stat}_specific') if option1 == "awards" else request.form.get(f'dropdown1_{career_stat}_specific')
        if career_stat != "ERA":
            stat_range = convert_to_number(stat_range)

        # Handling different career statistics based on user input
        if award == "Hall of Fame" and career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_hof(career_stat, stat_range)

        elif award == "Hall of Fame" and career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_hof(career_stat, stat_range)

        elif award == "All Star" and career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_allStar(career_stat, stat_range)

        elif award == "All Star" and career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_allStar(career_stat, stat_range)

        elif award in standard_awards and career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_stdAward(career_stat, award, stat_range)

        elif award in standard_awards and career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_stdAward(career_stat, award, stat_range)

        elif award in standard_awards and career_stat == "AVG":
            results = get_players_careerBattingAVG_stdAward(stat_range, award)

        elif career_stat == "AVG" and award == "Hall of Fame":
            results = get_players_careerBattingAVG_hof(stat_range)

        elif career_stat == "AVG" and award == "All Star":
            results = get_players_careerBattingAVG_allStar(stat_range)

        elif career_stat == "ERA" and award == "Hall of Fame":
            results = get_players_careerPitchingERA_hof()

        elif career_stat == "ERA" and award == "All Star":
            results = get_players_careerPitchingERA_allStar()

        elif career_stat == "ERA" and award in standard_awards:
            results = get_players_careerPitchingERA_stdAward(award)






    elif (option1 == "career statistic" and option2 == "positions") or (option1 == "positions" and option2 == "career statistic"):
        print("IN POSITION CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        position = option2_details if option1 == "career statistic" else option1_details
        stat_range = request.form.get(f'dropdown2_{career_stat}_specific') if option1 == "positions" else request.form.get(
            f'dropdown1_{career_stat}_specific')

        if career_stat != "ERA":
            stat_range = convert_to_number(stat_range)

        if career_stat == "AVG":
            results = get_players_careerBattingAVG_position(stat_range, position)

        elif career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_position(career_stat, stat_range, position)

        elif career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_position(career_stat, stat_range, position)

        elif career_stat == "ERA":
            results = get_players_careerPitchingERA_position(position)



    elif (option1 == "career statistic" and option2 == "pob") or (option1 == "pob" and option2 == "career statistic"):
        print("IN POB CSTATS")
        # Extract career statistics and team details
        career_stat = option1_details if option1 == "career statistic" else option2_details
        pob = option2_details if option1 == "career statistic" else option1_details

        stat_range = request.form.get(
            f'dropdown2_{career_stat}_specific') if option1 == "pob" else request.form.get(
            f'dropdown1_{career_stat}_specific')


        if career_stat in standard_careerStatPitching and pob == "Outside of USA":
            results = get_players_careerStatPitching_pob(career_stat, stat_range)

        if career_stat in standard_careerStatBatting and pob == "Outside of USA":
            results = get_players_careerStatBatting_pob(career_stat, stat_range)

        if career_stat == "AVG" and pob == "Outside of USA":
            results = get_players_careerBattingAVG_pob(stat_range)

        if career_stat == "ERA" and pob == "Outside of USA":
            results = get_players_careerPitchingERA_pob()

        if career_stat in standard_careerStatPitching and pob != "Outside of USA":
            results = get_players_careerStatPitching_country(career_stat, stat_range, pob)

        if career_stat in standard_careerStatBatting and pob != "Outside of USA":
            results = get_players_careerStatBatting_country(career_stat, stat_range, pob)

        if career_stat == "AVG" and pob != "Outside of USA":
            results = get_players_careerBattingAVG_country(stat_range, pob)

        if career_stat == "ERA" and pob != "Outside of USA":
            results = get_players_careerPitchingERA_country(pob)




    elif (option1 == "career statistic" and option2 == "dp") or (option1 == "dp" and option2 == "career statistic"):
        career_stat = option1_details if option1 == "career statistic" else option2_details
        stat_range = request.form.get(
            f'dropdown2_{career_stat}_specific') if option1 == "dp" else request.form.get(
            f'dropdown1_{career_stat}_specific')
        if career_stat in standard_careerStatBatting:
            results = get_players_careerStatBatting_draftPick(career_stat, stat_range)

        if career_stat in standard_careerStatPitching:
            results = get_players_careerStatPitching_draftPick(career_stat, stat_range)

        if career_stat == "AVG":
            results = get_players_careerBattingAVG_draftPick(stat_range)

        if career_stat == "ERA":
            results = get_players_careerPitchingERA_draftPick()




    elif option1 == "seasonal statistic" and option2 == "seasonal statistic":
        stat1 = option1_details
        stat2 = option2_details


        stat_range1 = request.form.get(f'dropdown1_{stat1}_specific')
        stat_range2 = request.form.get(f'dropdown2_{stat2}_specific')

        if stat1 != "30+HR/30+SB" and stat1 != "ERA":
            stat_range1 = convert_to_number(stat_range1)

        if stat2 != "30+HR/30+SB" and stat2 != "ERA":
            stat_range2 = convert_to_number(stat_range2)

        if stat1 in standard_seasonStatBatting and stat2 in standard_seasonStatBatting:
            results = get_players_seasonStatBatting_seasonStatBatting(stat1, stat_range1, stat2, stat_range2)

        elif stat1 in standard_seasonStatPitching and stat2 in standard_seasonStatPitching:
            results = get_players_seasonStatPitching_seasonStatPitching(stat1, stat_range1, stat2, stat_range2)

        elif (stat1 in standard_seasonStatBatting or stat1 in standard_seasonStatPitching) and (stat2 in standard_seasonStatBatting or stat2 in standard_seasonStatPitching):
            if stat1 in standard_seasonStatBatting:
                results = get_players_seasonStatPitching_seasonStatBatting(stat2, stat_range2, stat1, stat_range1)
            else:
                results = get_players_seasonStatPitching_seasonStatBatting(stat1, stat_range1, stat2, stat_range2)

        elif (stat1 in standard_seasonStatPitching and stat2 == "AVG") or (stat1 == "AVG" and stat2 in standard_seasonStatPitching):
            if stat1 in standard_seasonStatPitching:
                results = get_players_seasonStatPitching_seasonStatAVG(stat1, stat_range1, stat_range2)
            else:
                results = get_players_seasonStatPitching_seasonStatAVG(stat2, stat_range2, stat_range1)

        elif (stat1 in standard_seasonStatBatting and stat2 == "AVG") or (stat1 == "AVG" and stat2 in standard_seasonStatBatting):
            if stat1 in standard_seasonStatBatting:
                results = get_players_seasonStatBatting_seasonStatAVG(stat1, stat_range1, stat_range2)
            else:
                results = get_players_seasonStatBatting_seasonStatAVG(stat2, stat_range2, stat_range1)

        elif (stat1 == "AVG" and stat2 == "30+HR/30+SB") or (stat1 == "30+HR/30+SB" and stat2 == "AVG"):
            if stat1 == "AVG":
                results = get_players_seasonBatting3030_seasonStatAVG(stat_range1)
            else:
                results = get_players_seasonBatting3030_seasonStatAVG(stat_range2)

        elif (stat1 == "AVG" and stat2 == "ERA") or (stat1 == "ERA" and stat2 == "AVG"):
            if stat1 == "AVG":
                results = get_players_seasonPitchingERA_seasonStatAVG(stat_range1)
            else:
                results = get_players_seasonPitchingERA_seasonStatAVG(stat_range2)

        elif (stat1 == "30+HR/30+SB" and stat2 == "ERA") or (stat1 == "ERA" and  stat2 == "30+HR/30+SB"):
            results = get_players_seasonPitchingERA_seasonBatting3030()


        elif (stat1 in standard_seasonStatBatting and stat2 == "30+HR/30+SB") or (stat1 == "30+HR/30+SB" and stat2 in standard_seasonStatBatting):
            if stat1 == "30+HR/30+SB":
                results = get_players_seasonStatBatting3030_seasonStatBatting(stat2, stat_range2)
            else:
                results = get_players_seasonStatBatting3030_seasonStatBatting(stat1, stat_range1)

        elif (stat1 in standard_seasonStatPitching and stat2 == "30+HR/30+SB") or (stat1 == "30+HR/30+SB" and stat2 in standard_seasonStatPitching):
            if stat1 == "30+HR/30+SB":
                results = get_players_seasonStatBatting3030_seasonStatPitching(stat2, stat_range2)
            else:
                results = get_players_seasonStatBatting3030_seasonStatPitching(stat1, stat_range1)

        elif (stat1 in standard_seasonStatPitching and stat2 == "ERA") or (stat1 == "ERA" and stat2 in standard_seasonStatPitching):
            if stat1 == "ERA":
                results = get_players_seasonPitchingERA_seasonStatPitching(stat2, stat_range2)
            else:
                results= get_players_seasonPitchingERA_seasonStatPitching(stat1, stat_range1)

        elif (stat1 in standard_seasonStatBatting and stat2 == "ERA") or (stat1 == "ERA" and stat2 in standard_seasonStatBatting):
            if stat1 == "ERA":
                results = get_players_seasonPitchingERA_seasonStatBatting(stat2, stat_range2)
            else:
                results= get_players_seasonPitchingERA_seasonStatBatting(stat1, stat_range1)



    elif (option1 == "seasonal statistic" and option2 == "awards") or (option1 == "awards" and option2 == "seasonal statistic"):
        if option1 == "awards":
            award = option1_details  # option1 holds the award details
            stat = option2_details  # option2 holds the stat details
        else:
            award = option2_details  # if option1 is not "award", then option2 must be "award"
            stat = option1_details  # if option2 is "award", then option1 must be "seasonal statistic"

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "awards" else request.form.get(
            f'dropdown1_{stat}_specific')
        if stat != "ERA" and stat != "30+HR/30+SB":
            stat_range = convert_to_number(stat_range)


        if stat in standard_seasonStatBatting and award in standard_awards :
            results = get_players_seasonStatBatting_stdAward(stat, award, stat_range)
        elif stat in standard_seasonStatPitching and award in standard_awards:
            results = get_players_seasonStatPitching_stdAward(award, stat, stat_range)
        elif stat in standard_seasonStatBatting and award == "World Series":
            results = get_players_seasonStatBatting_ws(stat, stat_range)
        elif stat in standard_seasonStatBatting and award == "All Star":
            results = get_players_seasonStatBatting_allStar(stat, stat_range)
        elif stat in standard_seasonStatPitching and award == "All Star":
            results = get_players_seasonStatPitching_allStar(stat, stat_range)
        elif stat == "AVG" and award in standard_awards:
            results = get_players_seasonBattingAVG_stdAward(stat_range, award)
        elif stat == "AVG" and award == "All Star":
            results = get_players_seasonBattingAVG_allStar(stat_range)
        elif stat == "AVG" and award == "Hall of Fame":
            results = get_players_seasonBattingAVG_hof(stat_range)
        elif stat in standard_seasonStatBatting and award == "Hall of Fame":
            results = get_players_seasonStatBatting_hof(stat, stat_range)
        elif stat in standard_seasonStatPitching and award == "Hall of Fame":
            results = get_players_seasonStatPitching_hof(stat, stat_range)
        elif stat == "ERA" and award in standard_awards:
            results = get_players_seasonStatERA_stdAward(award)
        elif stat == "ERA" and award == "All Star":
            results = get_players_seasonStatERA_allStar()
        elif stat == "ERA" and award == "Hall of Fame":
            results = get_players_seasonStatERA_hof()
        elif stat == "30+HR/30+SB" and award in standard_awards:
            results = get_players_seasonBatting3030_stdAward(award)
        elif stat == "30+HR/30+SB" and award == "Hall of Fame":
            results = get_players_seasonBatting3030_hof()
        elif stat == "30+HR/30+SB" and award == "All Star":
            results = get_players_seasonBatting3030_allStar()
        elif stat == "WAR" and award == "Hall of Fame":
            results = get_players_seasonWAR_hof(stat_range)



    elif (option1 == "seasonal statistic" and option2 == "positions") or (option1 == "positions" and option2 == "seasonal statistic"):
        if option1 == "positions":
            position = option1_details
            stat = option2_details
        else:
            position = option2_details
            stat = option1_details

        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "positions" else request.form.get(
            f'dropdown1_{stat}_specific')
        if stat != "ERA" and stat != "30+HR/30+SB":
            stat_range = convert_to_number(stat_range)

        if stat in standard_seasonStatBatting:
            results = get_players_seasonStatBatting_position(stat, position, stat_range)

        elif stat in standard_seasonStatPitching:
            results = get_players_seasonStatPitching_position(stat, position, stat_range)

        elif stat == "ERA":
            results = get_players_seasonPitchingERA_position(position)

        elif stat == "AVG":
            results = get_players_seasonBattingAVG_position(position, stat_range)

        elif stat == "30+HR/30+SB":
            results = get_players_seasonBatting3030_position(position)
        elif stat == "WAR":
            results = get_players_seasonWAR_position(stat_range, position)


    elif (option1 == "seasonal statistic" and option2 == "pob") or (option1 == "pob" and option2 == "seasonal statistic"):
        stat = option1_details if option1 == "seasonal statistic" else option2_details
        pob = option2_details if option1 == "seasonal statistic" else option1_details
        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "pob" else request.form.get(
            f'dropdown1_{stat}_specific')
        if stat != "ERA" and stat != "30+HR/30+SB":
            stat_range = convert_to_number(stat_range)

        if stat in standard_seasonStatBatting and pob == "Outside of USA":
            results = get_players_seasonStatBatting_pob(stat, stat_range)
        elif stat in standard_seasonStatPitching and pob == "Outside of USA":
            results = get_players_seasonStatPitching_pob(stat, stat_range)
        elif stat == "ERA" and pob == "Outside of USA":
            results = get_players_seasonPitchingERA_pob()
        elif stat == "AVG" and pob == "Outside of USA":
            results = get_players_seasonBattingAVG_pob(stat_range)
        elif stat == "30+HR/30+SB" and pob == "Outside of USA":
            results = get_players_seasonBatting3030_pob()
        elif stat in standard_seasonStatBatting and pob != "Outside of USA":
            results = get_players_seasonStatBatting_country(stat, stat_range, pob)
        elif stat in standard_seasonStatPitching and pob != "Outside of USA":
            results = get_players_seasonStatPitching_country(stat, stat_range, pob)
        elif stat == "AVG" and pob != "Outside of USA":
            results = get_players_seasonBattingAVG_country(stat_range, pob)
        elif stat == "ERA" and pob != "Outside of USA":
            results = get_players_seasonPitchingERA_country(pob)
        elif stat == "30+HR/30+SB" and pob != "Outside of USA":
            results = get_players_seasonBatting3030_country(pob)


    elif (option1 == "seasonal statistic" and option2 == "dp") or (option1 == "dp" and option2 == "seasonal statistic"):
        stat = option1_details if option1 == "seasonal statistic" else option2_details
        stat_range = request.form.get(f'dropdown2_{stat}_specific') if option1 == "dp" else request.form.get(
            f'dropdown1_{stat}_specific')
        if stat != "ERA" and stat != "30+HR/30+SB":
            stat_range = convert_to_number(stat_range)

        if stat in standard_seasonStatPitching:
            results = get_players_draftPick_seasonStatPitching(stat, stat_range)
        elif stat in standard_seasonStatBatting:
            results = get_players_draftPick_seasonStatBatting(stat, stat_range)
        elif stat == "AVG":
            results = get_players_draftPick_seasonBattingAVG(stat_range)
        elif stat == "ERA":
            results = get_players_draftPick_seasonPitchingERA()
        elif stat == "30+HR/30+SB":
            results = get_players_draftPick_seasonBatting3030()



    elif option1 == "awards" and option2 == "awards":
        if option1_details in standard_awards and option2_details in standard_awards:
            results = get_players_stdAward_stdAward(option1_details, option2_details)
        elif (option1_details == "All Star" and option2_details == "Hall of Fame") or (option1_details == "Hall of Fame" and option2_details == "All Star"):
            results = get_players_allStar_hof()
        elif (option1_details == "Hall of Fame" and option2_details in standard_awards) or (option1_details in standard_awards and option2_details == "Hall of Fame"):
            if option1_details in standard_awards:
                results = get_players_hof_stdAward(option1_details)
            else:
                results = get_players_hof_stdAward(option2_details)
        elif (option1_details == "All Star" and option2_details in standard_awards) or (option1_details in standard_awards and option2_details == "All Star"):
            if option1_details in standard_awards:
                results= get_players_allStar_stdAward(option1_details)
            else:
                results = get_players_allStar_stdAward(option2_details)






    elif (option1 == "positions" and option2 == "awards") or (option1 == "awards" and option2 == "positions"):
        position = option1_details if option1 == "positions" else option2_details
        award = option1_details if option1 == "awards" else option2_details

        if award in standard_awards:
            results = get_players_stdAward_position(award, position)

        elif award == "Hall of Fame":
            results = get_players_hof_position(position)

        elif award == "All Star":
            results = get_players_allstar_position(position)

    elif (option1 == "pob" and option2 == "awards") or (option1 == "awards" and option2 == "pob"):
        award = option1_details if option1 == "awards" else option2_details
        pob = option2_details if option1 == "awards" else option1_details

        if award == "Hall of Fame" and pob == "Outside of USA":
            results = get_players_pob_hof()

        elif award == "All Star" and pob == "Outside of USA":
            results = get_players_pob_allStar()

        elif award in standard_awards and pob == "Outside of USA":
            results = get_players_pob_stdAward(award)

        elif award in standard_awards and pob != "Outside of USA":
            results = get_players_country_stdAward(award, pob)

        elif award == "Hall of Fame" and pob != "Outside of USA":
            results = get_players_country_hof(pob)

        elif award == "All Star" and pob != "Outside of USA":
            results = get_players_country_allStar(pob)

    elif (option1 == "dp" and option2 == "awards") or (option1 == "awards" and option2 == "dp"):
        award = option1_details if option1 == "awards" else option2_details
        if award == "Hall of Fame":
            results = get_players_draftPick_hof()
        elif award == "All Star":
            results = get_players_draftPick_allStar()
        elif award in standard_awards:
            results = get_players_draftPick_stdAward(award)


    elif (option1 == "positions" and option2 == "positions"):
        position1 = option1_details
        position2 = option2_details
        results = get_players_position_position(position1, position2)

    elif (option1 == "pob" and option2 == "positions") or (option1 == "positions" and option2 == "pob"):
        position = option1_details if option1 == "positions" else option2_details
        pob = option2_details if option1 == "positions" else option1_details
        if pob == "Outside of USA":
            results = get_players_pob_position(position)
        else:
            results = get_players_country_position(position, pob)


    elif (option1 == "dp" and option2 == "positions") or (option1 == "positions" and option2 == "dp"):
        position = option1_details if option1 == "positions" else option2_details
        results = get_players_draftPick_position(position)

    elif (option1 == "dp" and option2 == "pob") or (option1 == "pob" and option2 == "dp"):
        pob = option1_details if option1 == "pob" else option2_details
        if pob == "Outside of USA":
            results = get_players_draftPick_pob()
        else:
            results = get_players_draftPick_country(pob)



    else:
        return "Invalid selection or combination. Please try again.", 400
        # Render results
        # Render results

    if results:
        return render_template('results.html', results=results)
    else:
        return render_template(
            'results.html',
            results=[],
            message="No matching results found for your query."
        )