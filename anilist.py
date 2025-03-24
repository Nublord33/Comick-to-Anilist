
import pandas as pd
import requests
import time

try:
    df = pd.read_csv('out.csv', sep='\t')
except Exception as e:
    print("Failed to read out.csv:", e)
    exit(1)

if 'ID' not in df.columns:
    print("CSV does not contain the 'ID' column.")
    exit(1)

ids = df['ID'].dropna().unique()
if len(ids) == 0:
    print("No manga IDs found in CSV.")
    exit(1)

url = "https://graphql.anilist.co"
access_token = "Please put your token here /\(T-T)"

mutation = """
mutation ($id: Int) {
  SaveMediaListEntry (mediaId: $id, status: CURRENT) {
    id
    media {
      title {
        romaji
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

def handle_rate_limit(response):
    if response.status_code == 429:
        print("Rate limit exceeded, retrying in 10 seconds...")
        time.sleep(2)
        return True
    return False

for manga_id in ids:
    try:
        manga_id_int = int(manga_id)
    except ValueError:
        print(f"Invalid manga ID: {manga_id}, skipping.")
        continue

    variables = {"id": manga_id_int}

    try:
        response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers, timeout=10)
        
        if handle_rate_limit(response):
            response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers, timeout=10)
    except Exception as e:
        print(f"Request failed for manga ID {manga_id_int}: {e}")
        continue

    if response.status_code == 200:
        try:
            json_response = response.json()
        except Exception as e:
            print(f"Failed to parse JSON for manga ID {manga_id_int}: {e}")
            continue

        if 'data' in json_response and json_response['data'].get('SaveMediaListEntry'):
            media_entry = json_response['data']['SaveMediaListEntry']
            media_info = media_entry.get('media', {})
            title = media_info.get('title', {}).get('romaji', "Unknown Title")
            print(f"Successfully added {title} (ID: {manga_id_int}) to your list.")
        elif 'errors' in json_response:
            print(f"Error adding manga ID {manga_id_int}: {json_response['errors']}")
        else:
            print(f"Failed to add manga ID {manga_id_int}. Response: {json_response}")
    else:
        print(f"GraphQL request failed for manga ID {manga_id_int} with status code {response.status_code}.")
        print(response.text)
    
    time.sleep(2)

# this probably does some weird shit that I dont know abt run at your own risk and patience since this is helllllllllaaa slow
