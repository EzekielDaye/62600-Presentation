import os
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np


cells = {
    "ID": [10, 15, 12, 3, 8, 9, 6, 5, 4, 11, 12, 2, 7, 13, 1, 14],
    "W (µm)": [24, 24, 24, 24, 24, 24, 24, 24, 24, 14, 24, 36, 54, 104, 204, 404],
    "N": [0, 5, 20, 50, 100, 200, 400, 600, 800, 20, 20, 20, 20, 20, 20, 20],
    "Metal Coverage (%)": [0, 1, 3, 8, 15, 30, 60, 90, 100, 2, 3, 5, 7, 13, 26, 51]
}

# Convert to Pandas DataFrame for easier manipulation
cell_data = pd.DataFrame(cells)

# Define the folder path containing the CSV files
folder_path = os.path.expanduser("Fri1")

# Get all CSV files that end with '_JV.csv' in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith("_JV.csv")]

# Loop through each CSV file and process the data
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)

    # Convert filename to lowercase and check for "dark" or "light"
    file_name_lower = file_name.lower()
    if "dark" in file_name_lower:
        plot_type = "semi-log"
    elif "light" in file_name_lower:
        plot_type = "linear"
    else:
        print(f"Skipping file: {file_name} (No 'dark' or 'light' in name)")
        continue  # Skip files without "dark" or "light"

    try:
        # Read the CSV file
        dark_data = pd.read_csv(file_path, header=None)

        # Extract metadata from rows 1-11
        metadata_keys = [
            "Pad Area (sq cm)", "Voc (V)", "Isc (A)", "Jsc (mA/sq cm)",
            "Vmpp (V)", "Impp (A)", "Jmpp (mA/sq cm)", "Pmax (mW/sq cm)",
            "FF (%)", "PCE (%)"
        ]

        # Convert metadata values to numeric, handling errors
        metadata_values = pd.to_numeric(dark_data.iloc[:10, 1], errors='coerce').values
        metadata = {key: value for key, value in zip(metadata_keys, metadata_values)}

        # Skip the first 12 rows and extract IV data
        iv_data = dark_data.iloc[12:].reset_index(drop=True)

        # Convert columns to numeric values, handling errors
        iv_data.iloc[:, 0] = pd.to_numeric(iv_data.iloc[:, 0], errors='coerce')
        iv_data.iloc[:, 1] = pd.to_numeric(iv_data.iloc[:, 1], errors='coerce')

        # Drop rows with NaN values (if any non-numeric rows exist)
        iv_data = iv_data.dropna()

        # Extract voltage and current as NumPy arrays
        voltage = iv_data.iloc[:, 0].values
        current = iv_data.iloc[:, 1].values

        # Print confirmation message
        print(f"Processing file: {file_name} ({plot_type} plot)")

        # ---- CONDITIONAL PLOTTING ----
        plt.figure(figsize=(8, 6))

        if plot_type == "linear":
            plt.plot(voltage, current, marker='o', linestyle='-', label=f"{file_name} IV Curve")
        elif plot_type == "semi-log":
            plt.plot(voltage, np.abs(current), marker='o', linestyle='-', label=f"{file_name} IV Curve (Semi-Log)")
            plt.yscale('log')  # Apply log scale to y-axis

        # Add metadata text box
        metadata_text = "\n".join([f"{key}: {value:.3f}" for key, value in metadata.items() if not np.isnan(value)])
        plt.text(0.05, 0.75, metadata_text, transform=plt.gca().transAxes,
                 fontsize=10, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

        # Labels and title
        plt.xlabel("Voltage (V)", fontsize=14)
        plt.ylabel("Current (A)" if plot_type == "linear" else "Log(Current) (A)", fontsize=14)
        plt.title(f"Voltage vs. {'Log(Current)' if plot_type == 'semi-log' else 'Current'} ({file_name})", fontsize=16)

        # Adjust tick font sizes
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        # Add grid and legend
        plt.legend(fontsize=12)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Show the plot
        plt.show()

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")


