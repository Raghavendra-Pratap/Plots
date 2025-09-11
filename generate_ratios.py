import pandas as pd
import itertools
import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

# --- Step 1: Load the CSV file with a file picker ---
root = tk.Tk()
root.withdraw()  # Hide the main window
input_path = filedialog.askopenfilename(title="Select input CSV file", filetypes=[("CSV files", "*.csv")])
if not input_path:
    raise Exception("No file selected.")
df = pd.read_csv(input_path)
df.columns = df.columns.str.strip()

# --- Add timestamp for output filenames ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# --- Step 1.5: Save input file for reference ---
input_df = df.copy()

# --- Step 2: Remove outliers based on area for each (category_name, test_image_id, class_name) ---
def remove_outliers_area(df):
    def lower_bound(x):
        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        iqr = q3 - q1
        return q1 - 1.5 * iqr

    def upper_bound(x):
        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        iqr = q3 - q1
        return q3 + 1.5 * iqr

    lower = df.groupby(['category_name', 'test_image_id', 'class_name'])['Area'].transform(lower_bound)
    upper = df.groupby(['category_name', 'test_image_id', 'class_name'])['Area'].transform(upper_bound)
    mask = (df['Area'] >= lower) & (df['Area'] <= upper)
    cleaned = df[mask].copy()
    outliers = df[~mask].copy()
    return cleaned, outliers

cleaned_df, outliers_df = remove_outliers_area(df)

# --- Step 3: Store results here ---
results = []

# --- Step 4: Iterate over each image and compute Problem ↔ Reference ratios (using cleaned data) ---
for (category_name, test_image_id), group in cleaned_df.groupby(["category_name", "test_image_id"]):
    # Filter problem and reference rows
    problems = group[group["Prob/Ref"].str.lower() == "problem"]
    references = group[group["Prob/Ref"].str.lower() == "reference"]

    # Skip if either list is empty
    if problems.empty or references.empty:
        continue

    # Cross join Problem × Reference pairs
    for _, prob_row in problems.iterrows():
        for _, ref_row in references.iterrows():
            try:
                ratio = float(ref_row["Area"]) / float(prob_row["Area"])
            except ZeroDivisionError:
                ratio = None

            results.append({
                "category_name": category_name,
                "test_image_id": test_image_id,
                "problem_class_name": prob_row["class_name"],
                "reference_class_name": ref_row["class_name"],
                "ratio": ratio
            })

# --- Step 5: Save results to CSV in the same directory as input ---
out_df = pd.DataFrame(results)
# Ensure 'ratio' is numeric and format to 4 decimal places
out_df['ratio'] = pd.to_numeric(out_df['ratio'], errors='coerce').round(4)
output_path = os.path.join(os.path.dirname(input_path), f"problem_reference_ratios_{timestamp}.csv")
out_df.to_csv(output_path, index=False)
print(f"✅ Output saved to '{output_path}'")

# --- Step 6: Calculate percentiles and median statistics and save to Excel ---
group_cols = ["category_name", "test_image_id", "problem_class_name", "reference_class_name"]

# Group and calculate percentiles
percentiles = out_df.groupby(group_cols)["ratio"].quantile([0.25, 0.75]).unstack(level=-1)
percentiles = percentiles.rename(columns={0.25: "ratio_25th_percentile", 0.75: "ratio_75th_percentile"}).reset_index()

# Group and calculate median
medians = out_df.groupby(group_cols)["ratio"].median().reset_index().rename(columns={"ratio": "ratio_median"})

# Calculate 25th and 75th percentiles of the medians
median_percentiles = medians["ratio_median"].quantile([0.25, 0.75])
median_percentiles_df = median_percentiles.reset_index()
median_percentiles_df.columns = ["percentile", "median_of_ratio"]

# Calculate percentiles without image_id
group_cols_no_img = ["category_name", "problem_class_name", "reference_class_name"]
percentiles_no_img = out_df.groupby(group_cols_no_img)["ratio"].quantile([0.25, 0.75]).unstack(level=-1)
percentiles_no_img = percentiles_no_img.rename(columns={0.25: "ratio_25th_percentile", 0.75: "ratio_75th_percentile"}).reset_index()

# Prepare thresholds sheet using 75th percentile as threshold
thresholds_df = percentiles_no_img[[
    "category_name", "problem_class_name", "reference_class_name", "ratio_75th_percentile"
]].rename(columns={"ratio_75th_percentile": "threshold"})

# Save all to Excel, including the new thresholds sheet
excel_output_path = os.path.join(os.path.dirname(input_path), f"problem_reference_ratios_with_stats_{timestamp}.xlsx")
with pd.ExcelWriter(excel_output_path) as writer:
    input_df.to_excel(writer, sheet_name="Input File", index=False)
    cleaned_df.to_excel(writer, sheet_name="Data After Removing Outliers", index=False)
    outliers_df.to_excel(writer, sheet_name="Removed Outliers", index=False)
    out_df.to_excel(writer, sheet_name="All Ratios", index=False)
    percentiles.to_excel(writer, sheet_name="Percentiles", index=False)
    medians.to_excel(writer, sheet_name="Medians", index=False)
    median_percentiles_df.to_excel(writer, sheet_name="Median Percentiles", index=False)
    percentiles_no_img.to_excel(writer, sheet_name="Percentiles (No Image ID)", index=False)
    thresholds_df.to_excel(writer, sheet_name="Thresholds", index=False)
print(f"✅ Stats and ratios saved to '{excel_output_path}'")
