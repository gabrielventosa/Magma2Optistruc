"""
==============================================================================
Copyright (C) 2024 Luis G. Ventosa, Inteligencia Mecánica
Email: gv@inteligenciamecanica.com

This script is licensed under the GNU General Public License (GPL).
You may redistribute it and/or modify it under the terms of the GPL as published 
by the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version.

Description:
This script converts MagmaSoft mapped data into initial stresses data for 
Optistruct. It reads six input files corresponding to stress components (XX, YY, 
ZZ, XY, YZ, ZX), processes the data, and formats it into a specific structure 
required by Optistruct.

Disclaimer:
This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

For more details about the GNU General Public License, see <https://www.gnu.org/licenses/>.
==============================================================================
"""
import pandas as pd

# File names for the six stress components
file_names = [
    "StressE_TensorX_Ambient_MPa.fem",  # σXX
    "StressE_TensorY_Ambient_MPa.fem",  # σYY
    "StressE_TensorY_Ambient_MPa.fem",  # σZZ
    "StressE_TensorXY_c8_Ambient_MPa.fem",  # τXY
    "StressE_TensorXZ_c8_Ambient_MPa.fem",  # τYZ
    "StressE_TensorXZ_c8_Ambient_MPa.fem"   # τZX
]

# Read the data from each file, skipping lines starting with '$' and handling scientific notation
data_frames = []
for file, comp in zip(file_names, ["XX", "YY", "ZZ", "XY", "YZ", "ZX"]):
    df = pd.read_csv(file, sep='\s+', comment='$', header=None, names=["ELEM", f"COMP_{comp}"])
    data_frames.append(df)

# Merge data on the element column
combined_data = data_frames[0][["ELEM"]].copy()
for df in data_frames:
    combined_data = combined_data.merge(df, on="ELEM")

# Smarter field formatting function
def format_field(value):
    """
    Formats the value based on its type and properties:
    - Non-numeric: Left-align in an 8-character field.
    - Integer: Right-align in an 8-character field.
    - Positive float: 8.2E format.
    - Negative float: 7.2E format with sign.
    """
    if isinstance(value, str):
        # Non-numeric values: Left-align
        return f"{value:<8}"
    elif isinstance(value, int):
        # Integer values: Right-align
        return f"{value:>8}"
    elif isinstance(value, float):
        if value < 0:
            # Negative floats: 7.2E with sign
            formatted = f"{value:8}"
            #return formatted
            return formatted[:8] if len(formatted) > 8 else formatted
        else:
            # Positive floats: 8.2E
            formatted = f"{value:8}"
            #return f"{value:8}"
            return formatted[:8] if len(formatted) > 8 else formatted
    else:
        # Fallback for unknown types
        raise ValueError(f"Unsupported type for value: {value}")

# Prepare output lines
output_lines = []
# Add the INISTRS line at the top
output_lines.append(
    format_field("INISTRS") +
    format_field("100") +
    format_field("") +
    format_field("0")
)

# Add lines for each element
for _, row in combined_data.iterrows():
    # First line for ELEM
    elem_line = format_field("") + format_field("ELEM") + format_field(int(row["ELEM"]))
    output_lines.append(elem_line)

    # Second line for VALUE
    value_line = format_field("") + format_field("VALUE") + "".join(
        [format_field(value) for value in row[1:].values]
    )
    output_lines.append(value_line)

# Write to the output file
output_file = "mapped_stress_data.fem"
with open(output_file, "w") as f:
    f.write("\n".join(output_lines))

print(f"Combined data saved to {output_file}")
