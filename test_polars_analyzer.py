import polars as pl
import numpy as np
from sku_ratio_analyzer_polars import SKURatioAnalyzer
import os

def create_sample_data():
    """
    Create sample data to test the Polars analyzer
    """
    print("📝 Creating sample data for Polars analyzer...")
    
    # Sample data with various scenarios
    sample_data = [
        # Image 1 - Normal case with multiple annotations
        {'test_image_id': 'img_001', 'category_name': 'shampoo', 'group_name': 'group_a', 'class_name': 'shampoo_100g', 'Area': 1000, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_001', 'category_name': 'shampoo', 'group_name': 'group_a', 'class_name': 'shampoo_100g', 'Area': 1050, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_001', 'category_name': 'shampoo', 'group_name': 'group_b', 'class_name': 'shampoo_200g', 'Area': 2000, 'Prob/Ref': 'problem'},
        {'test_image_id': 'img_001', 'category_name': 'shampoo', 'group_name': 'group_b', 'class_name': 'shampoo_200g', 'Area': 2100, 'Prob/Ref': 'problem'},
        
        # Image 2 - Different zoom level
        {'test_image_id': 'img_002', 'category_name': 'shampoo', 'group_name': 'group_a', 'class_name': 'shampoo_100g', 'Area': 1500, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_002', 'category_name': 'shampoo', 'group_name': 'group_c', 'class_name': 'shampoo_500g', 'Area': 7500, 'Prob/Ref': 'problem'},
        
        # Image 3 - Tilt issue (outlier)
        {'test_image_id': 'img_003', 'category_name': 'conditioner', 'group_name': 'group_d', 'class_name': 'conditioner_100g', 'Area': 1200, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_003', 'category_name': 'conditioner', 'group_name': 'group_d', 'class_name': 'conditioner_100g', 'Area': 800, 'Prob/Ref': 'reference'},  # Tilt outlier
        {'test_image_id': 'img_003', 'category_name': 'conditioner', 'group_name': 'group_e', 'class_name': 'conditioner_200g', 'Area': 2400, 'Prob/Ref': 'problem'},
        
        # Image 4 - Human error (wrong annotation)
        {'test_image_id': 'img_004', 'category_name': 'toothpaste', 'group_name': 'group_f', 'class_name': 'toothpaste_100g', 'Area': 800, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_004', 'category_name': 'toothpaste', 'group_name': 'group_f', 'class_name': 'toothpaste_100g', 'Area': 850, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_004', 'category_name': 'toothpaste', 'group_name': 'group_f', 'class_name': 'toothpaste_100g', 'Area': 50, 'Prob/Ref': 'reference'},   # Human error
        {'test_image_id': 'img_004', 'category_name': 'toothpaste', 'group_name': 'group_g', 'class_name': 'toothpaste_200g', 'Area': 1600, 'Prob/Ref': 'problem'},
        
        # Image 5 - Only problematic SKUs (should be filtered out)
        {'test_image_id': 'img_005', 'category_name': 'soap', 'group_name': 'group_h', 'class_name': 'soap_100g', 'Area': 600, 'Prob/Ref': 'problem'},
        {'test_image_id': 'img_005', 'category_name': 'soap', 'group_name': 'group_h', 'class_name': 'soap_200g', 'Area': 1200, 'Prob/Ref': 'problem'},
        
        # Image 6 - Only reference SKUs (should be filtered out)
        {'test_image_id': 'img_006', 'category_name': 'soap', 'group_name': 'group_i', 'class_name': 'soap_100g', 'Area': 600, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_006', 'category_name': 'soap', 'group_name': 'group_i', 'class_name': 'soap_200g', 'Area': 1200, 'Prob/Ref': 'reference'},
        
        # Image 7 - Multiple annotations with variations
        {'test_image_id': 'img_007', 'category_name': 'detergent', 'group_name': 'group_j', 'class_name': 'detergent_500g', 'Area': 2500, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_007', 'category_name': 'detergent', 'group_name': 'group_j', 'class_name': 'detergent_500g', 'Area': 2600, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_007', 'category_name': 'detergent', 'group_name': 'group_j', 'class_name': 'detergent_500g', 'Area': 2400, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_007', 'category_name': 'detergent', 'group_name': 'group_k', 'class_name': 'detergent_1kg', 'Area': 5000, 'Prob/Ref': 'problem'},
        {'test_image_id': 'img_007', 'category_name': 'detergent', 'group_name': 'group_k', 'class_name': 'detergent_1kg', 'Area': 5200, 'Prob/Ref': 'problem'},
        
        # Image 8 - Extreme outlier (should be removed)
        {'test_image_id': 'img_008', 'category_name': 'beverage', 'group_name': 'group_l', 'class_name': 'beverage_330ml', 'Area': 1000, 'Prob/Ref': 'reference'},
        {'test_image_id': 'img_008', 'category_name': 'beverage', 'group_name': 'group_l', 'class_name': 'beverage_330ml', 'Area': 50000, 'Prob/Ref': 'reference'},  # Extreme outlier
        {'test_image_id': 'img_008', 'category_name': 'beverage', 'group_name': 'group_m', 'class_name': 'beverage_500ml', 'Area': 1500, 'Prob/Ref': 'problem'},
    ]
    
    # Create Polars DataFrame
    df = pl.DataFrame(sample_data)
    
    # Save sample data
    sample_file = 'sample_polars_data.csv'
    df.write_csv(sample_file)
    print(f"✅ Sample data saved to: {sample_file}")
    print(f"   - Total rows: {len(df)}")
    print(f"   - Images: {df.select('test_image_id').n_unique()}")
    print(f"   - Categories: {df.select('category_name').n_unique()}")
    
    return sample_file

def test_polars_analyzer():
    """
    Test the Polars-based SKU ratio analyzer
    """
    print("\n🧪 Testing Polars SKU Ratio Analyzer")
    print("=" * 50)
    
    # Create sample data
    sample_file = create_sample_data()
    
    # Initialize analyzer
    analyzer = SKURatioAnalyzer()
    
    try:
        # Load data
        print(f"\n📁 Loading sample data from: {sample_file}")
        if not analyzer.load_data(sample_file):
            print("❌ Failed to load data")
            return
        
        # Clean data
        analyzer.clean_data()
        
        # Calculate ratios
        analyzer.calculate_ratios()
        
        # Generate final output
        final_output = analyzer.generate_final_output()
        
        # Display results
        print("\n📊 Final Results:")
        print("=" * 50)
        print(final_output)
        
        # Display summary statistics
        print("\n📈 Summary Statistics:")
        print("=" * 30)
        for key, value in analyzer.stats.items():
            print(f"   {key}: {value}")
        
        # Save results
        output_file = 'test_polars_results.xlsx'
        if analyzer.save_results(output_file):
            print(f"\n✅ Test results saved to: {output_file}")
        
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
            print(f"🧹 Cleaned up sample file: {sample_file}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def benchmark_polars_vs_pandas():
    """
    Simple benchmark to show Polars performance
    """
    print("\n⚡ Polars Performance Demo")
    print("=" * 30)
    
    # Create larger sample dataset
    print("Creating larger dataset for benchmark...")
    
    # Generate 10,000 rows of sample data
    np.random.seed(42)
    n_rows = 10000
    
    data = {
        'test_image_id': [f'img_{i:04d}' for i in range(n_rows)],
        'category_name': np.random.choice(['shampoo', 'conditioner', 'toothpaste', 'soap'], n_rows),
        'group_name': [f'group_{i}' for i in range(n_rows)],
        'class_name': [f'sku_{i}' for i in range(n_rows)],
        'Area': np.random.normal(1000, 300, n_rows),
        'Prob/Ref': np.random.choice(['problem', 'reference'], n_rows)
    }
    
    # Create Polars DataFrame
    df = pl.DataFrame(data)
    
    print(f"Created dataset with {len(df)} rows")
    
    # Simple operations benchmark
    import time
    
    # Polars operations
    start_time = time.time()
    
    # Group by operations
    result1 = df.group_by('category_name').agg([
        pl.col('Area').mean().alias('mean_area'),
        pl.col('Area').std().alias('std_area'),
        pl.col('Area').count().alias('count')
    ])
    
    # Filter operations
    result2 = df.filter(pl.col('Area') > 1000)
    
    # Join operations (self-join for demo)
    result3 = df.join(df, on='category_name', how='inner')
    
    polars_time = time.time() - start_time
    
    print(f"Polars processing time: {polars_time:.3f} seconds")
    print(f"Group by result shape: {result1.shape}")
    print(f"Filter result shape: {result2.shape}")
    print(f"Join result shape: {result3.shape}")

if __name__ == "__main__":
    # Run the main test
    test_polars_analyzer()
    
    # Run performance demo
    benchmark_polars_vs_pandas() 