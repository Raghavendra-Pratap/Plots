import pandas as pd
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SKURatioAnalyzer:
    """
    Enhanced SKU Ratio Analyzer that handles all the blockers mentioned:
    1. Different zoom levels and tilt issues
    2. Annotation variations
    3. Missing reference/problematic SKUs
    4. Human errors and outliers
    5. Data quality issues
    """
    
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        self.ratio_data = None
        self.outliers_removed = 0
        self.images_processed = 0
        self.total_ratios = 0
        
    def load_and_validate_data(self, file_path):
        """
        Load and validate the input CSV file
        """
        print("📁 Loading and validating data...")
        
        try:
            self.raw_data = pd.read_csv(file_path)
            self.raw_data.columns = self.raw_data.columns.str.strip()
            
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
    
    def remove_annotation_variations(self, df):
        """
        Handle annotation variations within the same image and SKU
        Uses median area for each SKU within each image to reduce noise
        """
        print("🔧 Removing annotation variations...")
        
        # Calculate median area for each SKU within each image
        median_areas = df.groupby(['test_image_id', 'class_name'])['Area'].transform('median')
        
        # Calculate deviation from median
        deviation = np.abs(df['Area'] - median_areas)
        deviation_percentage = (deviation / median_areas) * 100
        
        # Remove annotations that deviate more than 30% from median (adjustable)
        threshold_percentage = 30
        clean_mask = deviation_percentage <= threshold_percentage
        
        removed_count = (~clean_mask).sum()
        cleaned_df = df[clean_mask].copy()
        
        print(f"   - Removed {removed_count} annotations with >{threshold_percentage}% deviation")
        print(f"   - Remaining annotations: {len(cleaned_df)}")
        
        return cleaned_df
    
    def handle_zoom_and_tilt_issues(self, df):
        """
        Handle different zoom levels and tilt issues by using relative ratios
        within the same image rather than absolute areas
        """
        print("📐 Handling zoom and tilt issues...")
        
        # Group by image and calculate relative areas
        image_stats = df.groupby('test_image_id')['Area'].agg(['mean', 'std']).reset_index()
        image_stats.columns = ['test_image_id', 'image_mean_area', 'image_std_area']
        
        # Merge back to main dataframe
        df_with_stats = df.merge(image_stats, on='test_image_id', how='left')
        
        # Calculate z-score within each image
        df_with_stats['z_score'] = (df_with_stats['Area'] - df_with_stats['image_mean_area']) / df_with_stats['image_std_area']
        
        # Remove extreme outliers (z-score > 4) that might be due to zoom/tilt issues
        outlier_mask = np.abs(df_with_stats['z_score']) <= 4
        cleaned_df = df_with_stats[outlier_mask].copy()
        
        removed_count = (~outlier_mask).sum()
        print(f"   - Removed {removed_count} extreme outliers (z-score > 4)")
        print(f"   - Remaining data: {len(cleaned_df)} rows")
        
        # Drop temporary columns
        cleaned_df = cleaned_df.drop(['image_mean_area', 'image_std_area', 'z_score'], axis=1)
        
        return cleaned_df
    
    def filter_images_with_both_types(self, df):
        """
        Filter out images that don't have both problematic and reference SKUs
        """
        print("🔄 Filtering images with both problematic and reference SKUs...")
        
        # Count problematic and reference SKUs per image
        image_counts = df.groupby('test_image_id')['Prob/Ref'].value_counts().unstack(fill_value=0)
        
        # Filter images that have both types
        valid_images = image_counts[(image_counts['problem'] > 0) & (image_counts['reference'] > 0)].index
        
        filtered_df = df[df['test_image_id'].isin(valid_images)].copy()
        
        removed_images = df['test_image_id'].nunique() - len(valid_images)
        print(f"   - Removed {removed_images} images without both SKU types")
        print(f"   - Valid images remaining: {len(valid_images)}")
        
        return filtered_df
    
    def detect_and_remove_human_errors(self, df):
        """
        Detect and remove potential human errors in annotations
        """
        print("👁️  Detecting human errors...")
        
        # Calculate statistics for each class across all images
        class_stats = df.groupby('class_name')['Area'].agg(['mean', 'std', 'count']).reset_index()
        class_stats.columns = ['class_name', 'class_mean_area', 'class_std_area', 'class_count']
        
        # Only consider classes with sufficient data (at least 3 annotations)
        reliable_classes = class_stats[class_stats['class_count'] >= 3]['class_name'].tolist()
        
        # Filter data to only include reliable classes
        reliable_df = df[df['class_name'].isin(reliable_classes)].copy()
        
        # Merge class statistics back
        reliable_df = reliable_df.merge(class_stats, on='class_name', how='left')
        
        # Calculate z-score for each annotation relative to its class
        reliable_df['class_z_score'] = (reliable_df['Area'] - reliable_df['class_mean_area']) / reliable_df['class_std_area']
        
        # Remove annotations that are statistical outliers (z-score > 3)
        error_mask = np.abs(reliable_df['class_z_score']) <= 3
        cleaned_df = reliable_df[error_mask].copy()
        
        removed_count = (~error_mask).sum()
        print(f"   - Removed {removed_count} potential human errors")
        print(f"   - Remaining reliable annotations: {len(cleaned_df)}")
        
        # Drop temporary columns
        cleaned_df = cleaned_df.drop(['class_mean_area', 'class_std_area', 'class_count', 'class_z_score'], axis=1)
        
        return cleaned_df
    
    def clean_data(self):
        """
        Comprehensive data cleaning pipeline
        """
        print("\n🧹 Starting comprehensive data cleaning...")
        
        df = self.raw_data.copy()
        initial_count = len(df)
        
        # Step 1: Remove annotation variations
        df = self.remove_annotation_variations(df)
        
        # Step 2: Handle zoom and tilt issues
        df = self.handle_zoom_and_tilt_issues(df)
        
        # Step 3: Filter images with both SKU types
        df = self.filter_images_with_both_types(df)
        
        # Step 4: Detect and remove human errors
        df = self.detect_and_remove_human_errors(df)
        
        self.cleaned_data = df
        self.outliers_removed = initial_count - len(df)
        
        print(f"\n✅ Data cleaning completed!")
        print(f"   - Original data: {initial_count} rows")
        print(f"   - Cleaned data: {len(df)} rows")
        print(f"   - Total outliers removed: {self.outliers_removed}")
        
        return df
    
    def calculate_ratios(self):
        """
        Calculate ratios between problematic and reference SKUs
        """
        print("\n📊 Calculating ratios...")
        
        if self.cleaned_data is None:
            raise ValueError("Data must be cleaned before calculating ratios")
        
        results = []
        
        # Group by image to process each image separately
        for test_image_id, image_data in self.cleaned_data.groupby('test_image_id'):
            # Separate problematic and reference SKUs
            problems = image_data[image_data['Prob/Ref'] == 'problem']
            references = image_data[image_data['Prob/Ref'] == 'reference']
            
            if problems.empty or references.empty:
                continue
            
            # Calculate all possible ratios between problematic and reference SKUs
            for _, prob_row in problems.iterrows():
                for _, ref_row in references.iterrows():
                    try:
                        # Calculate ratio: Reference Area / Problematic Area
                        ratio = ref_row['Area'] / prob_row['Area']
                        
                        if np.isfinite(ratio) and ratio > 0:
                            results.append({
                                'category_name': prob_row['category_name'],
                                'problematic_group_name': prob_row['group_name'],
                                'problematic_class_name': prob_row['class_name'],
                                'reference_group_name': ref_row['group_name'],
                                'reference_class_name': ref_row['class_name'],
                                'ratio': ratio,
                                'test_image_id': test_image_id
                            })
                    except (ZeroDivisionError, ValueError):
                        continue
        
        if not results:
            print("⚠️  No valid ratios could be calculated")
            return pd.DataFrame()
        
        self.ratio_data = pd.DataFrame(results)
        self.total_ratios = len(self.ratio_data)
        self.images_processed = self.ratio_data['test_image_id'].nunique()
        
        print(f"✅ Ratio calculation completed!")
        print(f"   - Total ratios calculated: {self.total_ratios}")
        print(f"   - Images processed: {self.images_processed}")
        print(f"   - Unique problematic SKUs: {self.ratio_data['problematic_class_name'].nunique()}")
        print(f"   - Unique reference SKUs: {self.ratio_data['reference_class_name'].nunique()}")
        
        return self.ratio_data
    
    def generate_final_output(self):
        """
        Generate the final output in the requested format
        """
        print("\n📋 Generating final output...")
        
        if self.ratio_data is None or self.ratio_data.empty:
            print("⚠️  No ratio data available")
            return pd.DataFrame()
        
        # Group by the required columns and aggregate ratios into lists
        final_output = self.ratio_data.groupby([
            'category_name', 
            'problematic_group_name', 
            'problematic_class_name', 
            'reference_group_name', 
            'reference_class_name'
        ])['ratio'].apply(list).reset_index()
        
        # Rename the ratio column to match requested format
        final_output.columns = [
            'category_name',
            'problematic_group_name', 
            'problematic_class_name',
            'reference_group_name', 
            'reference_class_name', 
            'ratio_list'
        ]
        
        # Add statistical information
        final_output['ratio_count'] = final_output['ratio_list'].apply(len)
        final_output['ratio_mean'] = final_output['ratio_list'].apply(np.mean)
        final_output['ratio_median'] = final_output['ratio_list'].apply(np.median)
        final_output['ratio_std'] = final_output['ratio_list'].apply(np.std)
        final_output['ratio_min'] = final_output['ratio_list'].apply(min)
        final_output['ratio_max'] = final_output['ratio_list'].apply(max)
        
        # Sort by category and problematic group for better organization
        final_output = final_output.sort_values(['category_name', 'problematic_group_name', 'problematic_class_name'])
        
        print(f"✅ Final output generated!")
        print(f"   - Total combinations: {len(final_output)}")
        print(f"   - Average ratios per combination: {final_output['ratio_count'].mean():.1f}")
        
        return final_output
    
    def save_results(self, output_path):
        """
        Save all results to Excel file with multiple sheets
        """
        print(f"\n💾 Saving results to: {output_path}")
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Save raw data
                self.raw_data.to_excel(writer, sheet_name='01_Raw_Data', index=False)
                
                # Save cleaned data
                self.cleaned_data.to_excel(writer, sheet_name='02_Cleaned_Data', index=False)
                
                # Save all ratios
                self.ratio_data.to_excel(writer, sheet_name='03_All_Ratios', index=False)
                
                # Save final output
                final_output = self.generate_final_output()
                final_output.to_excel(writer, sheet_name='04_Final_Output', index=False)
                
                # Save summary statistics
                summary_stats = pd.DataFrame({
                    'Metric': [
                        'Total Images Processed',
                        'Total Ratios Calculated',
                        'Outliers Removed',
                        'Unique Problematic SKUs',
                        'Unique Reference SKUs',
                        'Categories Processed'
                    ],
                    'Value': [
                        self.images_processed,
                        self.total_ratios,
                        self.outliers_removed,
                        self.ratio_data['problematic_class_name'].nunique() if self.ratio_data is not None else 0,
                        self.ratio_data['reference_class_name'].nunique() if self.ratio_data is not None else 0,
                        self.raw_data['category_name'].nunique()
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
    Main execution function
    """
    print("🚀 Enhanced SKU Ratio Analyzer")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = SKURatioAnalyzer()
    
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
        if not analyzer.load_and_validate_data(input_file_path):
            return
        
        # Clean the data
        analyzer.clean_data()
        
        # Calculate ratios
        analyzer.calculate_ratios()
        
        # Generate timestamp for output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.dirname(input_file_path)
        output_file_path = os.path.join(output_dir, f'enhanced_sku_analysis_{timestamp}.xlsx')
        
        # Save results
        if analyzer.save_results(output_file_path):
            print(f"\n🎉 Analysis completed successfully!")
            print(f"📁 Results saved to: {output_file_path}")
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"Analysis completed successfully!\n\n"
                f"Results saved to:\n{output_file_path}\n\n"
                f"Summary:\n"
                f"- Images processed: {analyzer.images_processed}\n"
                f"- Ratios calculated: {analyzer.total_ratios}\n"
                f"- Outliers removed: {analyzer.outliers_removed}"
            )
        else:
            messagebox.showerror("Error", "Failed to save results")
    
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"❌ {error_msg}")
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    main()