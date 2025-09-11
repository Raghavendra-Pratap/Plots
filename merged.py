import os
import pandas as pd

# 📁 Set your folder path containing the CSV files
csv_folder_path = "/Users/raghavendra_pratap/Downloads/1250 3"
# 📄 Output Excel file will be saved in the same folder
output_excel_path = os.path.join(csv_folder_path, "merged_output.xlsx")

# ✨ Create a new Excel writer object
with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
    # Loop through all files in the folder
    for filename in os.listdir(csv_folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(csv_folder_path, filename)
            sheet_name = os.path.splitext(filename)[0][:31]  # Excel sheet name limit = 31 chars
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            # Write to a sheet named after the CSV filename
            df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"✅ All CSV files merged into Excel file: '{output_excel_path}'")