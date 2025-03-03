import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the folder path containing the CSV files (Update this to your actual path)
folder_path = "Fri1"

# Get all CSV files that end with '_JV.csv' in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith("_JV.csv")]

# Dictionary with cell metadata
cells = {
    "ID": [10, 15, 12, 3, 8, 9, 6, 5, 4, 11, 12, 2, 7, 13, 1, 14],
    "W (µm)": [24, 24, 24, 24, 24, 24, 24, 24, 24, 14, 24, 36, 54, 104, 204, 404],
    "N": [0, 5, 20, 50, 100, 200, 400, 600, 800, 20, 20, 20, 20, 20, 20, 20],
    "Metal Coverage (%)": [0, 1, 3, 8, 15, 30, 60, 90, 100, 2, 3, 5, 7, 13, 26, 51]
}

# Convert dictionary to a DataFrame for easier lookup
cell_data = pd.DataFrame(cells)

# Lists to store extracted values
jmpp_values = []
isc_values = []
metal_coverage_values = []
num_fingers_values = []

# Loop through each CSV file and process the data
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)

    # Convert filename to lowercase and check if it's "light"
    if "light" not in file_name.lower():
        print(f"Skipping file: {file_name} (Not 'light')")
        continue  # Skip non-light files

    try:
        # Extract cell ID from filename (assuming format like "Fri1-10-Light_JV.csv")
        cell_id = int(''.join(filter(str.isdigit, file_name.split('-')[1])))  # Extract numeric part after 'Fri1-'

        # Read the CSV file
        light_data = pd.read_csv(file_path, header=None)

        # Extract `Jmpp (mA/sq cm)` from the ninth row (row index 8, second column index 1)
        jmpp = pd.to_numeric(light_data.iloc[8, 1], errors='coerce')

        # Extract `Isc (mA)` from the fifth row (row index 4, second column index 1)
        isc = pd.to_numeric(light_data.iloc[4, 1], errors='coerce')

        # Get corresponding Metal Coverage and Number of Fingers (N) for this ID
        metal_coverage = cell_data.loc[cell_data["ID"] == cell_id, "Metal Coverage (%)"].values
        num_fingers = cell_data.loc[cell_data["ID"] == cell_id, "N"].values

        # Ensure valid data before appending
        if not np.isnan(jmpp) and not np.isnan(isc) and len(metal_coverage) > 0 and len(num_fingers) > 0:
            jmpp_values.append(jmpp)
            isc_values.append(isc)
            metal_coverage_values.append(metal_coverage[0])
            num_fingers_values.append(num_fingers[0])

        print(f"Processed: {file_name} | Cell ID: {cell_id} | Jmpp: {jmpp:.3f} mA/sq cm | Isc: {isc:.3f} mA | Metal Coverage: {metal_coverage[0]}% | Fingers: {num_fingers[0]}")

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

# ---- PLOT Jmpp vs. Metal Coverage ----
plt.figure(figsize=(8, 6))
plt.scatter(metal_coverage_values, jmpp_values, color='red', marker='o', label="Jmpp vs. Metal Coverage")

# Labels and title
plt.xlabel("Metal Coverage (%)", fontsize=14)
plt.ylabel("Jmpp (mA/sq cm)", fontsize=14)
plt.title("Jmpp vs. Metal Coverage", fontsize=16)

# Adjust tick font sizes
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Add grid and legend
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', linewidth=0.5)

# Show the plot
plt.show()

# ---- PLOT Jmpp vs. Number of Fingers ----
plt.figure(figsize=(8, 6))
plt.scatter(num_fingers_values, jmpp_values, color='green', marker='s', label="Jmpp vs. Number of Fingers")

# Labels and title
plt.xlabel("Number of Fingers", fontsize=14)
plt.ylabel("Jmpp (mA/sq cm)", fontsize=14)
plt.title("Jmpp vs. Number of Fingers", fontsize=16)

# Adjust tick font sizes
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Add grid and legend
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', linewidth=0.5)

# Show the plot
plt.show()

# ---- PLOT Isc vs. Metal Coverage ----
plt.figure(figsize=(8, 6))
plt.scatter(metal_coverage_values, isc_values, color='blue', marker='^', label="Isc vs. Metal Coverage")

# Labels and title
plt.xlabel("Metal Coverage (%)", fontsize=14)
plt.ylabel("Isc (mA)", fontsize=14)
plt.title("Isc vs. Metal Coverage", fontsize=16)

# Adjust tick font sizes
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Add grid and legend
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', linewidth=0.5)

# Show the plot
plt.show()
