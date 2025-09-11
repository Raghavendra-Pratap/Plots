import pandas as pd
import numpy as np

def split_csv_to_excel(input_csv, output_excel):
    # Read the CSV file
    print(f"Reading CSV file: {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Get unique Shop IDs
    unique_shop_ids = df['Shop ID'].unique()
    
    # Split Shop IDs into two groups
    mid_point = len(unique_shop_ids) // 2
    first_half_ids = unique_shop_ids[:mid_point]
    second_half_ids = unique_shop_ids[mid_point:]
    
    # Create two dataframes based on Shop IDs
    df1 = df[df['Shop ID'].isin(first_half_ids)]
    df2 = df[df['Shop ID'].isin(second_half_ids)]
    
    # Create Excel writer object
    print(f"Creating Excel file: {output_excel}")
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        # Write each dataframe to a different sheet
        df1.to_excel(writer, sheet_name='Sheet1', index=False)
        df2.to_excel(writer, sheet_name='Sheet2', index=False)
    
    print(f"Successfully split data into two sheets:")
    print(f"Sheet1: {len(df1)} rows with {len(first_half_ids)} unique Shop IDs")
    print(f"Sheet2: {len(df2)} rows with {len(second_half_ids)} unique Shop IDs")

if __name__ == "__main__":
    input_csv = "input.csv"  # Replace with your input CSV file name
    output_excel = "output.xlsx"  # Replace with your desired output Excel file name
    split_csv_to_excel(input_csv, output_excel) 