from nba_api.stats.static import players
from nba_api.stats.endpoints import CommonPlayerInfo
import json
import time

# Get all players
nba_players = players.get_players()

# List to store player data
all_players_info = []
processed_ids = set()  # Track successfully processed player IDs
save_interval = 50  # Save every 50 players

# Load previous progress if available
try:
    with open("nba_players_info.json", "r") as f:
        all_players_info = json.load(f)
        processed_ids = {p["PERSON_ID"] for p in all_players_info}
        print(f"Resuming from {len(processed_ids)} players already processed...")
except (FileNotFoundError, json.JSONDecodeError):
    print("No previous progress found. Starting fresh.")

# Fetch player details using player ID
for idx, player in enumerate(nba_players):
    player_id = player["id"]
    player_name = player["full_name"]

    # Skip already processed players
    if player_id in processed_ids:
        continue

    retries = 3  # Number of retries for failed requests
    while retries > 0:
        try:
            # Fetch player details with increased timeout
            player_info = CommonPlayerInfo(player_id=player_id, timeout=60)
            player_data = player_info.get_dict()

            # Extract relevant data
            player_details = player_data["resultSets"][0]["rowSet"][0]
            headers = player_data["resultSets"][0]["headers"]

            # Convert to dictionary
            player_profile = dict(zip(headers, player_details))
            all_players_info.append(player_profile)
            processed_ids.add(player_id)

            # Save progress every 50 players
            if len(all_players_info) % save_interval == 0:
                with open("nba_players_info.json", "w") as f:
                    json.dump(all_players_info, f, indent=4)
                print(f"Saved progress at {len(all_players_info)}/{len(nba_players)} players...")

            # Sleep to avoid rate limits
            time.sleep(0.5)
            break  # Exit retry loop if successful

        except Exception as e:
            print(f"Error fetching {player_name}: {e}")
            retries -= 1
            time.sleep(5)  # Wait before retrying

# Final save after loop completes
with open("nba_players_info.json", "w") as f:
    json.dump(all_players_info, f, indent=4)

print(f"Successfully saved data for {len(all_players_info)} players.")