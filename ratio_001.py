import polars as pl
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SKURatioAnalyzer:
    """
    Fresh SKU Ratio Analyzer using Polars for efficient data processing.
    Handles all blockers in SKU detection: zoom levels, tilt issues, annotation variations,
    missing data, and human errors.
    """
    
    def __init__(self):
        self.raw_data = None
        self.cleaned_data = None
        self.ratio_data = None
        self.stats = {
            'original_rows': 0,
            'cleaned_rows': 0,
            'outliers_removed': 0,
            'images_processed': 0,
            'total_ratios': 0,
            'categories': 0,
            'problematic_skus': 0,
            'reference_skus': 0
        }
    
    def load_data(self, file_path: str) -> bool:
        """
        Load and validate CSV data using Polars
        """
        print("📁 Loading data with Polars...")
        
        try:
            # Load CSV with Polars
            self.raw_data = pl.read_csv(file_path)
            
            # Validate required columns
            required_cols = ['test_image_id', 'category_name', 'group_name', 'class_name', 'Area', 'Prob/Ref']
            missing_cols = [col for col in required_cols if col not in self.raw_data.columns]
            
            if missing_cols:
                raise ValueError(f"Missing columns: {missing_cols}")
            
            # Convert Area to numeric and handle invalid values
            self.raw_data = self.raw_data.with_columns([
                pl.col('Area').cast(pl.Float64).alias('Area'),
                pl.col('Prob/Ref').str.to_lowercase().str.strip_chars().alias('Prob/Ref')
            ])
            
            # Filter out invalid Prob/Ref values
            valid_values = ['problem', 'reference']
            self.raw_data = self.raw_data.filter(
                pl.col('Prob/Ref').is_in(valid_values)
            )
            
            # Update stats
            self.stats['original_rows'] = len(self.raw_data)
            self.stats['categories'] = self.raw_data.select('category_name').n_unique()
            self.stats['problematic_skus'] = self.raw_data.filter(pl.col('Prob/Ref') == 'problem').height
            self.stats['reference_skus'] = self.raw_data.filter(pl.col('Prob/Ref') == 'reference').height
            
            print(f"✅ Data loaded: {self.stats['original_rows']} rows")
            print(f"   Categories: {self.stats['categories']}")
            print(f"   Problematic SKUs: {self.stats['problematic_skus']}")
            print(f"   Reference SKUs: {self.stats['reference_skus']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def remove_annotation_variations(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Remove inconsistent annotations within same image and SKU
        """
        print("🔧 Removing annotation variations...")
        
        # Calculate median area for each SKU within each image
        median_areas = df.group_by(['test_image_id', 'class_name']).agg([
            pl.col('Area').median().alias('median_area')
        ])
        
        # Join back to main dataframe
        df_with_median = df.join(median_areas, on=['test_image_id', 'class_name'])
        
        # Calculate deviation percentage
        df_with_deviation = df_with_median.with_columns([
            ((pl.col('Area') - pl.col('median_area')).abs() / pl.col('median_area') * 100).alias('deviation_pct')
        ])
        
        # Filter out annotations with >30% deviation
        threshold = 30
        cleaned = df_with_deviation.filter(pl.col('deviation_pct') <= threshold)
        
        removed = len(df_with_deviation) - len(cleaned)
        print(f"   Removed {removed} annotations with >{threshold}% deviation")
        
        # Drop temporary columns
        return cleaned.drop(['median_area', 'deviation_pct'])
    
    def handle_zoom_tilt_issues(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Handle zoom and tilt issues using z-score analysis per image
        """
        print("📐 Handling zoom and tilt issues...")
        
        # Calculate image statistics
        image_stats = df.group_by('test_image_id').agg([
            pl.col('Area').mean().alias('image_mean'),
            pl.col('Area').std().alias('image_std')
        ])
        
        # Join back and calculate z-scores
        df_with_stats = df.join(image_stats, on='test_image_id')
        
        df_with_zscore = df_with_stats.with_columns([
            ((pl.col('Area') - pl.col('image_mean')) / pl.col('image_std')).alias('z_score')
        ])
        
        # Remove extreme outliers (z-score > 4)
        z_threshold = 4
        cleaned = df_with_zscore.filter(pl.col('z_score').abs() <= z_threshold)
        
        removed = len(df_with_zscore) - len(cleaned)
        print(f"   Removed {removed} extreme outliers (z-score > {z_threshold})")
        
        # Drop temporary columns
        return cleaned.drop(['image_mean', 'image_std', 'z_score'])
    
    def filter_valid_images(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Keep only images with both problematic and reference SKUs
        """
        print("🔄 Filtering valid images...")
        
        # Count problematic and reference SKUs per image
        image_counts = df.group_by('test_image_id').agg([
            pl.col('Prob/Ref').filter(pl.col('Prob/Ref') == 'problem').count().alias('problem_count'),
            pl.col('Prob/Ref').filter(pl.col('Prob/Ref') == 'reference').count().alias('reference_count')
        ])
        
        # Filter images with both types
        valid_images = image_counts.filter(
            (pl.col('problem_count') > 0) & (pl.col('reference_count') > 0)
        ).select('test_image_id')
        
        # Filter main dataframe
        filtered = df.join(valid_images, on='test_image_id', how='inner')
        
        removed_images = df.select('test_image_id').n_unique() - valid_images.height
        print(f"   Removed {removed_images} images without both SKU types")
        
        return filtered
    
    def detect_human_errors(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Detect and remove human annotation errors
        """
        print("👁️  Detecting human errors...")
        
        # Calculate class statistics
        class_stats = df.group_by('class_name').agg([
            pl.col('Area').mean().alias('class_mean'),
            pl.col('Area').std().alias('class_std'),
            pl.col('Area').count().alias('class_count')
        ])
        
        # Filter classes with sufficient data (at least 3 annotations)
        reliable_classes = class_stats.filter(pl.col('class_count') >= 3)
        
        # Join back and calculate z-scores
        df_with_class_stats = df.join(reliable_classes, on='class_name', how='inner')
        
        df_with_class_zscore = df_with_class_stats.with_columns([
            ((pl.col('Area') - pl.col('class_mean')) / pl.col('class_std')).alias('class_z_score')
        ])
        
        # Remove statistical outliers (z-score > 3)
        z_threshold = 3
        cleaned = df_with_class_zscore.filter(pl.col('class_z_score').abs() <= z_threshold)
        
        removed = len(df_with_class_zscore) - len(cleaned)
        print(f"   Removed {removed} potential human errors")
        
        # Drop temporary columns
        return cleaned.drop(['class_mean', 'class_std', 'class_count', 'class_z_score'])
    
    def clean_data(self) -> pl.DataFrame:
        """
        Complete data cleaning pipeline
        """
        print("\n🧹 Starting comprehensive data cleaning...")
        
        df = self.raw_data.clone()
        initial_count = len(df)
        
        # Step 1: Remove annotation variations
        df = self.remove_annotation_variations(df)
        
        # Step 2: Handle zoom and tilt issues
        df = self.handle_zoom_tilt_issues(df)
        
        # Step 3: Filter valid images
        df = self.filter_valid_images(df)
        
        # Step 4: Detect human errors
        df = self.detect_human_errors(df)
        
        self.cleaned_data = df
        self.stats['cleaned_rows'] = len(df)
        self.stats['outliers_removed'] = initial_count - len(df)
        
        print(f"\n✅ Data cleaning completed!")
        print(f"   Original: {initial_count} rows")
        print(f"   Cleaned: {len(df)} rows")
        print(f"   Outliers removed: {self.stats['outliers_removed']}")
        
        return df
    
    def calculate_ratios(self) -> pl.DataFrame:
        """
        Calculate ratios between problematic and reference SKUs
        """
        print("\n📊 Calculating ratios...")
        
        if self.cleaned_data is None:
            raise ValueError("Data must be cleaned first")
        
        # Separate problematic and reference SKUs
        problems = self.cleaned_data.filter(pl.col('Prob/Ref') == 'problem')
        references = self.cleaned_data.filter(pl.col('Prob/Ref') == 'reference')
        
        if problems.height == 0 or references.height == 0:
            print("⚠️  No valid SKU pairs found")
            self.ratio_data = pl.DataFrame()
            self.stats['total_ratios'] = 0
            self.stats['images_processed'] = 0
            return pl.DataFrame()
        
        # Cross join to create all possible pairs
        ratios = problems.join(
            references,
            on=['test_image_id', 'category_name'],
            how='inner',
            suffix='_ref'
        )
        
        # Calculate ratios
        ratios = ratios.with_columns([
            (pl.col('Area_ref') / pl.col('Area')).alias('ratio')
        ])
        
        # Filter valid ratios
        ratios = ratios.filter(
            pl.col('ratio').is_finite() & (pl.col('ratio') > 0)
        )
        
        # Select and rename columns
        ratios = ratios.select([
            'category_name',
            pl.col('group_name').alias('problematic_group_name'),
            pl.col('class_name').alias('problematic_class_name'),
            pl.col('group_name_ref').alias('reference_group_name'),
            pl.col('class_name_ref').alias('reference_class_name'),
            'ratio',
            'test_image_id'
        ])
        
        self.ratio_data = ratios
        self.stats['total_ratios'] = len(ratios)
        self.stats['images_processed'] = ratios.select('test_image_id').n_unique()
        
        print(f"✅ Ratio calculation completed!")
        print(f"   Total ratios: {self.stats['total_ratios']}")
        print(f"   Images processed: {self.stats['images_processed']}")
        
        return ratios
    
    def generate_final_output(self) -> pl.DataFrame:
        """
        Generate final output in requested format
        """
        print("\n📋 Generating final output...")
        
        if self.ratio_data is None or self.ratio_data.height == 0:
            print("⚠️  No ratio data available")
            return pl.DataFrame()
        
        # Group by required columns and aggregate ratios
        final_output = self.ratio_data.group_by([
            'category_name',
            'problematic_group_name',
            'problematic_class_name',
            'reference_group_name',
            'reference_class_name'
        ]).agg([
            pl.col('ratio').alias('ratio_list'),
            pl.col('ratio').count().alias('ratio_count'),
            pl.col('ratio').mean().alias('ratio_mean'),
            pl.col('ratio').median().alias('ratio_median'),
            pl.col('ratio').std().alias('ratio_std'),
            pl.col('ratio').min().alias('ratio_min'),
            pl.col('ratio').max().alias('ratio_max')
        ])
        
        # Sort for better organization
        final_output = final_output.sort(['category_name', 'problematic_group_name', 'problematic_class_name'])
        
        print(f"✅ Final output generated!")
        print(f"   Total combinations: {len(final_output)}")
        print(f"   Avg ratios per combination: {final_output.select('ratio_count').mean().item():.1f}")
        
        return final_output
    
    def save_results(self, output_path: str) -> bool:
        """
        Save all results to Excel file
        """
        print(f"\n💾 Saving results to: {output_path}")
        
        try:
            # Convert to pandas for Excel writing (Polars doesn't have Excel writer yet)
            raw_pandas = self.raw_data.to_pandas()
            cleaned_pandas = self.cleaned_data.to_pandas()
            ratios_pandas = self.ratio_data.to_pandas()
            final_pandas = self.generate_final_output().to_pandas()
            
            # Create summary stats
            summary_stats = pl.DataFrame({
                'Metric': [
                    'Total Images Processed',
                    'Total Ratios Calculated',
                    'Outliers Removed',
                    'Unique Problematic SKUs',
                    'Unique Reference SKUs',
                    'Categories Processed',
                    'Original Data Rows',
                    'Cleaned Data Rows'
                ],
                'Value': [
                    self.stats['images_processed'],
                    self.stats['total_ratios'],
                    self.stats['outliers_removed'],
                    self.ratio_data.select('problematic_class_name').n_unique() if self.ratio_data is not None and self.ratio_data.height > 0 else 0,
                    self.ratio_data.select('reference_class_name').n_unique() if self.ratio_data is not None and self.ratio_data.height > 0 else 0,
                    self.stats['categories'],
                    self.stats['original_rows'],
                    self.stats['cleaned_rows']
                ]
            }).to_pandas()
            
            # Save to Excel
            import pandas as pd
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                raw_pandas.to_excel(writer, sheet_name='01_Raw_Data', index=False)
                cleaned_pandas.to_excel(writer, sheet_name='02_Cleaned_Data', index=False)
                ratios_pandas.to_excel(writer, sheet_name='03_All_Ratios', index=False)
                final_pandas.to_excel(writer, sheet_name='04_Final_Output', index=False)
                summary_stats.to_excel(writer, sheet_name='05_Summary_Stats', index=False)
            
            print("✅ Results saved successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            return False

def main():
    """
    Main execution function
    """
    print("🚀 Fresh SKU Ratio Analyzer (Polars)")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = SKURatioAnalyzer()
    
    # Hide tkinter window
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
        # Load data
        if not analyzer.load_data(input_file_path):
            return
        
        # Clean data
        analyzer.clean_data()
        
        # Calculate ratios
        analyzer.calculate_ratios()
        
        # Generate timestamp and save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.dirname(input_file_path)
        output_file_path = os.path.join(output_dir, f'polars_sku_analysis_{timestamp}.xlsx')
        
        if analyzer.save_results(output_file_path):
            print(f"\n🎉 Analysis completed successfully!")
            print(f"📁 Results saved to: {output_file_path}")
            
            messagebox.showinfo(
                "Success",
                f"Analysis completed successfully!\n\n"
                f"Results saved to:\n{output_file_path}\n\n"
                f"Summary:\n"
                f"- Images processed: {analyzer.stats['images_processed']}\n"
                f"- Ratios calculated: {analyzer.stats['total_ratios']}\n"
                f"- Outliers removed: {analyzer.stats['outliers_removed']}"
            )
        else:
            messagebox.showerror("Error", "Failed to save results")
    
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"❌ {error_msg}")
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    main()