import pandas as pd
import requests
import time
import re

try:
    df = pd.read_csv('out.csv')
except Exception as e:
    print("Failed to read out.csv:", e)
    exit(1)

if 'anilist' not in df.columns:
    print("CSV does not contain the 'anilist' column.")
    exit(1)

def extract_anilist_id(url):
    if isinstance(url, str):
        match = re.search(r'anilist\.co\/manga\/(\d{6})', url)
        if match:
            return match.group(1)
    return None

df['ID'] = df['anilist'].apply(extract_anilist_id)
df = df.dropna(subset=['ID'])

if 'type' not in df.columns or 'read' not in df.columns:
    print("CSV does not contain necessary columns.")
    exit(1)

status_mapping = {
    'Reading': 'CURRENT',
    'Completed': 'COMPLETED',
    'On-Hold': 'PAUSED',
    'Plan to Read': 'PLANNING',
    'Dropped': 'DROPPED'
}

url = "https://graphql.anilist.co"
access_token = 'YOUR_ACCESS_TOKEN'

mutation = """
mutation ($id: Int, $status: MediaListStatus, $progress: Int, $score: Float) {
  SaveMediaListEntry (mediaId: $id, status: $status, progress: $progress, score: $score) {
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

for index, row in df.iterrows():
    manga_id = row['ID']
    manga_type = row['type']
    read_chapter = round(row['read']) if pd.notna(row['read']) else 0
    rating = row['rating'] if 'rating' in row else None

    if manga_type not in status_mapping:
        print(f"Skipping manga ID {manga_id} due to unknown status: {manga_type}")
        continue

    status = status_mapping[manga_type]

    try:
        manga_id_int = int(manga_id)
    except ValueError:
        print(f"Invalid manga ID: {manga_id}, skipping.")
        continue

    variables = {"id": manga_id_int, "status": status, "progress": read_chapter}
    if pd.notna(rating):
        variables["score"] = float(rating)

    try:
        response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers, timeout=10)

        if response.status_code == 429:
            print("Rate limit exceeded, retrying...")
            time.sleep(10)
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
            print(f"Successfully added or updated {title} (ID: {manga_id_int}) with status {status}, chapter {read_chapter}, and score {rating} to your list.")
        elif 'errors' in json_response:
            print(f"Error adding manga ID {manga_id_int}: {json_response['errors']}")
        else:
            print(f"Failed to add or update manga ID {manga_id_int}. Response: {json_response}")
    else:
        print(f"GraphQL request failed for manga ID {manga_id_int} with status code {response.status_code}.")
        print(response.text)

    time.sleep(2)

print("Process completed.")
