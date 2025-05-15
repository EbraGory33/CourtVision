from nba_api.stats.static import teams
from nba_api.stats.library.data import TEAM_INFO
from nba_api.stats.endpoints import TeamInfoCommon
from nba_api.stats.library.http import NBAStatsHTTP
import json
import time

# Get all teams
nba_teams = teams.get_teams()

# List to store team data
all_teams_info = []
processed_ids = set()  # Track successfully processed team IDs
save_interval = 5  # Save every 5 teams

# Load previous progress if available
try:
    with open("nba_teams_info.json", "r") as f:
        all_teams_info = json.load(f)
        processed_ids = {t["id"] for t in all_teams_info}
        print(f"Resuming from {len(processed_ids)} teams already processed...")
except (FileNotFoundError, json.JSONDecodeError):
    print("No previous progress found. Starting fresh.")

# Fetch team details using team ID
for idx, team in enumerate(nba_teams):
    team_id = team["id"]
    team_name = team["full_name"]

    # Skip already processed teams
    if team_id in processed_ids:
        continue

    retries = 3  # Number of retries for failed requests
    print("team_id = " + str(team_id))
    print("team_name = " + str(team_name))
    while retries > 0:
        try:
            # Initialize TeamInfoCommon with the current team ID
            team_info = TeamInfoCommon(team_id=team_id, timeout=60)
            team_data = team_info.get_dict() #nba_response.get_data_sets()

            # Extract relevant data
            team_details = team_data["resultSets"][0]["rowSet"][0]
            headers = team_data["resultSets"][0]["headers"]

            # Map the response to the desired JSON structure
            team_profile = {
                "id": team_details[headers.index("TEAM_ID")],
                "name": team_details[headers.index("TEAM_NAME")],
                "abbreviation": team_details[headers.index("TEAM_ABBREVIATION")],
                "city": team_details[headers.index("TEAM_CITY")],
                "state": team_details[headers.index("TEAM_CONFERENCE")],
                "conference": team_details[headers.index("TEAM_CONFERENCE")],
                "division": team_details[headers.index("TEAM_DIVISION")],
                "founded": team_details[headers.index("MIN_YEAR")],
                'logo': TEAM_INFO.get(team['abbreviation'], {}).get('logo', None),  # Store image path or URL
                "players": [],  # You can fill this with player data if needed
                "stats": [],  # Fill with team stats if needed
                "home_games": [],  # Fill with game data if needed
                "away_games": []  # Fill with game data if needed
            }

            # Add team data to the list
            all_teams_info.append(team_profile)
            processed_ids.add(team_id)

            # Save progress every 5 teams
            if len(all_teams_info) % save_interval == 0:
                with open("nba_teams_info.json", "w") as f:
                    json.dump(all_teams_info, f, indent=4)
                print(f"Saved progress at {len(all_teams_info)}/{len(nba_teams)} teams...")

            # Sleep to avoid rate limits
            time.sleep(0.5)
            break  # Exit retry loop if successful

        except Exception as e:
            print(f"Error fetching {team_name}: {e}")
            retries -= 1
            time.sleep(5)  # Wait before retrying

# Final save after loop completes
with open("nba_teams_info.json", "w") as f:
    json.dump(all_teams_info, f, indent=4)

print(f"Successfully saved data for {len(all_teams_info)} teams.")



'''

def print_team_data(team_id):
    try:
        # Create an instance of TeamInfoCommon for a specific team_id
        
        team_info = TeamInfoCommon(team_id=team_id, timeout=60)
        team_data = team_info.get_dict()
        #print(f"Raw response: {team_data}")


        # Extract relevant data
        team_details = team_data["resultSets"][0]["rowSet"][0]
        headers = team_data["resultSets"][0]["headers"]

        # Convert to dictionary
        team_profile = dict(zip(headers, team_details))

        # Print formatted details
        for key, value in team_profile.items():
            print(f"{key}: {value}")
   
        # Check if we got a valid response
        if team_info.nba_response is None or not team_info.nba_response.get_data_sets():
            print(f"No data returned for team ID: {team_id}")
            return
        
        # Access the team info
        team_data = team_info.team_info_common[0]
        
        # Prepare a dictionary to map data points to readable keys
        headers = team_info.expected_data["TeamInfoCommon"]
        team_profile = dict(zip(headers, team_data))

        # Print the team profile
        print("Team Information:")
        for key, value in team_profile.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"Error fetching team data: {e}")


# Example: Print data for the Atlanta Hawks (team ID 1)
team_id = 1610612737  # Replace with the team ID you want to fetch
print_team_data(team_id)'''
