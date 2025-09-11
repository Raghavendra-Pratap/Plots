#!/usr/bin/env python3
"""
Test Specific Formulas
Easy script to test and modify specific formulas
"""

import pandas as pd
import numpy as np

def test_custom_formulas():
    """Test custom formulas - modify this function to test your own formulas"""
    print("🧮 TESTING CUSTOM FORMULAS")
    print("=" * 50)
    
    # Create sample data - modify this for your own data
    data = pd.DataFrame({
        'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'y': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        'z': [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
        'score': [85, 92, 78, 95, 88, 91, 76, 94, 89, 93]
    })
    
    print("📊 Original data:")
    print(data)
    print(f"\nShape: {data.shape}")
    print(f"Columns: {list(data.columns)}")
    
    # ========================================
    # MODIFY THESE FORMULAS TO TEST YOUR OWN
    # ========================================
    
    print("\n🧮 APPLYING FORMULAS:")
    print("-" * 40)
    
    # Formula 1: Basic arithmetic
    data['sum_xy'] = data['x'] + data['y']
    print("✅ Formula 1: sum_xy = x + y")
    
    # Formula 2: Multiplication and division
    data['product_ratio'] = (data['x'] * data['y']) / data['z']
    print("✅ Formula 2: product_ratio = (x * y) / z")
    
    # Formula 3: Power and square root
    data['power_sqrt'] = data['x'] ** 2 + np.sqrt(data['y'])
    print("✅ Formula 3: power_sqrt = x² + √y")
    
    # Formula 4: Conditional logic
    data['performance'] = np.where(
        data['score'] >= 90, 'Excellent',
        np.where(data['score'] >= 80, 'Good',
        np.where(data['score'] >= 70, 'Average', 'Needs Improvement'))
    )
    print("✅ Formula 4: performance = conditional based on score")
    
    # Formula 5: Complex business logic
    data['bonus_multiplier'] = np.where(
        (data['score'] >= 90) & (data['category'] == 'A'), 2.0,
        np.where(data['score'] >= 85, 1.5,
        np.where(data['score'] >= 80, 1.2, 1.0))
    )
    data['bonus_amount'] = data['score'] * data['bonus_multiplier']
    print("✅ Formula 5: bonus calculation with category and score")
    
    # Formula 6: Statistical calculations
    data['score_normalized'] = (data['score'] - data['score'].mean()) / data['score'].std()
    print("✅ Formula 6: score_normalized = z-score normalization")
    
    # Formula 7: Rolling calculations (if you have time series data)
    if len(data) > 3:
        data['rolling_avg_3'] = data['score'].rolling(window=3, min_periods=1).mean()
        print("✅ Formula 7: rolling_avg_3 = 3-period rolling average")
    
    # Formula 8: String operations (if you have text data)
    data['category_enhanced'] = data['category'] + '_' + data['performance']
    print("✅ Formula 8: category_enhanced = category + '_' + performance")
    
    # ========================================
    # RESULTS DISPLAY
    # ========================================
    
    print("\n📊 RESULTS:")
    print("-" * 40)
    print(data)
    
    print(f"\n📈 FINAL DATASET:")
    print(f"   Rows: {len(data)}")
    print(f"   Columns: {len(data.columns)}")
    print(f"   New columns added: {len(data.columns) - 5}")  # 5 original columns
    
    # Show summary statistics for numeric columns
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    print(f"\n📊 Summary Statistics for Numeric Columns:")
    print(data[numeric_cols].describe().round(2))
    
    # Show category distributions
    categorical_cols = data.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        print(f"\n📊 Category Distributions:")
        for col in categorical_cols:
            print(f"\n{col}:")
            print(data[col].value_counts())
    
    # ========================================
    # ADD YOUR OWN FORMULAS HERE
    # ========================================
    
    print("\n🔧 ADD YOUR OWN FORMULAS:")
    print("-" * 40)
    print("To add your own formulas, modify this script and add lines like:")
    print("data['your_column'] = your_formula_here")
    print("\nExamples:")
    print("data['custom_calc'] = data['x'] * 2 + data['y'] / 10")
    print("data['conditional'] = np.where(data['score'] > 85, 'High', 'Low')")
    print("data['aggregated'] = data.groupby('category')['score'].transform('mean')")
    
    return data

def test_advanced_formulas():
    """Test more advanced formula patterns"""
    print("\n🚀 ADVANCED FORMULA PATTERNS")
    print("=" * 50)
    
    # Create time series data
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    time_data = pd.DataFrame({
        'date': dates,
        'value': np.random.randn(20).cumsum() + 100,
        'volume': np.random.randint(100, 1000, 20),
        'category': np.random.choice(['A', 'B', 'C'], 20)
    })
    
    print("📊 Time series data:")
    print(time_data.head())
    
    # Advanced formulas
    print("\n🧮 Advanced formulas:")
    
    # 1. Time-based calculations
    time_data['day_of_week'] = time_data['date'].dt.day_name()
    time_data['month'] = time_data['date'].dt.month
    time_data['quarter'] = time_data['date'].dt.quarter
    print("✅ Time-based calculations: day_of_week, month, quarter")
    
    # 2. Lag and lead calculations
    time_data['value_lag1'] = time_data['value'].shift(1)
    time_data['value_lead1'] = time_data['value'].shift(-1)
    time_data['value_change'] = time_data['value'] - time_data['value_lag1']
    print("✅ Lag/lead calculations: lag1, lead1, change")
    
    # 3. Rolling statistics
    time_data['rolling_mean_5'] = time_data['value'].rolling(window=5, min_periods=1).mean()
    time_data['rolling_std_5'] = time_data['value'].rolling(window=5, min_periods=1).std()
    print("✅ Rolling statistics: 5-period mean and std")
    
    # 4. Grouped calculations
    time_data['category_avg'] = time_data.groupby('category')['value'].transform('mean')
    time_data['category_rank'] = time_data.groupby('category')['value'].rank(ascending=False)
    print("✅ Grouped calculations: category average and ranking")
    
    # 5. Complex conditional logic
    time_data['trend'] = np.where(
        time_data['value_change'] > time_data['value_change'].rolling(5).mean(),
        'Up',
        np.where(time_data['value_change'] < time_data['value_change'].rolling(5).mean(), 'Down', 'Stable')
    )
    print("✅ Complex conditional logic: trend detection")
    
    print(f"\n📊 Advanced results (first 10 rows):")
    print(time_data.head(10))
    
    return time_data

def main():
    """Main function to run formula tests"""
    print("🚀 FORMULA TESTING SCRIPT")
    print("=" * 60)
    print("This script demonstrates various formula capabilities.")
    print("Modify the functions to test your own formulas!")
    print("=" * 60)
    
    # Test basic formulas
    basic_data = test_custom_formulas()
    
    # Test advanced formulas
    advanced_data = test_advanced_formulas()
    
    print("\n" + "=" * 60)
    print("🎉 FORMULA TESTING COMPLETED!")
    print("=" * 60)
    print("✅ Basic mathematical operations")
    print("✅ Conditional logic")
    print("✅ Statistical calculations")
    print("✅ Time series operations")
    print("✅ Grouped calculations")
    print("✅ Rolling statistics")
    print("\n💡 To test your own formulas:")
    print("   1. Modify the test_custom_formulas() function")
    print("   2. Add your own data and formulas")
    print("   3. Run: python test_specific_formulas.py")
    print("\n🚀 The formula engine is ready for your custom formulas!")

if __name__ == "__main__":
    main()
