import pandas as pd
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SKUAnalysisProcessor:
    """
    SKU Analysis Processor.
    
    This script performs a comprehensive analysis of SKU data including:
    1. Intra-image outlier removal
    2. Global outlier removal  
    3. Ratio calculation between problematic and reference SKUs
    4. Threshold generation for SKU classification
    """
    
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        self.ratios_raw = None
        self.final_thresholds = None
        self.stats = {}
        
    def load_data(self, file_path):
        """
        Load and validate the input CSV file.
        
        Args:
            file_path (str): Path to the input CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"📁 Reading data from: {file_path}")
        
        try:
            self.raw_data = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['test_image_id', 'category_name', 'group_name', 'class_name', 'Area', 'Prob/Ref']
            missing_columns = [col for col in required_columns if col not in self.raw_data.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert Area to numeric
            self.raw_data['Area'] = pd.to_numeric(self.raw_data['Area'], errors='coerce')
            
            # Standardize Prob/Ref values
            self.raw_data['Prob/Ref'] = self.raw_data['Prob/Ref'].str.lower().str.strip()
            
            # Validate Prob/Ref values
            valid_values = ['problem', 'reference']
            invalid_mask = ~self.raw_data['Prob/Ref'].isin(valid_values)
            if invalid_mask.any():
                print(f"⚠️  Warning: Found {invalid_mask.sum()} rows with invalid 'Prob/Ref' values")
                self.raw_data = self.raw_data[~invalid_mask]
            
            print(f"✅ Data loaded successfully: {len(self.raw_data)} rows")
            print(f"   - Categories: {self.raw_data['category_name'].nunique()}")
            print(f"   - Images: {self.raw_data['test_image_id'].nunique()}")
            print(f"   - Problematic SKUs: {len(self.raw_data[self.raw_data['Prob/Ref'] == 'problem'])}")
            print(f"   - Reference SKUs: {len(self.raw_data[self.raw_data['Prob/Ref'] == 'reference'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def perform_intra_image_outlier_removal(self, df):
        """
        Step 1: Remove outliers within each image based on median area deviation.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with intra-image outliers removed
        """
        print("Step 1: Performing intra-image outlier removal...")
        
        df_step1 = df.copy()
        initial_count = len(df_step1)
        
        # Calculate median area for each SKU within each image and group
        median_areas = df_step1.groupby(['test_image_id', 'group_name', 'class_name'])['Area'].transform('median')
        
        # Calculate the deviation of each area from the median
        deviation = np.abs(df_step1['Area'] - median_areas)
        
        # Set a threshold for removal (50% deviation from median)
        deviation_threshold = median_areas * 0.5
        
        # Filter out rows where area is too far from the group median
        df_step1 = df_step1[deviation <= deviation_threshold]
        
        removed_count = initial_count - len(df_step1)
        print(f"   - Removed {removed_count} intra-image outliers")
        print(f"   - Remaining data: {len(df_step1)} rows")
        
        return df_step1
    
    def perform_global_outlier_removal(self, df):
        """
        Step 2: Remove global outliers based on z-score across all images.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with global outliers removed
        """
        print("Step 2: Performing global outlier removal...")
        
        df_step2 = df.copy()
        initial_count = len(df_step2)
        
        # Calculate global mean and std for each class
        class_stats = df_step2.groupby('class_name')['Area'].agg(['mean', 'std']).reset_index()
        class_stats.columns = ['class_name', 'global_mean_area', 'global_std_area']
        
        # Merge global stats back to the main DataFrame
        df_step2 = df_step2.merge(class_stats, on='class_name', how='left')
        
        # Define a z-score threshold (3 standard deviations)
        z_score_threshold = 3
        
        # Calculate z-score for each area, handling potential division by zero
        df_step2['z_score'] = df_step2.apply(lambda row: 
            (row['Area'] - row['global_mean_area']) / row['global_std_area'] 
            if row['global_std_area'] != 0 else 0, axis=1)
        
        # Filter out rows with z-scores above the threshold
        cleaned_df = df_step2[np.abs(df_step2['z_score']) < z_score_threshold].copy()
        
        # Clean up temporary columns
        cleaned_df = cleaned_df.drop(columns=['global_mean_area', 'global_std_area', 'z_score'])
        
        removed_count = initial_count - len(cleaned_df)
        print(f"   - Removed {removed_count} global outliers")
        print(f"   - Remaining data: {len(cleaned_df)} rows")
        
        return cleaned_df
    
    def clean_data(self):
        """
        Perform the complete data cleaning pipeline.
        
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        if self.raw_data is None:
            raise ValueError("No data loaded. Please load data first.")
        
        print("\n🧹 Starting data cleaning pipeline...")
        
        # Step 1: Intra-image outlier removal
        df_step1 = self.perform_intra_image_outlier_removal(self.raw_data)
        
        # Step 2: Global outlier removal
        self.cleaned_data = self.perform_global_outlier_removal(df_step1)
        
        total_removed = len(self.raw_data) - len(self.cleaned_data)
        print(f"\n✅ Data cleaning completed!")
        print(f"   - Original data: {len(self.raw_data)} rows")
        print(f"   - Cleaned data: {len(self.cleaned_data)} rows")
        print(f"   - Total outliers removed: {total_removed}")
        
        return self.cleaned_data
    
    def calculate_ratios_and_stats(self):
        """
        Calculate ratios between problematic and reference SKUs and generate statistics.
        
        Returns:
            tuple: (ratios_raw_df, final_thresholds_df)
        """
        print("Step 3: Calculating ratios...")
        
        if self.cleaned_data is None:
            raise ValueError("Data must be cleaned before calculating ratios")
        
        # Separate problematic and reference SKUs
        problematic_skus = self.cleaned_data[self.cleaned_data['Prob/Ref'] == 'problem']
        reference_skus = self.cleaned_data[self.cleaned_data['Prob/Ref'] == 'reference']
        
        print(f"   - Problematic SKUs: {len(problematic_skus)}")
        print(f"   - Reference SKUs: {len(reference_skus)}")
        
        # Merge problematic and reference SKUs on image AND category
        merged_ratios = pd.merge(problematic_skus, reference_skus, 
                                 on=['test_image_id', 'category_name'],
                                 suffixes=('_prob', '_ref'))
        
        if merged_ratios.empty:
            print("⚠️  No valid combinations found after merge")
            # Return empty DataFrames with expected columns
            empty_ratios_cols = ['test_image_id', 'category_name', 'group_name_prob', 'class_name_prob', 
                                 'Area_prob', 'Prob/Ref_prob', 'group_name_ref', 'class_name_ref', 
                                 'Area_ref', 'Prob/Ref_ref', 'ratio']
            empty_thresholds_cols = ['category_name', 'problematic_group_name', 'problematic_sku', 
                                     'reference_group_name', 'reference_sku', 'ratio_list', 'ratio_threshold']
            return pd.DataFrame(columns=empty_ratios_cols), pd.DataFrame(columns=empty_thresholds_cols)
        
        # Calculate the ratio as Reference Area / Problematic Area
        merged_ratios['ratio'] = merged_ratios['Area_ref'] / merged_ratios['Area_prob']
        
        # Convert ratio to numeric and round to 4 decimal places
        merged_ratios['ratio'] = pd.to_numeric(merged_ratios['ratio'], errors='coerce').round(4)
        
        # Remove invalid ratios (NaN, inf, or negative)
        merged_ratios = merged_ratios[merged_ratios['ratio'].notna() & 
                                     np.isfinite(merged_ratios['ratio']) & 
                                     (merged_ratios['ratio'] > 0)]
        
        print(f"   - Valid ratios calculated: {len(merged_ratios)}")
        
        self.ratios_raw = merged_ratios
        
        # Generate final thresholds
        print("Step 4: Aggregating ratios to find thresholds...")
        self.final_thresholds = self.generate_final_thresholds(merged_ratios)
        
        return self.ratios_raw, self.final_thresholds
    
    def generate_final_thresholds(self, ratios_df):
        """
        Generate final thresholds by aggregating ratios.
        
        Args:
            ratios_df (pd.DataFrame): DataFrame with calculated ratios
            
        Returns:
            pd.DataFrame: DataFrame with final thresholds
        """
        # Group by the desired final columns and aggregate ratios into a list
        final_thresholds_df = ratios_df.groupby([
            'category_name', 'group_name_prob', 'class_name_prob', 
            'group_name_ref', 'class_name_ref'
        ])['ratio'].apply(list).reset_index()
        
        # Rename columns for clarity
        final_thresholds_df.columns = [
            'category_name', 'problematic_group_name', 'problematic_sku', 
            'reference_group_name', 'reference_sku', 'ratio_list'
        ]
        
        # Calculate the median of the ratio_list to get the final threshold
        final_thresholds_df['ratio_threshold'] = final_thresholds_df['ratio_list'].apply(np.median)
        
        # Add additional statistics
        final_thresholds_df['ratio_count'] = final_thresholds_df['ratio_list'].apply(len)
        final_thresholds_df['ratio_mean'] = final_thresholds_df['ratio_list'].apply(np.mean)
        final_thresholds_df['ratio_std'] = final_thresholds_df['ratio_list'].apply(np.std)
        final_thresholds_df['ratio_min'] = final_thresholds_df['ratio_list'].apply(min)
        final_thresholds_df['ratio_max'] = final_thresholds_df['ratio_list'].apply(max)
        
        print(f"   - Final threshold combinations: {len(final_thresholds_df)}")
        
        return final_thresholds_df
    
    def save_results(self, output_path):
        """
        Save all results to Excel file with multiple sheets.
        
        Args:
            output_path (str): Path to save the output Excel file
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"\n💾 Saving results to: {output_path}")
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Save raw data
                self.raw_data.to_excel(writer, sheet_name='01_Raw_Data', index=False)
                
                # Save cleaned data
                self.cleaned_data.to_excel(writer, sheet_name='02_Cleaned_Data', index=False)
                
                # Save all ratios
                self.ratios_raw.to_excel(writer, sheet_name='03_Ratios_Raw', index=False)
                
                # Save final thresholds
                self.final_thresholds.to_excel(writer, sheet_name='04_Final_Thresholds', index=False)
                
                # Save summary statistics
                summary_stats = pd.DataFrame({
                    'Metric': [
                        'Total Images Processed',
                        'Total Ratios Calculated',
                        'Outliers Removed (Intra-image)',
                        'Outliers Removed (Global)',
                        'Unique Problematic SKUs',
                        'Unique Reference SKUs',
                        'Categories Processed',
                        'Final Threshold Combinations'
                    ],
                    'Value': [
                        self.raw_data['test_image_id'].nunique(),
                        len(self.ratios_raw) if self.ratios_raw is not None else 0,
                        len(self.raw_data) - len(self.cleaned_data) if self.cleaned_data is not None else 0,
                        len(self.raw_data) - len(self.cleaned_data) if self.cleaned_data is not None else 0,
                        self.ratios_raw['class_name_prob'].nunique() if self.ratios_raw is not None else 0,
                        self.ratios_raw['class_name_ref'].nunique() if self.ratios_raw is not None else 0,
                        self.raw_data['category_name'].nunique(),
                        len(self.final_thresholds) if self.final_thresholds is not None else 0
                    ]
                })
                summary_stats.to_excel(writer, sheet_name='05_Summary_Stats', index=False)
            
            print("✅ Results saved successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")
            return False

def main():
    """
    Main execution function with GUI file selection.
    """
    print("🚀 SKU Analysis Processor for Unilever Ghana Rollout")
    print("=" * 60)
    
    # Initialize the processor
    processor = SKUAnalysisProcessor()
    
    # Hide the main tkinter window
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog
    input_file_path = filedialog.askopenfilename(
        title="Select your SKU data CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    
    if not input_file_path:
        print("❌ No file selected. Exiting.")
        return
    
    try:
        # Load and validate data
        if not processor.load_data(input_file_path):
            return
        
        # Clean the data
        processor.clean_data()
        
        # Calculate ratios and generate thresholds
        processor.calculate_ratios_and_stats()
        
        # Generate timestamp for output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.dirname(input_file_path)
        output_file_path = os.path.join(output_dir, f'sku_analysis_output_{timestamp}.xlsx')
        
        # Save results
        if processor.save_results(output_file_path):
            print(f"\n🎉 Analysis completed successfully!")
            print(f"📁 Results saved to: {output_file_path}")
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"Processing complete!\n\n"
                f"Results saved to:\n{output_file_path}\n\n"
                f"Summary:\n"
                f"- Images processed: {processor.raw_data['test_image_id'].nunique()}\n"
                f"- Ratios calculated: {len(processor.ratios_raw) if processor.ratios_raw is not None else 0}\n"
                f"- Threshold combinations: {len(processor.final_thresholds) if processor.final_thresholds is not None else 0}"
            )
        else:
            messagebox.showerror("Error", "Failed to save results")
    
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"❌ {error_msg}")
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    main()
