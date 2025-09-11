# Enhanced SKU Ratio Analyzer

## Overview

The Enhanced SKU Ratio Analyzer is a comprehensive solution for determining product sizes based on annotation areas in images. It addresses the common challenges in SKU detection processes and provides robust ratio calculations between problematic and reference SKUs.

## Problem Statement

In SKU detection processes, you need to determine the size of products (out of two or more similar-looking products) based on their annotation areas. The process involves:

1. **Reference SKUs**: Products that appear consistently across multiple images (known sizes)
2. **Problematic SKUs**: Products whose sizes need to be determined by comparing their annotation areas to reference SKUs

## Challenges Addressed

The analyzer handles the following blockers:

1. **Different zoom levels**: Images captured at different zoom levels create outliers in area data
2. **Tilt issues**: Users sometimes capture images at angles, resulting in different areas for the same product
3. **Annotation variations**: Multiple annotations of the same product can have slightly different areas
4. **Missing data**: Some images have only problematic SKUs or only reference SKUs
5. **Human errors**: Incorrect annotations, wrong class assignments, or size misclassifications

## Features

### 🔧 Robust Data Cleaning
- **Annotation variation removal**: Uses median-based filtering to remove inconsistent annotations
- **Zoom/tilt outlier detection**: Identifies and removes extreme outliers using z-score analysis
- **Image filtering**: Only processes images with both problematic and reference SKUs
- **Human error detection**: Removes statistical outliers that likely represent annotation errors

### 📊 Advanced Ratio Calculation
- **Relative ratios**: Uses ratios within the same image to handle zoom/tilt issues
- **Comprehensive pairing**: Calculates all possible ratios between problematic and reference SKUs
- **Statistical aggregation**: Provides mean, median, standard deviation, and range for each ratio combination

### 📋 Flexible Output Format
- **Requested format**: Outputs data in the exact format you specified
- **Multiple sheets**: Excel output with raw data, cleaned data, all ratios, and final results
- **Summary statistics**: Comprehensive overview of the analysis process

## Input Data Format

Your CSV file should have the following columns:

| Column | Description |
|--------|-------------|
| `test_image_id` | Unique identifier for each image |
| `category_name` | Product category (shampoo, conditioner, etc.) |
| `group_name` | Groups similar-looking products with same packshot |
| `class_name` | Actual SKU/product name |
| `Area` | Annotation area (pixel area of bounding box) |
| `Prob/Ref` | Whether this SKU is "problematic" or "reference" |

## Output Format

The final output includes:

| Column | Description |
|--------|-------------|
| `category_name` | Product category |
| `problematic_group_name` | Group of the problematic SKU |
| `problematic_class_name` | Name of the problematic SKU |
| `reference_group_name` | Group of the reference SKU |
| `reference_class_name` | Name of the reference SKU |
| `ratio_list` | List of all calculated ratios |
| `ratio_count` | Number of ratios in the list |
| `ratio_mean` | Mean of all ratios |
| `ratio_median` | Median of all ratios |
| `ratio_std` | Standard deviation of ratios |
| `ratio_min` | Minimum ratio value |
| `ratio_max` | Maximum ratio value |

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required packages:
   ```bash
   pip install pandas numpy openpyxl tkinter
   ```

## Usage

### Method 1: Interactive GUI
```bash
python enhanced_sku_ratio_analyzer.py
```
This will open a file dialog to select your CSV file.

### Method 2: Programmatic Usage
```python
from enhanced_sku_ratio_analyzer import SKURatioAnalyzer

# Initialize analyzer
analyzer = SKURatioAnalyzer()

# Load and validate data
analyzer.load_and_validate_data('your_data.csv')

# Clean the data
analyzer.clean_data()

# Calculate ratios
analyzer.calculate_ratios()

# Generate final output
final_output = analyzer.generate_final_output()

# Save results
analyzer.save_results('output.xlsx')
```

### Method 3: Test with Sample Data
```bash
python test_enhanced_analyzer.py
```

## Output Files

The analyzer creates an Excel file with multiple sheets:

1. **01_Raw_Data**: Original input data
2. **02_Cleaned_Data**: Data after outlier removal and cleaning
3. **03_All_Ratios**: All calculated ratios with image IDs
4. **04_Final_Output**: Final aggregated results in requested format
5. **05_Summary_Stats**: Summary statistics of the analysis

## Key Algorithms

### 1. Annotation Variation Removal
- Calculates median area for each SKU within each image
- Removes annotations that deviate more than 30% from the median
- Reduces noise from inconsistent annotations

### 2. Zoom/Tilt Outlier Detection
- Calculates z-score for each annotation relative to the image mean
- Removes annotations with z-score > 4 (extreme outliers)
- Handles different zoom levels and tilt issues

### 3. Human Error Detection
- Requires minimum 3 annotations per class for reliability
- Uses z-score analysis relative to class statistics
- Removes annotations with z-score > 3 (statistical outliers)

### 4. Ratio Calculation
- Calculates Reference Area / Problematic Area for each pair
- Only includes ratios from images with both SKU types
- Handles division by zero and invalid values

## Configuration

You can adjust the following parameters in the code:

- **Annotation deviation threshold**: Currently 30% (line 67)
- **Zoom/tilt outlier threshold**: Currently z-score > 4 (line 95)
- **Human error threshold**: Currently z-score > 3 (line 140)
- **Minimum annotations per class**: Currently 3 (line 125)

## Example Results

For a shampoo category with:
- Reference SKU: shampoo_100g (Area: 1000)
- Problematic SKU: shampoo_200g (Area: 2000)

The ratio would be: 1000/2000 = 0.5

This indicates the reference SKU is half the size of the problematic SKU.

## Troubleshooting

### Common Issues

1. **"No valid ratios could be calculated"**
   - Check if your images have both problematic and reference SKUs
   - Verify the 'Prob/Ref' column contains only 'problem' or 'reference'

2. **"Missing required columns"**
   - Ensure your CSV has all required columns with exact names
   - Check for extra spaces in column names

3. **"Area column contains no valid numeric data"**
   - Verify the Area column contains only numbers
   - Remove any text or special characters

### Performance Tips

- For large datasets (>10,000 rows), the analysis may take several minutes
- The analyzer automatically handles memory efficiently
- Consider splitting very large datasets into smaller chunks

## Comparison with Previous Solutions

This enhanced analyzer improves upon previous solutions by:

1. **Better outlier detection**: More sophisticated statistical methods
2. **Comprehensive error handling**: Addresses all mentioned blockers
3. **Flexible output**: Produces the exact format requested
4. **Robust validation**: Extensive data validation and error checking
5. **Detailed reporting**: Comprehensive statistics and progress tracking

## Support

If you encounter any issues or need modifications:

1. Check the console output for detailed error messages
2. Verify your input data format matches the requirements
3. Review the summary statistics to understand the analysis results
4. Test with the sample data first to ensure everything works

## Future Enhancements

Potential improvements for future versions:

1. **Machine learning integration**: Use ML models for better outlier detection
2. **Batch processing**: Handle multiple files simultaneously
3. **Visualization**: Add charts and graphs for ratio analysis
4. **API integration**: Web-based interface for easier access
5. **Real-time processing**: Stream processing for live data feeds 