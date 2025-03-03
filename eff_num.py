import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the folder path containing the CSV files
folder_path = os.path.expanduser("Fri1")

# Get all CSV files that end with '_JV.csv' in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith("_JV.csv")]

# Dictionary with cell metadata
cells = {
    "ID": [10, 15, 12, 3, 8, 9, 6, 5, 4, 11, 12, 2, 7, 13, 1, 14],
    "W (µm)": [24, 24, 24, 24, 24, 24, 24, 24, 24, 14, 24, 36, 54, 104, 204, 404],
    "N": [0, 5, 20, 50, 100, 200, 400, 600, 800, 20, 20, 20, 20, 20, 20, 20],  # Number of Fingers
    "Metal Coverage (%)": [0, 1, 3, 8, 15, 30, 60, 90, 100, 2, 3, 5, 7, 13, 26, 51]
}

# Convert dictionary to a DataFrame for easier lookup
cell_data = pd.DataFrame(cells)

# Lists to store extracted values
efficiency_values = []
num_fingers_values = []

# Loop through each CSV file and process the data
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)

    # Convert filename to lowercase and check if it's "light"
    file_name_lower = file_name.lower()
    if "light" not in file_name_lower:
        print(f"Skipping file: {file_name} (Not 'light')")
        continue  # Skip non-light files

    try:
        # Extract cell ID from filename (assuming format like "Fri1-10-Light_JV.csv")
        cell_id = int(''.join(filter(str.isdigit, file_name.split('-')[1])))  # Extracts numeric part after 'Fri1-'

        # Read the CSV file
        light_data = pd.read_csv(file_path, header=None)

        # Extract Efficiency (`PCE (%)`) from metadata (12th row → row index **11**, second column → index **1**)
        efficiency = pd.to_numeric(light_data.iloc[11, 1], errors='coerce')  # Row index 11, second column

        # Convert efficiency to positive if negative
        if not np.isnan(efficiency):
            efficiency = -efficiency  # Multiply by -1 to make it positive

        # Get corresponding Number of Fingers for this ID
        num_fingers = cell_data.loc[cell_data["ID"] == cell_id, "N"].values

        # Ensure valid data before appending
        if not np.isnan(efficiency) and len(num_fingers) > 0:
            efficiency_values.append(efficiency)
            num_fingers_values.append(num_fingers[0])

        print(f"Processed: {file_name} | Cell ID: {cell_id} | Efficiency: {efficiency:.3f}% | Num Fingers: {num_fingers[0]}")

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

# ---- PLOT Efficiency vs. Number of Fingers ----
plt.figure(figsize=(8, 6))
plt.scatter(num_fingers_values, efficiency_values, color='red', marker='o', label="Efficiency vs. Number of Fingers")
#plt.plot(num_fingers_values, efficiency_values, linestyle='--', color='black', alpha=0.6)  # Connect points with a dashed line

# Labels and title
plt.xlabel("Number of Fingers (N)", fontsize=14)
plt.ylabel("Efficiency (PCE %) ", fontsize=14)
plt.title("Efficiency vs. Number of Fingers", fontsize=16)

# Adjust tick font sizes
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Add grid and legend
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', linewidth=0.5)

# Show the plot
plt.show()
