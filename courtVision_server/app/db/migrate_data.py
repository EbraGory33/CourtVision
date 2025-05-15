import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from nba_api.stats.library.data import teams
from nba_api.stats.library.data import players
from nba_api.stats.endpoints import TeamInfoCommon
from nba_api.stats.endpoints import CommonPlayerInfo
from nba_api.stats.endpoints import playercareerstats
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.models import *
from datetime import datetime
import json
import sys
import os
from requests.exceptions import ReadTimeout
import random
import threading
import hashlib

# Get the absolute path of the project root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

session = SessionLocal()

# Function to insert Seasons
def fetch_seasons():
    seasons = []
    for id,year in enumerate(range(1949, 2025)):
        seasons.append({
            "id": int(f"{year}{str(year + 1)[-2:]}"),
            "year" : f"{year}-{str(year + 1)[-2:]}",
        })
    return seasons

def insert_seasons():
    session = SessionLocal()
    season_data = fetch_seasons()
    print("Fetched Seasons")
    seasons = [Season(**season) for season in season_data]
    session.bulk_save_objects(seasons)
    session.commit()
    session.close()


# Function to insert Teams
def fetch_teams():
    team_id = [team[0] for team in teams]
    print(team_id)
    saved_teams = []
    i=1
    
    for idx,id in enumerate(team_id):
        retries = 3  # Max retries
        for attempt in range(retries):
            try:
                team_info = TeamInfoCommon(team_id=id, timeout=10)
                team_data = team_info.get_dict()

                team_details = team_data["resultSets"][0]["rowSet"][0]
                headers = team_data["resultSets"][0]["headers"]

                team_data = {
                    "id": team_details[headers.index("TEAM_ID")],
                    "name": team_details[headers.index("TEAM_NAME")],
                    "abbreviation": team_details[headers.index("TEAM_ABBREVIATION")],
                    "city": team_details[headers.index("TEAM_CITY")],
                    "state": teams[idx][6],
                    "conference": team_details[headers.index("TEAM_CONFERENCE")],
                    "division": team_details[headers.index("TEAM_DIVISION")],
                    "founded": team_details[headers.index("MIN_YEAR")],
                    "logo": f"https://cdn.nba.com/logos/nba/{id}/global/L/logo.svg"
                }
                print(i)
                print(team_data)
                i+=1
                saved_teams.append(team_data)
                break  # Break retry loop if successful
            except ReadTimeout:
                wait_time = 2 ** attempt + random.uniform(0, 1)  # Exponential backoff
                print(f"Timeout for team {id}, retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        else:
            print(f"Failed to fetch data for team {id} after {retries} retries.")

    return saved_teams

def insert_teams(teams_data):
    session = SessionLocal()
    teams = [Team(**team) for team in teams_data]
    session.bulk_save_objects(teams)
    session.commit()
    session.close()

# Function to insert Players

# Semaphore to rate limit requests (e.g., 5 concurrent calls at a time)
semaphore = threading.Semaphore(5)

class RestartSignal(Exception):
    """Raised to simulate a full restart due to repeated failure."""
    pass

def insert_players(players_data):
    """
    Insert player data into the database.

    Args:
        session (SQLAlchemy Session): The active database session.
        players_data (list): List of player data to insert.
    """
    session = SessionLocal()
    players = [Player(**player) for player in players_data]
    session.bulk_save_objects(players)
    session.commit()
    session.close()


pause_event = threading.Event()
pause_event.set()


def fetch_players_info(player_id):
    """
    Fetch player information from an external API.

    Args:
        player_id (str): The unique identifier for the player.

    Returns:
        dict: Player data retrieved from the API.
    """
    tries = 1
    while tries <= 3:
        pause_event.wait()
        try:
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
                'jersey_number':int(player_profile.get('JERSEY')) if str(player_profile.get('JERSEY')).isdigit() else None,
                'experience':player_profile.get('SEASON_EXP', None),
                'is_active': player_profile.get('ROSTERSTATUS') == 'Active',
                'image': f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_profile.get('PERSON_ID')}.png"
            }
            return my_dict

        except (ReadTimeout, ConnectionError) as e:
            print(f"Timeout/Connection error for {player_id} ({tries}/3)...")
            tries += 1

        except Exception as e:
            print(f"Unhandled error for player {player_id}: {e}")
            break

    raise RestartSignal(f"Failed to fetch player {player_id}")

def fetch_all_players(players, max_workers=5):
    """
    Fetch all players' information and insert them into the database.

    Args:
        session (SQLAlchemy Session): The active database session.
        player_ids (list): List of player IDs to fetch data for.
    """
    player_ids = [player[0] for player in players]
    fetched_players = []
    imported_Players_ids = [player.id for player in session.query(Player.id).all()]

    attempt = 1
    i=1
    while not set(player_ids).issubset(set(imported_Players_ids)):
        print(f"\nAttempt {attempt} — Fetching missing players ({len(set(player_ids) - set(imported_Players_ids))} remaining)...")

        # Filter out already fetched player IDs
        remaining_ids = [pid for pid in player_ids if pid not in imported_Players_ids]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_players_info, pid): pid for pid in remaining_ids}

            for future in as_completed(futures):
                pid = futures[future]
                try:
                    data = future.result()
                    if data:
                        fetched_players.append(data)
                        imported_Players_ids.append(pid)
                        print(f"imported player:", data['name'])

                except RestartSignal as rs:
                    # 🛑 Cancel execution
                    print(rs)
                    executor.shutdown(wait=False, cancel_futures=True)
                    
                    # ⏸ Pause globally
                    pause_event.clear()
                    wait_time = random.uniform(30, 60)
                    insert_players(fetched_players)
                    print(f"{len(fetched_players)} Players saved to database")
                    fetched_players = []
                    print(f"Pausing all threads for {wait_time:.2f}s...")
                    time.sleep(wait_time)  # Simulate full restart
                    print("Resuming all threads...")
                    pause_event.set()

                    continue  # Retry from top of while loop


                except Exception as e:
                    executor.shutdown(wait=False, cancel_futures=True)
                    print(f"Future error for player {pid}: {e}")
                    sys.exit(0)

        print(f"Total fetched so far: {len(fetched_players)} / {len(set(player_ids) - set(imported_Players_ids))}")
        attempt += 1

    print(f"\nSuccessfully fetched all {len(fetched_players)} players.")
    insert_players(fetched_players)
    return None
"""




Finsh the Database




"""
# Function to insert Player stats by Seasons

def insert_player_season_stats(player_data):
    session = SessionLocal()
    season_stats = [PlayerBySeasons(**stat) for stat in player_data]
    session.add_all(season_stats)
    session.commit()
    session.close()
    print("Inserted Season Stats")

def hash_mod_id(player_id, team_id, season_id):
    #season_int = int(season_id.replace('-', ''))
    raw = f"{player_id}{team_id}{season_id}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return int(hashed, 16) % (7**9)

def fetch_players_season_stats(id):
    player_info = playercareerstats.PlayerCareerStats(player_id=id)
    player_info_per = playercareerstats.PlayerCareerStats(player_id=id, per_mode36="PerGame")

    player_data = player_info.get_dict()
    player_data_per = player_info_per.get_dict()

    player_details = player_data["resultSets"][0]["rowSet"]
    player_details_per = player_data_per["resultSets"][0]["rowSet"]

    headers = player_data["resultSets"][0]["headers"]

    player_details_list = [dict(zip(headers, row)) for row in player_details]
    player_details_per_list = [dict(zip(headers, row)) for row in player_details_per]
    
    player_data = []

    def team_exists(teamID):
        if team_id is None:
            return False
        if session.query(Team).filter_by(id=teamID).first() == None:
            return False
        else:
            return True
    
    for player_details, player_details_per in zip(player_details_list, player_details_per_list):
        player_id = player_details.get('PLAYER_ID')
    
        team_id = player_details.get('TEAM_ID')
        
        if not team_exists(team_id):
            continue

        season = player_details.get('SEASON_ID')
        season_id = int(season.replace('-', ''))
        
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
            "field_goal_percentage":player_details.get('FG_PCT'),
            "three_point_percentage":player_details.get('FG3_PCT'),
            "free_throw_percentage":player_details.get('FT_PCT'),                                                         
        })

    return player_data

"""




Finsh the Database




"""

# Function to insert teams by seasons
def fetch_teams_by_seasons(Team_id):
    if session.query('team_by_seasons').filter_by(team_id=Team_id).all() == None:
        team_seasons_data = []
        last_25_seasons = fetch_seasons()
        for seasons in last_25_seasons:
            my_dict = {}
        insert_team_seasons(team_seasons_data)
        return None
    seasons = fetch_seasons()

    return None

def insert_team_seasons(team_seasons_data):
    session = SessionLocal()
    team_seasons = [TeamBySeasons(**team_season) for team_season in team_seasons_data]
    session.bulk_save_objects(team_seasons)
    session.commit()
    session.close()

'''
# Fill in the Teams Table
def load_Teams_table():
    team_id = [team[0] for team in teams]
    for id in team_id:
        team_stats = commonteamroster.CommonTeamRoster(team_id=id)
        team_data_frame = team_stats.get_data_frames()[0]
        print (team_data_frame)
    return None


# Fill in the players Table
nba_players = players.get_players()
processed_ids = {p.id for p in session.query(Player.id).all()}  # Track existing players
save_interval = 50  # Save every 50 players

def update_player(player_profile):
    """Update player details if any changes are detected."""
    existing_player = session.query(Player).filter_by(id=player_profile.get("PERSON_ID")).first()
    if existing_player:
        updated = False
        if existing_player.team != player_profile.get("TEAM_NAME"):
            existing_player.team = player_profile.get("TEAM_NAME")
            updated = True
        if existing_player.position != player_profile.get("POSITION"):
            existing_player.position = player_profile.get("POSITION")
            updated = True
        if updated:
            print(f"Updated player {existing_player.name} details in the database.")
    else:
        new_player = Player(
            id=player_profile.get("PERSON_ID"),
            name=player_profile.get("DISPLAY_FIRST_LAST"),
            position=player_profile.get("POSITION"),
            height=player_profile.get("HEIGHT"),
            weight=player_profile.get("WEIGHT"),
            birth_date=player_profile.get("BIRTHDATE"),
            nationality=player_profile.get("COUNTRY"),
            college=player_profile.get("SCHOOL"),
            is_active=player_profile.get("ROSTERSTATUS") == "Active",
            image=f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_profile.get('PERSON_ID')}.png",
            team=player_profile.get("TEAM_NAME")
        )
        session.add(new_player)
'''



# Example of fetching and inserting data for the 2023-24 season
def migrate_data():
    # Fetch and store data (terminates if error occurs)
    #teams = fetch_teams()
    #fetch_all_players(players)

    
    print("Teams and players data successfully loaded!")

    imported_Players_ids = [player.id for player in session.query(Player.id).all()]
    #print(imported_Players_ids)

    for id in imported_Players_ids:
        print(id)
        try:
            insert_player_season_stats(fetch_players_season_stats(id))
        except Exception as e:
            print(id)
            print(f"Error : {e}")
        print(f'imported player: {id} seasons')

    # Fetch teams and insert them into the database
    '''
    try:
        insert_seasons()
        insert_teams(teams)
    except Exception as e:
        print(f"Error: {e}")
    '''
    

# Run migration for the 2023-24 season
if __name__ == "__main__":
    migrate_data()
