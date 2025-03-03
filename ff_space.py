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
}

# Convert dictionary to a DataFrame for easier lookup
cell_data = pd.DataFrame(cells)

# Lists to store extracted values
fill_factor_values = []
pitch_values = []

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

        # Extract Fill Factor (`FF (%)`) from metadata (11th row → row index **10**, second column → index **1**)
        fill_factor = pd.to_numeric(light_data.iloc[10, 1], errors='coerce')  # Row index 10, second column

        # Get corresponding Width (W) and Number of Fingers (N)
        row = cell_data.loc[cell_data["ID"] == cell_id]
        if row.empty:
            print(f"Warning: No metadata found for Cell ID {cell_id}. Skipping.")
            continue

        W = row["W (µm)"].values[0]
        N = row["N"].values[0]

        # Calculate Pitch = W / N (avoid division by zero)
        pitch = W / N if N > 0 else np.nan

        # Ensure valid data before appending
        if not np.isnan(fill_factor) and not np.isnan(pitch):
            fill_factor_values.append(fill_factor)
            pitch_values.append(pitch)

        print(f"Processed: {file_name} | Cell ID: {cell_id} | Fill Factor: {fill_factor:.3f}% | Pitch: {pitch:.3f} µm")

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

# ---- LINEAR FIT ----
# Perform a linear regression (y = mx + b)
if len(pitch_values) > 1:  # Only fit if we have enough data points
    slope, intercept = np.polyfit(pitch_values, fill_factor_values, 1)
    pitch_fit = np.linspace(min(pitch_values), max(pitch_values), 100)  # Generate x values for the fit
    fill_factor_fit = slope * pitch_fit + intercept  # Compute y values for the fit

# ---- PLOT Fill Factor vs. Pitch (LINEAR) ----
plt.figure(figsize=(8, 6))
plt.scatter(pitch_values, fill_factor_values, color='blue', marker='o', label="Fill Factor vs. Pitch")

# Plot the linear fit if enough data points exist
if len(pitch_values) > 1:
    plt.plot(pitch_fit, fill_factor_fit, linestyle='-', color='red', label=f"Linear Fit: y = {slope:.2f}x + {intercept:.2f}")

# Labels and title
plt.xlabel("Finger Spacing (Pitch) [µm]", fontsize=14)
plt.ylabel("Fill Factor (FF %) ", fontsize=14)
plt.title("Fill Factor vs. Finger Spacing (Linear Scale)", fontsize=16)

# Adjust tick font sizes
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Add grid and legend
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', linewidth=0.5)

# Show the plot
plt.show()
