import pandas as pd
import itertools
import tkinter as tk
from tkinter import filedialog
import os

# --- Step 1: Load the CSV file with a file picker ---
def select_file():
    """File picker to select input CSV file"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Set initial directory to user's home directory
    initial_dir = os.path.expanduser("~")
    
    # Support multiple file types
    filetypes = [
        ("CSV files", "*.csv"),
        ("Excel files", "*.xlsx *.xls"),
        ("All files", "*.*")
    ]
    
    input_path = filedialog.askopenfilename(
        title="Select input data file",
        filetypes=filetypes,
        initialdir=initial_dir
    )
    
    root.destroy()  # Clean up the tkinter window
    
    if not input_path:
        print("❌ No file selected. Exiting program.")
        exit()
    
    return input_path

def load_data(file_path):
    """Load data from file with error handling"""
    try:
        # Determine file type and load accordingly
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            # Try CSV as default
            df = pd.read_csv(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print(f"✅ Successfully loaded file: {os.path.basename(file_path)}")
        print(f"📊 Data shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"📋 Columns: {', '.join(df.columns.tolist())}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading file: {str(e)}")
        print("Please make sure the file is a valid CSV or Excel file.")
        exit()

# Get file path from user
print("🔍 Please select your input data file...")
input_path = select_file()

# Load the data
df = load_data(input_path)

# --- Step 3: Efficient cross join for Problem ↔ Reference ratios across all images in each category ---
results = []
for category_name, group in df.groupby("category_name"):
    problems = group[group["Prob/Ref"].str.lower() == "problem"].copy()
    references = group[group["Prob/Ref"].str.lower() == "reference"].copy()

    if problems.empty or references.empty:
        continue

    # Rename columns for clarity
    problems = problems.rename(columns={
        "class_name": "problem_class_name",
        "group_name": "problem_group_name",
        "Area": "problem_area",
        "test_image_id": "problem_test_image_id"
    })
    references = references.rename(columns={
        "class_name": "reference_class_name",
        "group_name": "reference_group_name",
        "Area": "reference_area",
        "test_image_id": "reference_test_image_id"
    })

    # Add a key for cross join
    problems["key"] = 1
    references["key"] = 1
    cross = problems.merge(references, on="key").drop("key", axis=1)

    cross["category_name"] = category_name
    # Calculate ratio, handle division by zero
    cross["ratio"] = cross["reference_area"] / cross["problem_area"]
    cross.loc[cross["problem_area"] == 0, "ratio"] = None

    # Select only the columns you want
    results.append(cross[[
        "category_name",
        "problem_test_image_id",
        "reference_test_image_id",
        "problem_class_name",
        "reference_class_name",
        "problem_group_name",
        "reference_group_name",
        "problem_area",
        "reference_area",
        "ratio"
    ]])

# After the loop, concatenate all results
if results:
    out_df = pd.concat(results, ignore_index=True)
else:
    out_df = pd.DataFrame()

# --- Step 4: Save results to CSV in the same directory as input ---
output_path = os.path.join(os.path.dirname(input_path), "problem_reference_ratiosxyz.csv")
out_df.to_csv(output_path, index=False)
print(f"✅ Output saved to '{output_path}'")
