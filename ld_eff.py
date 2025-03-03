import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# Define the folder path containing the CSV files
folder_path = os.path.expanduser("Fri1")

# Get all CSV files that end with '_JV.csv' in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith("_JV.csv")]

# Lists to store IV data for plotting
light_data = []
dark_data = []
efficiencies_light = []
efficiencies_dark = []

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
        data = pd.read_csv(file_path, header=None)

        # Extract metadata from rows 2-12 (i.e., row indices 1-11)
        metadata_keys = [
            "NumPads", "Pad Area (sq cm)", "Voc (V)", "Isc (A)", "Jsc (mA/sq cm)",
            "Vmpp (V)", "Impp (A)", "Jmpp (mA/sq cm)", "Pmax (mW/sq cm)", "FF (%)", "PCE (%)"
        ]
        metadata_values = pd.to_numeric(data.iloc[1:12, 1], errors='coerce').values
        metadata = {key: value for key, value in zip(metadata_keys, metadata_values)}

        # Ensure PCE is positive
        efficiency = metadata.get("PCE (%)")
        if efficiency is not None and not np.isnan(efficiency):
            efficiency = abs(efficiency)  # Make sure PCE is positive
        else:
            efficiency = 0  # Set to 0 if missing

        # Skip the first 12 rows and extract IV data
        iv_data = data.iloc[12:].reset_index(drop=True)

        # Convert columns to numeric values, handling errors
        iv_data.iloc[:, 0] = pd.to_numeric(iv_data.iloc[:, 0], errors='coerce')
        iv_data.iloc[:, 1] = pd.to_numeric(iv_data.iloc[:, 1], errors='coerce')

        # Drop rows with NaN values (if any non-numeric rows exist)
        iv_data = iv_data.dropna()

        # Extract voltage and current as NumPy arrays
        voltage = iv_data.iloc[:, 0].values
        current = iv_data.iloc[:, 1].values

        # Store data for later plotting
        if plot_type == "linear":
            light_data.append((voltage, current))
            efficiencies_light.append(efficiency)
        else:
            dark_data.append((voltage, current))
            efficiencies_dark.append(efficiency)

        print(f"Processed: {file_name} ({plot_type} plot) | PCE: {efficiency:.2f}%")

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

# ---- PLOT ALL LIGHT IV CURVES ----
if efficiencies_light:
    plt.figure(figsize=(8, 6))
    norm_light = mcolors.Normalize(vmin=min(efficiencies_light), vmax=max(efficiencies_light))
    cmap = cm.viridis  # Choose a perceptually uniform colormap

    for (voltage, current), eff in zip(light_data, efficiencies_light):
        color = cmap(norm_light(eff))  # Map efficiency to color
        plt.plot(voltage, current, linestyle='-', alpha=0.8, color=color, label=f"PCE: {eff:.2f}%")

    plt.xlabel("Voltage (V)", fontsize=14)
    plt.ylabel("Current (A)", fontsize=14)
    plt.title("Light IV Curves (Efficiency Gradient)", fontsize=16)

    # Add colorbar and link it to the current axis
    sm = cm.ScalarMappable(cmap=cmap, norm=norm_light)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca())  # Ensure colorbar is linked to the current axis
    cbar.set_label("Efficiency (PCE %)", fontsize=12)

    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.show()
else:
    print("No valid light IV curves found.")

# ---- PLOT ALL DARK IV CURVES ----
if efficiencies_dark:
    plt.figure(figsize=(8, 6))
    norm_dark = mcolors.Normalize(vmin=min(efficiencies_dark), vmax=max(efficiencies_dark))

    for (voltage, current), eff in zip(dark_data, efficiencies_dark):
        color = cmap(norm_dark(eff))  # Map efficiency to color
        plt.plot(voltage, np.abs(current), linestyle='-', alpha=0.8, color=color, label=f"PCE: {eff:.2f}%")

    plt.yscale('log')  # Semi-log plot for dark curves
    plt.xlabel("Voltage (V)", fontsize=14)
    plt.ylabel("Log(Current) (A)", fontsize=14)
    plt.title("Dark IV Curves (Efficiency Gradient)", fontsize=16)

    # Add colorbar and link it to the current axis
    sm = cm.ScalarMappable(cmap=cmap, norm=norm_dark)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca())  # Ensure colorbar is linked to the current axis
    cbar.set_label("Efficiency (PCE %)", fontsize=12)

    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()
else:
    print("No valid dark IV curves found.")
