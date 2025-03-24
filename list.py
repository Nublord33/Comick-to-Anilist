import pandas as pd
import re

df = pd.read_csv('data.csv')

df.columns = df.columns.str.strip()

print("Columns in CSV:", df.columns)

# Filter out rows where all three of the relevant columns are NaN
filtered_df = df[df['anilist'].notna() | df['mal'].notna() | df['mangaupdates'].notna()]

print("Which tracker do you use?")
print("1) Anilist")
print("2) MAL")
print("3) Manga Updates")

choice = input("Enter the number corresponding to your choice: ")

def extract_anilist_id(url):
    match = re.search(r'anilist\.co\/manga\/(\d{6})', url)
    if match:
        return match.group(1)
    return None

more_info = input("Would you like some more info or nah? (y/n): ").lower()

extra_columns = []

if more_info == 'y':
    print("Choose the extra info you'd like to include (enter the corresponding numbers, separated by commas):")
    print("1) hid")
    print("2) type")
    print("3) rating")
    print("4) read")
    print("5) last_read")
    print("6) synonyms")
    print("example output: 1, 2, 3")
    selected_columns = input("Enter your choices: ").split(',')
    
    if "1" in selected_columns:
        extra_columns.append('hid')
    if "2" in selected_columns:
        extra_columns.append('type')
    if "3" in selected_columns:
        extra_columns.append('rating')
    if "4" in selected_columns:
        extra_columns.append('read')
    if "5" in selected_columns:
        extra_columns.append('last_read')
    if "6" in selected_columns:
        extra_columns.append('synonyms')

# Select the appropriate column based on the user's choice
if choice == '1':  # Anilist
    selected_columns = filtered_df[['title', 'anilist'] + extra_columns].dropna(subset=['anilist'])
    selected_columns['ID'] = selected_columns['anilist'].apply(extract_anilist_id)
    print("Displaying 'title', 'anilist', and 'ID' columns (with no empty 'anilist' values):")
elif choice == '2':  # MAL
    selected_columns = filtered_df[['title', 'mal'] + extra_columns].dropna(subset=['mal'])
    print("Displaying 'title' and 'mal' columns (with no empty 'mal' values):")
elif choice == '3':  # Manga Updates
    selected_columns = filtered_df[['title', 'mangaupdates'] + extra_columns].dropna(subset=['mangaupdates'])
    print("Displaying 'title' and 'mangaupdates' columns (with no empty 'mangaupdates' values):")
else:
    print("Invalid choice! Please select a valid option.")
    selected_columns = pd.DataFrame()

# Save data 
if not selected_columns.empty:
    selected_columns.to_csv('out.csv', index=False, sep='\t')
    print("Data saved to out.csv!")
