import pandas as pd



rallyData = pd.read_excel(r'./Week 7 Rally Registration Form (Responses).xlsx')
rallyData['Tele Handle'] = rallyData['Tele Handle'].astype(str).apply(lambda x: '@' + x if not x.startswith('@') else x)

priority_members=['@Oomint', '@thiriiiiiii', '@garg0003', '@ujjwal24agarwal', 
    '@ArttuHannila', '@aribruhhh', '@atsh1220', 
    '@jingjonglingmong', '@SwatowAnthony', '@paella_ella', 
    '@Ananya_Jayanty', '@aladynnn', '@vverawen', 
    '@rohanR25', '@alexwpribadi', '@KrishSaraf', '@jonnyquek']


# Record the original order of the DataFrame
rallyData['original_order'] = rallyData.index
# Set the smallest possible timestamp for priority members
smallest_possible_timestamp = pd.Timestamp('1970-01-01 00:00:00')
rallyData.loc[rallyData['Tele Handle'].isin(priority_members), 'Timestamp'] = smallest_possible_timestamp

# Reorder the DataFrame based on the Timestamp column
rallyData = rallyData.sort_values(by=['Timestamp', 'original_order'])
rallyData.reset_index(drop=True, inplace=True)
rallyData.drop(columns=['original_order'], inplace=True)

# Reset the index after sorting
rallyData.reset_index(drop=True, inplace=True)
rallyData.loc[:, 'Skill'] = rallyData['Your Skill Level'].str.split().str[0]


session_column = 'Which session would you like to attend? (can select multiple, you\'ll be allocated ONE based on availability)'
session_a_tuesday = rallyData[rallyData[session_column].str.contains('Session A', na=False)].reset_index()
session_b_tuesday = rallyData[rallyData[session_column].str.contains('Session B', na=False)].reset_index()
session_c_thursday = rallyData[rallyData[session_column].str.contains('Session C', na=False)].reset_index()


def sort_groups_by_timestamp_sum(groups):
    # Calculate cumulative sum of timestamps for each group and sort
    groups_sorted = sorted(groups, key=lambda group: group['Timestamp'].astype('int64').sum())
    return groups_sorted

def session_court_allocation(df, flag):
    

    court_capacity = 4
    max_coaching = 16

    groups = []
    grouped_names = []  # List to track grouped players

    if flag:
        # Allocate Coaching first for sessions with coaching
        coaching_needed = df[df['Your Skill Level'].str.contains('Coaching') & (~df['Name'].isin(grouped_names))].head(max_coaching)
        groups.append(coaching_needed)
        grouped_names.extend(coaching_needed['Name'].tolist())  # Mark coaching as grouped

    df = df[~df['Your Skill Level'].str.contains('Coaching')].reset_index(drop=True)

    # Function to add players to a group
    def add_players_to_group(current_group, group, court_capacity):
        for player in group.iterrows():
            if len(current_group) < court_capacity:
                # Check if the player has already been grouped
                if player[1]['Name'] not in grouped_names:
                    current_group.append(player[1])
                    grouped_names.append(player[1]['Name'])  # Mark as grouped
            else:
                break
        return current_group

    # Step 2: Iterate through the rows and group players based on their skill level
    for index, row in df.iterrows():

        if row['Name'] in grouped_names:
            continue  # Skip this player if they've already been grouped

        # Initialize a new current_group
        current_group = [row]
        grouped_names.append(row['Name'])  # Mark as grouped

        # Grouping logic
        if row['Skill'] == 'Advanced':
            # Find additional Advanced or Intermediate players to fill the group
            eligible_players = df[(df['Skill'].isin(['Advanced', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
            current_group = add_players_to_group(current_group, eligible_players, court_capacity)

        elif row['Skill'] == 'Beginner':
            # Find additional Beginner or Intermediate players to fill the group
            eligible_players = df[(df['Skill'].isin(['Beginner', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
            current_group = add_players_to_group(current_group, eligible_players, court_capacity)

        elif row['Skill'] == 'Intermediate':
            # Intermediate can group with Advanced first if there are remaining Advanced players
            eligible_players = df[(df['Skill'].isin(['Advanced', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
            current_group = add_players_to_group(current_group, eligible_players, court_capacity)

            # If still not full, fill with Beginner players
            if len(current_group) < court_capacity:
                eligible_players = df[(df['Skill'].isin(['Beginner', 'Intermediate'])) & (~df['Name'].isin(grouped_names))]
                current_group = add_players_to_group(current_group, eligible_players, court_capacity)

        # Step 3: Finalize the group
        groups.append(pd.DataFrame(current_group))

    for i, group in enumerate(groups):
        print(f"Group {i + 1}:")
        print(group[['Name', 'Skill']])
        print()  # Add an empty line for better readability
    
    return groups




def save_court_allocation_to_file(session_name, court_allocation, court_count):
    # Define the file name based on the session name
    file_name = f"Session_{session_name}_Court_Allocation.txt"
    
    # Open the file to write the groups
    with open(file_name, "w") as file:
        # Loop through the groups and write only up to court_count groups to the file
        for i, group in enumerate(court_allocation[:court_count]):
            if all(group['Skill'] == 'New'):
                group_name = 'Coaching'
            elif all(group['Skill'] == 'Advanced'):
                group_name = 'Advanced'
            elif all(group['Skill'] == 'Beginner'):
                group_name = 'Beginner'
            elif all(group['Skill'] == 'Intermediate'):
                group_name = 'Intermediate'
            elif set(group['Skill']) == {'Beginner', 'Intermediate'}:
                group_name = 'Beginner/Intermediate'
            else:
                group_name = 'Advanced/Intermediate'

            # Write the group name and members to the file
            file.write(f"Group {i+1} ({group_name}):\n")
            for name in group['Name']:
                file.write(f"{name:<30}\n")  # Write names and skills to file
            file.write("\n\n")  # Add some spacing between groups
    
    # Print confirmation message
    print(f"Saved {court_count} groups to '{file_name}'")

    grouped_players = []
    for group in court_allocation[:court_count]:
        grouped_players.extend(group['Name'].tolist())
    
    return grouped_players


coaching_a_response = input("Will session A have coaching? (yes/no): ").strip().lower()
# Determine the flag for session A based on user input
if coaching_a_response == "yes":
    flag_a = True
else:
    flag_a = False

coaching_b_response = input("Will session B have coaching? (yes/no): ").strip().lower()
# Determine the flag for session A based on user input
if coaching_b_response == "yes":
    flag_b = True
else:
    flag_b = False


coaching_c_response = input("Will session C have coaching? (yes/no): ").strip().lower()
# Determine the flag for session A based on user input
if coaching_c_response == "yes":
    flag_c = True
else:
    flag_c = False


# Input the number of courts for each session
A_count = int(input("How many courts for session A? "))
B_count = int(input("How many courts for session B? "))
C_count = int(input("How many courts for session C? "))

# Create a list of sessions with their court counts
sessions = [
    ('A', session_a_tuesday.copy(), True, A_count),
    ('B', session_b_tuesday.copy(), True, B_count),
    ('C', session_c_thursday.copy(), False, C_count)
]

# Sort sessions by the number of courts in descending order
sessions.sort(key=lambda x: x[3], reverse=True)

# List to hold all grouped players
all_grouped_players = []

# Loop through sessions based on sorted order
for session_name, session_df, flag, court_count in sessions:
    # Perform the court allocation
    court_allocation = session_court_allocation(session_df, flag)
    grouped_players = save_court_allocation_to_file(session_name, court_allocation, court_count)
    
    # Extend the list of all grouped players
    all_grouped_players.extend(grouped_players)
    
    # Remove grouped players from subsequent sessions
    for i in range(len(sessions)):
        sessions[i] = (sessions[i][0], sessions[i][1][~sessions[i][1]['Name'].isin(grouped_players)], sessions[i][2], sessions[i][3])

# Combine all the session DataFrames
# all_players = pd.concat([session[1] for session in sessions])
all_players=rallyData
# Get ungrouped players by filtering out those in all_grouped_players
ungrouped_players_df = all_players[~all_players['Name'].isin(all_grouped_players)]


# Save ungrouped players to a text file
marker = "(Priority)"
with open("Ungrouped_Players.txt", "w") as file:
    file.write("Ungrouped Players:\n")
    for _, player in ungrouped_players_df.iterrows():
        # Check if the timestamp is the priority timestamp and add marker if true
        name_with_marker = f"{player['Name']}"
        if player['Timestamp'] == pd.Timestamp('1970-01-01 00:00:00'):
            name_with_marker += f" {marker}"  # Append marker to the name

        # Write name, skill, session, and marker (if applicable) to the file
        file.write(f"Name: {name_with_marker}, Skill: {player['Skill']}, Session: {player[session_column]}\n")

print(f"Saved ungrouped players to 'Ungrouped_Players.txt'")




import os

def check_duplicates_in_file(file_name):
    """
    Reads the specified file, extracts names, and checks for duplicates.
    """
    if not os.path.exists(file_name):
        print(f"File {file_name} does not exist.")
        return
    
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    # Extract names from the file (assuming each name starts after the group label)
    names = []
    for line in lines:
        if line.strip() and not line.startswith("Group") and not line.startswith("Ungrouped Players"):
            names.append(line.strip())
    
    # Check for duplicates
    duplicates = [name for name in set(names) if names.count(name) > 1]
    if duplicates:
        print(f"Warning: Duplicate names found in {file_name}:")
        for duplicate in duplicates:
            print(f" - {duplicate}")
    else:
        print(f"No duplicate names found in {file_name}.")


check_duplicates_in_file
