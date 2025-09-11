#!/usr/bin/env python3
"""
Data Validator Utility for Unified Data Studio
Validates data structure, types, and quality
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates data structure, types, and quality"""
    
    def __init__(self):
        self.validation_rules = self._get_default_validation_rules()
    
    def _get_default_validation_rules(self) -> Dict[str, Any]:
        """Get default validation rules"""
        return {
            'max_null_percentage': 50.0,  # Maximum allowed null percentage
            'min_rows': 1,  # Minimum number of rows
            'max_rows': 10000000,  # Maximum number of rows (10M)
            'min_columns': 1,  # Minimum number of columns
            'max_columns': 1000,  # Maximum number of columns
            'max_string_length': 10000,  # Maximum string length
            'allowed_data_types': ['object', 'int64', 'float64', 'bool', 'datetime64[ns]'],
            'required_columns': [],  # List of required column names
            'column_name_pattern': r'^[a-zA-Z_][a-zA-Z0-9_]*$',  # Valid column name pattern
            'max_duplicate_rows': 0.1,  # Maximum allowed duplicate row percentage
            'max_outlier_threshold': 3.0  # Standard deviations for outlier detection
        }
    
    def validate_dataframe(self, df: pd.DataFrame, rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate pandas DataFrame against rules"""
        try:
            if rules is None:
                rules = self.validation_rules
            
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'details': {}
            }
            
            # Basic structure validation
            structure_validation = self._validate_dataframe_structure(df, rules)
            if not structure_validation['valid']:
                validation_result['valid'] = False
                validation_result['errors'].extend(structure_validation['errors'])
            validation_result['details']['structure'] = structure_validation
            
            # Column validation
            column_validation = self._validate_columns(df, rules)
            if not column_validation['valid']:
                validation_result['valid'] = False
                validation_result['errors'].extend(column_validation['errors'])
            validation_result['details']['columns'] = column_validation
            
            # Data quality validation
            quality_validation = self._validate_data_quality(df, rules)
            validation_result['warnings'].extend(quality_validation['warnings'])
            validation_result['details']['quality'] = quality_validation
            
            # Data type validation
            type_validation = self._validate_data_types(df, rules)
            if not type_validation['valid']:
                validation_result['valid'] = False
                validation_result['errors'].extend(type_validation['errors'])
            validation_result['details']['types'] = type_validation
            
            return validation_result
            
        except Exception as e:
            logger.error(f"DataFrame validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'details': {}
            }
    
    def _validate_dataframe_structure(self, df: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate DataFrame structure"""
        validation_result = {
            'valid': True,
            'errors': [],
            'details': {}
        }
        
        # Check row count
        row_count = len(df)
        if row_count < rules['min_rows']:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Too few rows: {row_count} (minimum: {rules['min_rows']})")
        
        if row_count > rules['max_rows']:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Too many rows: {row_count} (maximum: {rules['max_rows']})")
        
        # Check column count
        column_count = len(df.columns)
        if column_count < rules['min_columns']:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Too few columns: {column_count} (minimum: {rules['min_columns']})")
        
        if column_count > rules['max_columns']:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Too many columns: {column_count} (maximum: {rules['max_columns']})")
        
        validation_result['details'] = {
            'row_count': row_count,
            'column_count': column_count
        }
        
        return validation_result
    
    def _validate_columns(self, df: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate DataFrame columns"""
        validation_result = {
            'valid': True,
            'errors': [],
            'details': {}
        }
        
        # Check required columns
        if rules['required_columns']:
            missing_columns = [col for col in rules['required_columns'] if col not in df.columns]
            if missing_columns:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Missing required columns: {missing_columns}")
        
        # Validate column names
        invalid_column_names = []
        for col in df.columns:
            if not re.match(rules['column_name_pattern'], str(col)):
                invalid_column_names.append(col)
        
        if invalid_column_names:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid column names: {invalid_column_names}")
        
        validation_result['details'] = {
            'required_columns': rules['required_columns'],
            'missing_columns': missing_columns if 'missing_columns' in locals() else [],
            'invalid_column_names': invalid_column_names
        }
        
        return validation_result
    
    def _validate_data_quality(self, df: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality"""
        validation_result = {
            'warnings': [],
            'details': {}
        }
        
        # Check for null values
        null_percentages = {}
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            null_percentages[col] = null_percentage
            
            if null_percentage > rules['max_null_percentage']:
                validation_result['warnings'].append(
                    f"High null percentage in column '{col}': {null_percentage:.1f}%"
                )
        
        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        duplicate_percentage = (duplicate_count / len(df)) * 100
        if duplicate_percentage > rules['max_duplicate_rows'] * 100:
            validation_result['warnings'].append(
                f"High duplicate row percentage: {duplicate_percentage:.1f}%"
            )
        
        # Check for outliers in numeric columns
        outlier_info = self._detect_outliers(df, rules)
        if outlier_info['outlier_columns']:
            validation_result['warnings'].append(
                f"Outliers detected in columns: {outlier_info['outlier_columns']}"
            )
        
        validation_result['details'] = {
            'null_percentages': null_percentages,
            'duplicate_count': duplicate_count,
            'duplicate_percentage': duplicate_percentage,
            'outlier_info': outlier_info
        }
        
        return validation_result
    
    def _validate_data_types(self, df: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data types"""
        validation_result = {
            'valid': True,
            'errors': [],
            'details': {}
        }
        
        invalid_types = {}
        for col in df.columns:
            col_type = str(df[col].dtype)
            if col_type not in rules['allowed_data_types']:
                invalid_types[col] = col_type
        
        if invalid_types:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid data types: {invalid_types}")
        
        validation_result['details'] = {
            'column_types': df.dtypes.to_dict(),
            'invalid_types': invalid_types
        }
        
        return validation_result
    
    def _detect_outliers(self, df: pd.DataFrame, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Detect outliers in numeric columns"""
        outlier_info = {
            'outlier_columns': [],
            'outlier_counts': {}
        }
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # Remove null values for outlier detection
                numeric_data = df[col].dropna()
                
                if len(numeric_data) > 0:
                    # Calculate z-scores
                    z_scores = np.abs((numeric_data - numeric_data.mean()) / numeric_data.std())
                    
                    # Count outliers
                    outlier_count = (z_scores > rules['max_outlier_threshold']).sum()
                    
                    if outlier_count > 0:
                        outlier_info['outlier_columns'].append(col)
                        outlier_info['outlier_counts'][col] = outlier_count
        
        return outlier_info
    
    def validate_csv_file(self, file_path: str, rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows for validation
            
            # Validate the DataFrame
            validation_result = self.validate_dataframe(df, rules)
            
            # Add file-specific information
            validation_result['file_path'] = file_path
            validation_result['file_type'] = 'csv'
            
            return validation_result
            
        except Exception as e:
            logger.error(f"CSV validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"CSV validation error: {str(e)}"],
                'warnings': [],
                'details': {},
                'file_path': file_path,
                'file_type': 'csv'
            }
    
    def validate_excel_file(self, file_path: str, rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, nrows=1000)  # Sample first 1000 rows
            
            # Validate the DataFrame
            validation_result = self.validate_dataframe(df, rules)
            
            # Add file-specific information
            validation_result['file_path'] = file_path
            validation_result['file_type'] = 'excel'
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Excel validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Excel validation error: {str(e)}"],
                'warnings': [],
                'details': {},
                'file_path': file_path,
                'file_type': 'excel'
            }
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive data summary"""
        try:
            summary = {
                'basic_info': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
                },
                'column_info': {},
                'data_quality': {
                    'null_counts': {},
                    'unique_counts': {},
                    'duplicate_rows': df.duplicated().sum()
                },
                'statistical_info': {}
            }
            
            # Column information
            for col in df.columns:
                col_data = df[col]
                col_type = str(col_data.dtype)
                
                summary['column_info'][col] = {
                    'data_type': col_type,
                    'null_count': col_data.isnull().sum(),
                    'null_percentage': round((col_data.isnull().sum() / len(df)) * 100, 2),
                    'unique_count': col_data.nunique(),
                    'unique_percentage': round((col_data.nunique() / len(df)) * 100, 2)
                }
                
                # Statistical information for numeric columns
                if col_type in ['int64', 'float64']:
                    numeric_data = col_data.dropna()
                    if len(numeric_data) > 0:
                        summary['statistical_info'][col] = {
                            'min': float(numeric_data.min()),
                            'max': float(numeric_data.max()),
                            'mean': float(numeric_data.mean()),
                            'median': float(numeric_data.median()),
                            'std': float(numeric_data.std()),
                            'q25': float(numeric_data.quantile(0.25)),
                            'q75': float(numeric_data.quantile(0.75))
                        }
            
            return summary
            
        except Exception as e:
            logger.error(f"Data summary generation failed: {e}")
            return {'error': str(e)}
    
    def suggest_data_improvements(self, df: pd.DataFrame) -> List[str]:
        """Suggest improvements for data quality"""
        suggestions = []
        
        # Check for high null percentages
        for col in df.columns:
            null_percentage = (df[col].isnull().sum() / len(df)) * 100
            if null_percentage > 20:
                suggestions.append(f"Consider handling null values in column '{col}' ({null_percentage:.1f}% null)")
        
        # Check for low unique values (potential categorical)
        for col in df.columns:
            unique_percentage = (df[col].nunique() / len(df)) * 100
            if unique_percentage < 5 and df[col].dtype == 'object':
                suggestions.append(f"Column '{col}' has low unique values ({unique_percentage:.1f}%) - consider converting to categorical")
        
        # Check for mixed data types
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains mixed types
                type_counts = df[col].apply(type).value_counts()
                if len(type_counts) > 1:
                    suggestions.append(f"Column '{col}' contains mixed data types - consider data cleaning")
        
        # Check for potential outliers
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                numeric_data = df[col].dropna()
                if len(numeric_data) > 0:
                    z_scores = np.abs((numeric_data - numeric_data.mean()) / numeric_data.std())
                    outlier_count = (z_scores > 3).sum()
                    if outlier_count > 0:
                        suggestions.append(f"Column '{col}' contains {outlier_count} potential outliers")
        
        return suggestions
