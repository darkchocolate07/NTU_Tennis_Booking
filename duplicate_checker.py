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




check_duplicates_in_file("Session_A_Court_Allocation.txt")
check_duplicates_in_file("Session_B_Court_Allocation.txt")
check_duplicates_in_file("Session_C_Court_Allocation.txt")
check_duplicates_in_file("Ungrouped_Players.txt")