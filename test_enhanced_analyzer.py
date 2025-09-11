import pandas as pd
import numpy as np
from enhanced_sku_ratio_analyzer import SKURatioAnalyzer
import os

def create_sample_data():
    """
    Create sample data to test the enhanced analyzer
    """
    print("📝 Creating sample data...")
    
    # Sample data with various scenarios
    sample_data = [
        # Image 1 - Normal case
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
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Save sample data
    sample_file = 'sample_sku_data.csv'
    df.to_csv(sample_file, index=False)
    print(f"✅ Sample data saved to: {sample_file}")
    print(f"   - Total rows: {len(df)}")
    print(f"   - Images: {df['test_image_id'].nunique()}")
    print(f"   - Categories: {df['category_name'].nunique()}")
    
    return sample_file

def test_enhanced_analyzer():
    """
    Test the enhanced SKU ratio analyzer
    """
    print("\n🧪 Testing Enhanced SKU Ratio Analyzer")
    print("=" * 50)
    
    # Create sample data
    sample_file = create_sample_data()
    
    # Initialize analyzer
    analyzer = SKURatioAnalyzer()
    
    try:
        # Load and validate data
        print(f"\n📁 Loading sample data from: {sample_file}")
        if not analyzer.load_and_validate_data(sample_file):
            print("❌ Failed to load data")
            return
        
        # Clean the data
        analyzer.clean_data()
        
        # Calculate ratios
        analyzer.calculate_ratios()
        
        # Generate final output
        final_output = analyzer.generate_final_output()
        
        # Display results
        print("\n📊 Final Results:")
        print("=" * 30)
        print(final_output.to_string(index=False))
        
        # Save results
        output_file = 'test_results.xlsx'
        if analyzer.save_results(output_file):
            print(f"\n✅ Test results saved to: {output_file}")
        
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
            print(f"🧹 Cleaned up sample file: {sample_file}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_enhanced_analyzer() 