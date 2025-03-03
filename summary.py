import os
import pandas as pd
import numpy as np

# Define the folder path containing the CSV files
folder_path = os.path.expanduser("Fri1")

# Create a subdirectory to store all summary tables
summary_folder = os.path.join(folder_path, "Summaries")
os.makedirs(summary_folder, exist_ok=True)  # Create folder if it doesn't exist

# Get all CSV files that end with '_JV.csv' in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith("_JV.csv")]

# Loop through each CSV file and process the data
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)

    # Read the CSV file
    try:
        data = pd.read_csv(file_path, header=None)

        # Correct metadata labels (rows 2-12 → indices 1-11)
        metadata_keys = [
            "NumPads", "Pad Area (sq cm)", "Voc (V)", "Isc (A)", "Jsc (mA/sq cm)",
            "Vmpp (V)", "Impp (A)", "Jmpp (mA/sq cm)", "Pmax (mW/sq cm)", "FF (%)", "PCE (%)"
        ]

        # Convert metadata values to numeric, handling errors
        metadata_values = pd.to_numeric(data.iloc[1:12, 1], errors='coerce').values
        metadata = {key: value for key, value in zip(metadata_keys, metadata_values)}

        # Ensure PCE is positive
        if "PCE (%)" in metadata and not np.isnan(metadata["PCE (%)"]):
            metadata["PCE (%)"] = abs(metadata["PCE (%)"])

        # Skip the first 12 rows and extract IV data
        iv_data = data.iloc[12:].reset_index(drop=True)

        # Convert columns to numeric values, handling errors
        iv_data.iloc[:, 0] = pd.to_numeric(iv_data.iloc[:, 0], errors='coerce')
        iv_data.iloc[:, 1] = pd.to_numeric(iv_data.iloc[:, 1], errors='coerce')

        # Drop rows with NaN values
        iv_data = iv_data.dropna()

        # Extract voltage and current as NumPy arrays
        voltage = iv_data.iloc[:, 0].values
        current = iv_data.iloc[:, 1].values

        # Compute dynamic resistance r_d = dV/dI
        dV = np.diff(voltage)
        dI = np.diff(current)

        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            r_d = np.where(dI != 0, dV / dI, np.inf)

        # Estimate R_s (Series Resistance) from high forward bias region (V > 0.4V)
        high_forward_indices = np.where(voltage[:-1] > 0.4)[0]
        R_s = np.mean(r_d[high_forward_indices]) if len(high_forward_indices) > 0 else None

        # Estimate R_sh (Shunt Resistance) from reverse bias region (V < 0V)
        reverse_indices = np.where(voltage[:-1] < 0)[0]
        R_sh = np.mean(r_d[reverse_indices]) if len(reverse_indices) > 0 else None

        # Format values with reasonable significant figures
        def format_value(value, sig_figs=3):
            if value is None or np.isnan(value):
                return "N/A"
            return f"{value:.{sig_figs}g}"

        # Prepare table data
        summary_data = {
            "Parameter": [
                "NumPads", "Pad Area", "Voc", "Isc", "Jsc", "Vmpp", "Impp", "Jmpp", "Pmax",
                "Fill Factor", "Efficiency", "Series Resistance", "Shunt Resistance"
            ],
            "Value": [
                format_value(metadata.get("NumPads")),
                format_value(metadata.get("Pad Area (sq cm)")),
                format_value(metadata.get("Voc (V)")),
                format_value(metadata.get("Isc (A)")),
                format_value(metadata.get("Jsc (mA/sq cm)")),
                format_value(metadata.get("Vmpp (V)")),
                format_value(metadata.get("Impp (A)")),
                format_value(metadata.get("Jmpp (mA/sq cm)")),
                format_value(metadata.get("Pmax (mW/sq cm)")),
                format_value(metadata.get("FF (%)")),
                format_value(metadata.get("PCE (%)")),
                format_value(R_s),  # Calculated R_s
                format_value(R_sh)  # Calculated R_sh
            ],
            "Description": [
                "Number of contact pads",
                "Pad area of the solar cell in cm²",
                "Open-circuit voltage in volts",
                "Short-circuit current in amperes",
                "Short-circuit current density in mA/cm²",
                "Voltage at maximum power point in volts",
                "Current at maximum power point in amperes",
                "Current density at maximum power point in mA/cm²",
                "Maximum power output in mW/cm²",
                "Fill factor (%) of the device",
                "Power conversion efficiency (%)",
                "Estimated series resistance (Ω)",
                "Estimated shunt resistance (Ω)"
            ]
        }

        # Convert to DataFrame
        summary_df = pd.DataFrame(summary_data)

        # Save CSV file inside the Summaries folder
        output_csv_path = os.path.join(summary_folder, f"summary_{file_name}.csv")
        summary_df.to_csv(output_csv_path, index=False)
        
        print(f"Saved summary table: {output_csv_path}")

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
