import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from nba_api.stats.library.data import teams
from nba_api.stats.library.data import players
from nba_api.stats.endpoints import TeamInfoCommon
from nba_api.stats.endpoints import CommonPlayerInfo
from sqlalchemy.orm import Session
from courtVision_server.app.db.database import SessionLocal
from courtVision_server.app.models.models import *
from datetime import datetime
import json
import sys
import os
from requests.exceptions import ReadTimeout
import random
import threading

# Get the absolute path of the project root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

session = SessionLocal()

# Function to insert Seasons
def fetch_seasons():
    seasons = []
    for id,year in enumerate(range(2000, 2025)):
        seasons.append({
            "id": id,
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


'''
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

def fetch_players_by_seasons():
    seasons = fetch_seasons()
    return None
'''
'''
# Fill in the Teams Table
def load_Teams_table():
    team_id = [team[0] for team in teams]
    for id in team_id:
        team_stats = commonteamroster.CommonTeamRoster(team_id=id)
        team_data_frame = team_stats.get_data_frames()[0]
        print (team_data_frame)
    return None
'''

'''
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

def fetch_and_store_players():
    for idx, player in enumerate(nba_players):
        player_id = player["id"]
        player_name = player["full_name"]

        retries = 3
        while retries > 0:
            try:
                player_info = CommonPlayerInfo(player_id=player_id, timeout=60)
                player_data = player_info.get_dict()
                player_details = player_data["resultSets"][0]["rowSet"][0]
                headers = player_data["resultSets"][0]["headers"]
                player_profile = dict(zip(headers, player_details))

                update_player(player_profile)
                processed_ids.add(player_id)

                if len(processed_ids) % save_interval == 0:
                    session.commit()
                    print(f"Saved {len(processed_ids)} players to the database...")

                time.sleep(0.5)  # Sleep to avoid rate limits
                break  # Exit retry loop if successful

            except Exception as e:
                print(f"Error fetching {player_name}: {e}")
                retries -= 1
                time.sleep(5)  # Wait before retrying

    session.commit()
    print(f"Successfully saved {len(processed_ids)} players to the database.")
    session.close()

fetch_and_store_players()






try:
    with open("nba_players_info.json", "r") as f:
        all_players_info = json.load(f)
except FileNotFoundError:
    print("Error: 'nba_players_info.json' not found. Starting fresh.")
except json.JSONDecodeError:
    print("Error: Failed to decode 'nba_players_info.json'. The file might be corrupted.")

try:
    with open("nba_teams_info.json", "r") as f:
        all_teams_info = json.load(f)
except FileNotFoundError:
    print("Error: 'nba_teams_info.json' not found.")
except json.JSONDecodeError:
    print("Error: Failed to decode 'nba_teams_info.json'. The file might be corrupted.")
'''



def fetch_teams_from_db():
    session = SessionLocal()
    teams = session.query(Team.id).all()
    session.close()
    
    # Convert list of tuples into a set of IDs
    return {team[0] for team in teams}



# Example of fetching and inserting data for the 2023-24 season
def migrate_data():
    # Fetch and store data (terminates if error occurs)
    #teams = fetch_teams()
    all_players = fetch_all_players(players)

    print("Teams and players data successfully loaded!")
    
    # Fetch teams and insert them into the database
    """
    try:
        insert_seasons()
        insert_teams(teams)
    except Exception as e:
        print(f"Error: {e}")
    """
    # Fetch players and insert them into the database

    # If you have player stats and team stats, you can call the relevant functions here.
    # Example:
    # player_stats_data = fetch_player_stats()
    # insert_player_stats(player_stats_data)
    
    # Example for team stats data (you'd need to write the `fetch_team_stats` function similarly)
    # team_stats_data = fetch_team_stats()
    # insert_team_stats(team_stats_data)

# Run migration for the 2023-24 season
if __name__ == "__main__":
    migrate_data()
