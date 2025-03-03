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
    "Metal Coverage (%)": [0, 1, 3, 8, 15, 30, 60, 90, 100, 2, 3, 5, 7, 13, 26, 51]
}

# Convert dictionary to a DataFrame for easier lookup
cell_data = pd.DataFrame(cells)

# Lists to store extracted values
r_s_values = []
efficiency_values = []
metal_coverage_values = []

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
        cell_id = int(''.join(filter(str.isdigit, file_name.split('-')[1])))  # Extract numeric part after 'Fri1-'

        # Read the CSV file
        light_data = pd.read_csv(file_path, header=None)

        # Extract Efficiency (%) from the 12th row (row index 11, second column index 1) and make it positive
        efficiency = pd.to_numeric(light_data.iloc[11, 1], errors='coerce') * -1  # Flip sign to make efficiency positive

        # Extract IV Data (Voltage & Current) - skipping the first 12 lines
        iv_data = light_data.iloc[12:].reset_index(drop=True)

        # Convert columns to numeric values, handling errors
        iv_data.iloc[:, 0] = pd.to_numeric(iv_data.iloc[:, 0], errors='coerce')
        iv_data.iloc[:, 1] = pd.to_numeric(iv_data.iloc[:, 1], errors='coerce')

        # Drop rows with NaN values (if any non-numeric rows exist)
        iv_data = iv_data.dropna()

        # Extract voltage and current as NumPy arrays
        voltage = iv_data.iloc[:, 0].values
        current = iv_data.iloc[:, 1].values

        # Compute dynamic resistance r_d = dV/dI
        dV = np.diff(voltage)
        dI = np.diff(current)

        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            r_d = np.where(dI != 0, dV / dI, np.inf)  # Handle cases where dI = 0

        # Estimate R_s (Series Resistance) from the high forward bias region (V > 0.4)
        high_forward_indices = np.where(voltage[:-1] > 0.4)[0]
        if len(high_forward_indices) > 0:
            R_s = np.mean(r_d[high_forward_indices])  # Approximate R_s as avg in high V
        else:
            R_s = None  # No high voltage data

        # Get corresponding Metal Coverage for this ID
        metal_coverage = cell_data.loc[cell_data["ID"] == cell_id, "Metal Coverage (%)"].values

        # Ensure valid data before appending
        if R_s is not None and not np.isnan(R_s) and not np.isnan(efficiency) and len(metal_coverage) > 0:
            r_s_values.append(R_s)
            efficiency_values.append(efficiency)
            metal_coverage_values.append(metal_coverage[0])

        print(f"Processed: {file_name} | Cell ID: {cell_id} | R_s: {R_s:.3f} Ω | Efficiency: {efficiency:.3f}% | Metal Coverage: {metal_coverage[0]}%")

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

# ---- PLOT R_s vs. Efficiency ----
plt.figure(figsize=(8, 6))
plt.scatter(r_s_values, efficiency_values, color='blue', marker='^', label="R_s vs. Efficiency")

# Labels and title
plt.xlabel("Series Resistance (R_s) [Ω]", fontsize=14)
plt.ylabel("Efficiency (%)", fontsize=14)
plt.title("Series Resistance vs. Efficiency", fontsize=16)

# Adjust tick font sizes
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Add grid and legend
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', linewidth=0.5)

# Show the plot
plt.show()
