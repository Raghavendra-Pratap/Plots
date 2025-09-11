import pandas as pd
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from datetime import datetime

def clean_data(df):
    """
    Performs a two-step data cleaning process.

    Args:
        df (pd.DataFrame): The input DataFrame with columns:
                          'test_image_id', 'category_name', 'group_name',
                          'class_name', 'Area', 'Prob/Ref'

    Returns:
        pd.DataFrame: The cleaned DataFrame after both filtering steps.
    """
    # ------------------ Step 1: Intra-Image Outlier Removal ------------------
    print("Step 1: Performing intra-image outlier removal...")
    df_step1 = df.copy()
    
    # Calculate median area for each SKU within each image and group
    median_areas = df_step1.groupby(['test_image_id', 'group_name', 'class_name'])['Area'].transform('median')
    
    # Calculate the deviation of each area from the median
    deviation = np.abs(df_step1['Area'] - median_areas)
    
    # Set a threshold for removal. You can adjust this value (e.g., 0.5 for 50%)
    deviation_threshold = median_areas * 0.5 
    
    # Filter out rows where area is too far from the group median
    df_step1 = df_step1[deviation <= deviation_threshold]
    
    # ------------------ Step 2: Global Outlier Removal ------------------
    print("Step 2: Performing global outlier removal...")
    df_step2 = df_step1.copy()
    
    # Calculate global mean and std for each class
    class_stats = df_step2.groupby('class_name')['Area'].agg(['mean', 'std']).reset_index()
    class_stats.columns = ['class_name', 'global_mean_area', 'global_std_area']
    
    # Merge global stats back to the main DataFrame
    df_step2 = df_step2.merge(class_stats, on='class_name', how='left')
    
    # Define a z-score threshold (e.g., 3 standard deviations)
    z_score_threshold = 3
    
    # Calculate z-score for each area, handling potential division by zero (std=0)
    df_step2['z_score'] = df_step2.apply(lambda row: 
        (row['Area'] - row['global_mean_area']) / row['global_std_area'] 
        if row['global_std_area'] != 0 else 0, axis=1)
    
    # Filter out rows with z-scores above the threshold
    cleaned_df = df_step2[np.abs(df_step2['z_score']) < z_score_threshold].copy()
    
    # Clean up temporary columns
    cleaned_df = cleaned_df.drop(columns=['global_mean_area', 'global_std_area', 'z_score'])
    
    return cleaned_df

def generate_ratios_and_stats(cleaned_df):
    """
    Computes ratios and statistics based on the cleaned data.

    Args:
        cleaned_df (pd.DataFrame): The DataFrame after data cleaning.

    Returns:
        tuple: A tuple of DataFrames for output.
    """
    # --- Step 3: Store results here ---
    results = []

    # --- Step 4: Iterate over each image and compute Problem ↔ Reference ratios ---
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
    
    out_df = pd.DataFrame(results)
    if out_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    out_df['ratio'] = pd.to_numeric(out_df['ratio'], errors='coerce').round(4)
    
    # --- Step 6: Calculate percentiles and median statistics ---
    group_cols = ["category_name", "test_image_id", "problem_class_name", "reference_class_name"]
    percentiles = out_df.groupby(group_cols)["ratio"].quantile([0.25, 0.75]).unstack(level=-1)
    percentiles = percentiles.rename(columns={0.25: "ratio_25th_percentile", 0.75: "ratio_75th_percentile"}).reset_index()

    medians = out_df.groupby(group_cols)["ratio"].median().reset_index().rename(columns={"ratio": "ratio_median"})

    median_percentiles = medians["ratio_median"].quantile([0.25, 0.75])
    median_percentiles_df = median_percentiles.reset_index()
    median_percentiles_df.columns = ["percentile", "median_of_ratio"]

    group_cols_no_img = ["category_name", "problem_class_name", "reference_class_name"]
    percentiles_no_img = out_df.groupby(group_cols_no_img)["ratio"].quantile([0.25, 0.75]).unstack(level=-1)
    percentiles_no_img = percentiles_no_img.rename(columns={0.25: "ratio_25th_percentile", 0.75: "ratio_75th_percentile"}).reset_index()

    thresholds_df = percentiles_no_img[[
        "category_name", "problem_class_name", "reference_class_name", "ratio_75th_percentile"
    ]].rename(columns={"ratio_75th_percentile": "threshold"})

    return out_df, percentiles, medians, median_percentiles_df, percentiles_no_img, thresholds_df

# --- Main Execution Block ---
if __name__ == "__main__":
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # Open a file dialog to select the input CSV file
    input_file_path = filedialog.askopenfilename(
        title="Select your SKU data CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if not input_file_path:
        messagebox.showerror("Error", "No file selected. Exiting.")
    else:
        try:
            print(f"Reading data from: {input_file_path}")
            df_raw = pd.read_csv(input_file_path)
            
            # Run the data cleaning process
            df_cleaned = clean_data(df_raw.copy())

            # Run the ratio generation on the cleaned data
            (out_df, percentiles, medians, median_percentiles_df, percentiles_no_img, thresholds_df) = generate_ratios_and_stats(df_cleaned.copy())
            
            # --- POST-CALCULATION PROCESSING ---
            # Create a class-to-group mapping from the raw data
            class_to_group_map = df_raw[['class_name', 'group_name']].drop_duplicates().set_index('class_name')['group_name'].to_dict()

            # Function to add group names based on class name
            def add_group_names(df):
                df['problem_group_name'] = df['problem_class_name'].map(class_to_group_map)
                df['reference_group_name'] = df['reference_class_name'].map(class_to_group_map)
                return df

            # Add group names to the output dataframes
            percentiles = add_group_names(percentiles)
            percentiles_no_img = add_group_names(percentiles_no_img)
            thresholds_df = add_group_names(thresholds_df)
            
            # Reorder columns to place new group names logically
            percentiles = percentiles[['category_name', 'problem_group_name', 'problem_class_name', 'reference_group_name', 'reference_class_name', 'ratio_25th_percentile', 'ratio_75th_percentile']]
            
            # Calculate size_seq for unique problem_class_names within the same problem_group_name
            problem_sku_representative_thresholds = thresholds_df.groupby(['problem_group_name', 'problem_class_name'])['threshold'].median().reset_index()
            problem_sku_representative_thresholds = problem_sku_representative_thresholds.sort_values(by=['problem_group_name', 'threshold']).copy()
            problem_sku_representative_thresholds['size_seq'] = problem_sku_representative_thresholds.groupby('problem_group_name').cumcount() + 1
            
            # Calculate #classes (unique count of problem_class_name within a problem_group_name)
            problem_group_class_counts = problem_sku_representative_thresholds.groupby('problem_group_name')['problem_class_name'].nunique().reset_index()
            problem_group_class_counts.rename(columns={'problem_class_name': '#classes'}, inplace=True)

            # Merge size_seq and #classes back to percentiles_no_img
            percentiles_no_img = pd.merge(percentiles_no_img, problem_sku_representative_thresholds[['problem_group_name', 'problem_class_name', 'size_seq']], 
                                          on=['problem_group_name', 'problem_class_name'], how='left')
            percentiles_no_img = pd.merge(percentiles_no_img, problem_group_class_counts, 
                                          on='problem_group_name', how='left')

            # Reorder columns for 04_Percentiles_No_Image_ID to place new columns at the end
            percentiles_no_img = percentiles_no_img[['category_name', 'problem_group_name', 'problem_class_name', 'reference_group_name', 'reference_class_name', 'ratio_25th_percentile', 'ratio_75th_percentile', 'size_seq', '#classes']]

            # Merge size_seq back to the main thresholds_df for 05_Thresholds
            thresholds_df = pd.merge(thresholds_df, problem_sku_representative_thresholds[['problem_group_name', 'problem_class_name', 'size_seq']], 
                                     on=['problem_group_name', 'problem_class_name'], how='left')

            # Reorder columns for the final thresholds sheet
            thresholds_df = thresholds_df[['category_name', 'problem_group_name', 'problem_class_name', 'size_seq', 'reference_group_name', 'reference_class_name', 'threshold']]
            thresholds_df = thresholds_df.sort_values(by=['category_name', 'problem_group_name', 'size_seq', 'reference_class_name']).reset_index(drop=True)


            # Generate a timestamp for the output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get the directory of the input file to save the output
            output_dir = os.path.dirname(input_file_path)
            output_file_path = os.path.join(output_dir, f'sku_analysis_output_{timestamp}.xlsx')
            
            # Save the results to an Excel file with multiple sheets
            print(f"\nSaving results to: {output_file_path}")
            with pd.ExcelWriter(output_file_path) as writer:
                df_raw.to_excel(writer, sheet_name='01_Raw_Data', index=False)
                df_cleaned.to_excel(writer, sheet_name='02_Cleaned_Data', index=False)
                percentiles.to_excel(writer, sheet_name="03_Percentiles", index=False)
                percentiles_no_img.to_excel(writer, sheet_name="04_Percentiles_No_Image_ID", index=False)
                thresholds_df.to_excel(writer, sheet_name="05_Thresholds", index=False)

            print("\nProcessing complete. The Excel file has been saved.")
            messagebox.showinfo("Success", "Processing complete. The Excel file has been saved in the same location as your input CSV.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")