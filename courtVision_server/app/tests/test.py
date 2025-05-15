import sys
from nba_api.stats.endpoints import TeamInfoCommon ,leaguedashteamstats, teamyearbyyearstats, leaguestandings, leaguestandingsv3, CommonPlayerInfo, teamgamelogs, assistleaders, leaguedashteamstats, playercareerstats
from nba_api.stats.library.data import players
from nba_api.stats.library.data import teams
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import ReadTimeout, ConnectionError
import random
import json
import time
from datetime import datetime
from app.db.database import SessionLocal
from sqlalchemy.orm import Session
from app.models.models import *
import threading

import requests


import hashlib


session = SessionLocal()

def hash_mod_id(player_id, team_id, season_id):
    #season_int = int(season_id.replace('-', ''))
    raw = f"{player_id}{team_id}{season_id}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return int(hashed, 16) % (7**9)

def test_playercareerstats_Endpoint(player_id):
    player_info = playercareerstats.PlayerCareerStats(player_id=player_id)
    player_info_per = playercareerstats.PlayerCareerStats(player_id=player_id, per_mode36="PerGame")
    print("Raw player_info object:")
    #print(player_info_per)
    print()

    player_data = player_info.get_dict()
    player_data_per = player_info_per.get_dict()
    print("Converted player_data dictionary:")
    #print(player_data)
    print()

    player_details = player_data["resultSets"][0]["rowSet"]
    player_details_per = player_data_per["resultSets"][0]["rowSet"]
    print("First row of player_details:")
    #print(player_details)
    print()

    headers = player_data["resultSets"][0]["headers"]
    print("Headers for data:")
    #print(headers)
    print()


    player_details_list = [dict(zip(headers, row)) for row in player_details]
    player_details_per_list = [dict(zip(headers, row)) for row in player_details_per]
    print("Zipped player profile dictionary:")
    #print(player_details_list)
    print()
    
    player_data = []
    for player_details, player_details_per in zip(player_details_list, player_details_per_list):

        player_id = player_details.get('PLAYER_ID')
        team_id = player_details.get('TEAM_ID')
        season = player_details.get('SEASON_ID')
        season_id = int(season.replace('-', ''))
        #if season_id == 202122:
        player_data.append({
            
            "id":hash_mod_id(player_id, team_id, season_id),
            "player_id":player_id,
            "season_id":season_id,
            "team_id":team_id,

            "games_played":player_details.get('GP'),
            "games_started":player_details.get('GS'),
            
            "minutes_played_per_game":player_details_per.get("MIN"),

            # Per-game stats
            "points_per_game":player_details_per.get('PTS'),
            "assists_per_game":player_details_per.get('AST'),
            "offensive_rebounds_per_game":player_details_per.get('OREB'),
            "defensive_rebounds_per_game":player_details_per.get('DREB'),
            "rebounds_per_game":player_details_per.get('REB'),
            "steals_per_game":player_details_per.get('STL'),
            "blocks_per_game":player_details_per.get('BLK'),
            "turn_over_per_game":player_details_per.get('TOV'),
            "personal_fouls_per_game":player_details_per.get('PF'),
            
            # Total stats
            "total_points":player_details.get('PTS'),
            "total_assists":player_details.get('AST'),
            "total_offensive_rebounds":player_details.get('OREB'),
            "total_defensive_rebounds":player_details.get('DREB'),
            "total_rebounds":player_details.get('REB'),
            "total_steals":player_details.get('STL'),
            "total_blocks":player_details.get('BLK'),
            "total_turnovers":player_details.get('TOV'),
            "total_personal_fouls":player_details.get('PF'),

            # Shooting - per game
            "field_goal_made_per_game":player_details_per.get('FGM'),
            "field_goal_attempted_per_game":player_details_per.get('FGA'),

            "three_point_made_per_game":player_details_per.get('FG3M'),
            "three_point_attempted_per_game":player_details_per.get('FG3A'),

            "free_throw_made_per_game":player_details_per.get('FTM'),
            "free_throw_attempted_per_game":player_details_per.get('FTA'),
            
            # Shooting - totals
            "total_field_goal":player_details.get('FGM'),
            "total_field_goal_attempted":player_details.get('FGA'),

            "total_three_point_made":player_details.get('FG3M'),
            "total_three_point_attempted":player_details.get('FG3A'),        
            
            "total_free_throw_made":player_details.get('FTM'),
            "total_free_throw_attempted":player_details.get('FTA'),
            
            # Shooting - percentage                                      
            "field_goal_percentage": round(player_details.get('FG_PCT') * 100, 1),
            "three_point_percentage": round(player_details.get('FG3_PCT') * 100, 1),
            "free_throw_percentage": round(player_details.get('FT_PCT') * 100, 1),
        })

    return player_data

print("List all lebron career stats")
#print(len(test_playercareerstats_Endpoint(2544)))
print(test_playercareerstats_Endpoint(2544))

raw = "25441610612739200809"
hashed = hashlib.sha256(raw.encode()).hexdigest()
id=int(hashed, 16) % (7**9)
print(id)
print(hash_mod_id(2544, 1610612739, 200809))



'''
# Semaphore to rate limit requests (e.g., 5 concurrent calls at a time)
semaphore = threading.Semaphore(5)

class RestartSignal(Exception):
    """#Raised to simulate a full restart due to repeated failure.
"""
    pass

pause_event = threading.Event()
pause_event.set()

def fetch_players_info(player_id):
    tries = 1
    while tries <= 3:
        try:
            pause_event.wait()
            with semaphore:
                # Respect rate limits
                time.sleep(random.uniform(1, 3))
                #time.sleep(random.uniform(0.3, 0.6))  # Optional: tune this down/up as needed

                player_info = CommonPlayerInfo(player_id=player_id)#, timeout=30)
                player_data = player_info.get_dict()

            player_details = player_data["resultSets"][0]["rowSet"][0]
            headers = player_data["resultSets"][0]["headers"]
            player_profile = dict(zip(headers, player_details))

            try:
                birth_date = datetime.strptime(player_profile.get('BIRTHDATE'), "%Y-%m-%dT%H:%M:%S").date()
            except (ValueError, TypeError):
                birth_date = None        

            my_dict = {
                'id': player_profile.get('PERSON_ID'),
                'name': f"{player_profile.get('FIRST_NAME')} {player_profile.get('LAST_NAME')}",
                'position': player_profile.get('POSITION', 'Unknown'),
                'height': player_profile.get('HEIGHT', 'Unknown'),
                'weight': int(player_profile.get('WEIGHT')) if str(player_profile.get('WEIGHT')).isdigit() else None,
                'birth_date': birth_date,
                'nationality': player_profile.get('COUNTRY', 'Unknown'),
                'college': player_profile.get('SCHOOL', None),
                'jersey_number':player_profile.get('JERSEY', None),
                'experience':player_profile.get('SEASON_EXP', None),
                'is_active': player_profile.get('ROSTERSTATUS') == 'Active',
                'image': f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_profile.get('PERSON_ID')}.png"
            }
            print("player_profile")
            print(my_dict)
            print()
            return my_dict

        except (ReadTimeout, ConnectionError) as e:
            print(f"Timeout/Connection error for {player_id} ({tries}/3)...")
            tries += 1

        except Exception as e:
            print(f"Unhandled error for player {player_id}: {e}")
            break

    #print(f"Failed to fetch data for player {player_id}")
    raise RestartSignal(f"Failed to fetch player {player_id}")

def fetch_all_players(players, max_workers=5):
    player_ids = [player[0] for player in players]
    fetched_players = []
    fetched_ids = set()

    attempt = 1
    i=1
    while len(fetched_players) < len(player_ids):
        print(f"\nAttempt {attempt} — Fetching missing players ({len(player_ids) - len(fetched_ids)} remaining)...")

        # Filter out already fetched player IDs
        remaining_ids = [pid for pid in player_ids if pid not in fetched_ids]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_players_info, pid): pid for pid in remaining_ids}

            for future in as_completed(futures):
                pid = futures[future]
                try:
                    data = future.result()
                    if data:
                        fetched_players.append(data)
                        fetched_ids.add(pid)
                        print(f"Fetched {i} players:", data['name'])
                        i+=1

                except RestartSignal as rs:
                    # 🛑 Cancel execution
                    executor.shutdown(wait=False, cancel_futures=True)
                    
                    # ⏸ Pause globally
                    pause_event.clear()
                    wait_time = random.uniform(30, 60)
                    print(f"Pausing all threads for {wait_time:.2f}s...")
                    time.sleep(wait_time)  # Simulate full restart
                    print("Resuming all threads...")
                    pause_event.set()

                    break  # Retry from top of while loop


                except Exception as e:
                    executor.shutdown(wait=False, cancel_futures=True)
                    print(f"Future error for player {pid}: {e}")
                    sys.exit(0)

        print(f"Total fetched so far: {len(fetched_players)} / {len(player_ids)}")
        attempt += 1

    print(f"\nSuccessfully fetched all {len(fetched_players)} players.")
    return fetched_players

print((fetch_all_players(players,5)))

'''





















"""
def fetch_seasons():
    seasons = []
    for id,year in enumerate(range(2000, 2025)):
        seasons.append({
            "id": id,
            "year" : f"{year}-{str(year + 1)[-2:]}",
        })
    return seasons

def fetch_teams_by_seasons():
 #   if session.query('team_by_seasons').filter_by(team_id=Team_id).all() == None:
        team_seasons_data = []
        last_25_seasons = fetch_seasons()
        my_dict = {}
        for season in last_25_seasons:
            info = leaguedashteamstats.LeagueDashTeamStats(
                per_mode_detailed="PerGame",
                season=season,
            )
            league_ranking = 0
            teamsranking = []

            data = info.get_dict()
            print(data)
            row_set = data["resultSets"][0]["rowSet"]
            teams = []
            print(len(row_set))
            for i in range(len(row_set)):
                details = data["resultSets"][0]["rowSet"][i]
                headers = data["resultSets"][0]["headers"]
                teams.append(dict(zip(headers, details)))


            for team in session.query(Team).all():
                team_divison = session.query(Team).filter(team.divison).all()
                team_conference = session.query(Team).filter(team.conference).all()
                division_ranking = 0
                conference_ranking = 0 
                for team in team_divison:
                    if(team.W_PCT.sort()):
                         
                for team in team_conference:    
                    if (team.W_PCT.sort()):
                
                
                teamsranking.append({
                    "Team_id": team.id,
                    "division_ranking": division_ranking, 
                    "conference_ranking":conference_ranking,
                    "league_ranking":league_ranking
                })
            
        
        return team_seasons_data
    #return None
"""    
'''
info = leaguedashteamstats.LeagueDashTeamStats(
    last_n_games=0,
    league_id_nullable="00",
    per_mode_detailed="PerGame",
    season="2024-25",
    season_type_all_star="Regular Season",
    measure_type_detailed_defense="Base",
    month=0,
    opponent_team_id = 0,
    pace_adjust = "N",
    period = 0,
    plus_minus = "N",
    rank = "N",
    conference_nullable = "",
    date_from_nullable = "",
    date_to_nullable = "",
    division_simple_nullable = "",
    game_scope_simple_nullable = "",
    game_segment_nullable = "",
    location_nullable = "",
    outcome_nullable = "",
    po_round_nullable = "",
    player_experience_nullable = "",
    player_position_abbreviation_nullable = "",
    season_segment_nullable = "",
    shot_clock_range_nullable = "",
    starter_bench_nullable = "",
    team_id_nullable = "",
    two_way_nullable = "0",
    vs_conference_nullable = "",
    vs_division_nullable = "",
)
'''
'''
info = leaguedashteamstats.LeagueDashTeamStats(
            per_mode_detailed="PerGame",
            season="2024-25",
        )


data = info.get_dict()
row_set = data["resultSets"][0]["rowSet"]
profile = []
print(len(row_set))
for i in range(len(row_set)):
    details = data["resultSets"][0]["rowSet"][i]
    headers = data["resultSets"][0]["headers"]
    print(i)
    #print(details)
    print(dict(zip(headers, details)))
    profile.append(dict(zip(headers, details)))
#print(profile)

'''







'''
def fetch_players_info(player_id):
    tries = 0
    while tries < 3:
        try:
            time.sleep(random.uniform(0.1, 0.3))  # Small delay to avoid rate limits    
            player_info = CommonPlayerInfo(player_id=player_id, timeout=120)  # Increased timeout
            
            player_data = player_info.get_dict()

            player_details = player_data["resultSets"][0]["rowSet"][0]
            headers = player_data["resultSets"][0]["headers"]
            
            player_profile = dict(zip(headers, player_details))        
        
            try:
                birth_date = datetime.strptime(player_profile.get('BIRTHDATE'), "%Y-%m-%dT%H:%M:%S").date()
            except (ValueError, TypeError):
                birth_date = None        
            
            my_dict = {
                'id': player_profile.get('PERSON_ID'),
                'name': f"{player_profile.get('FIRST_NAME')} {player_profile.get('LAST_NAME')}",
                'position': player_profile.get('POSITION', 'Unknown'),
                'height': player_profile.get('HEIGHT', 'Unknown'),
                'weight': int(player_profile.get('WEIGHT')) if str(player_profile.get('WEIGHT')).isdigit() else None,
                'birth_date': birth_date,
                'nationality': player_profile.get('COUNTRY', 'Unknown'),
                'college': player_profile.get('SCHOOL', None),
                'is_active': player_profile.get('ROSTERSTATUS') == 'Active',
                'image': f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_profile.get('PERSON_ID')}.png"
            }
            print("Fetched Player:", f"{player_profile.get('FIRST_NAME')} {player_profile.get('LAST_NAME')}")
            return my_dict

        except Exception as e:
            print(f"Error fetching player {player_id}, retrying... ({tries+1}/3)")
            print(f"{e}")
            time.sleep(2 ** tries)  # Exponential backoff
            tries += 1

    return None  # Return None if failed after retries


def fetch_all_players(max_workers=15):
    player_id = [player[0] for player in players]
    fetched_players = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_players_info, pid): pid for pid in player_id}

        for future in as_completed(future_to_id):
            player_id = future_to_id[future]
            try:
                player_data = future.result()
                if player_data:
                    fetched_players.append(player_data)
            except Exception as e:
                print(f"Failed to fetch Player {player_id}: {e}")
    
    print("Fetched All Players")
    return fetched_players

print(fetch_all_players())


def fetch_seasons():
    seasons = []
    for year in range(2000, 2025):
        seasons.append(f"{year}-{str(year + 1)[-2:]}")
    return seasons

seasons = fetch_seasons()
for season in seasons:
    team_info = leaguestandingsv3.LeagueStandingsV3(season=season, timeout=60)
    team_data = team_info.get_dict()


    team_details = team_data["resultSets"][0]["rowSet"][0]
    headers = team_data["resultSets"][0]["headers"]

    team_profile = dict(zip(headers, team_details))

    print(team_profile)  # Use parentheses instead of square brackets
'''