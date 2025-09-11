#!/usr/bin/env python3
"""
DuckDB Service for Complex Data Processing and Analytics
Handles large datasets, complex SQL queries, and multi-level analytics
"""

import duckdb
import pandas as pd
import numpy as np
import logging
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import tempfile
import json

logger = logging.getLogger(__name__)

class DuckDBService:
    def __init__(self):
        """Initialize DuckDB service with in-memory database"""
        self.conn = None
        self.is_healthy_status = False
        self.initialize_duckdb()
    
    def initialize_duckdb(self):
        """Initialize DuckDB connection and extensions"""
        try:
            # Create in-memory DuckDB connection
            self.conn = duckdb.connect(':memory:')
            
            # Install and load necessary extensions
            self.conn.install_extension('httpfs')
            self.conn.load_extension('httpfs')
            self.conn.install_extension('parquet')
            self.conn.load_extension('parquet')
            
            # Configure DuckDB for optimal performance
            self.conn.execute("SET memory_limit='2GB'")
            self.conn.execute("SET threads=4")
            
            self.is_healthy_status = True
            logger.info("DuckDB initialized successfully")
            
        except Exception as e:
            logger.error(f"DuckDB initialization failed: {e}")
            self.is_healthy_status = False
    
    def is_healthy(self) -> bool:
        """Check if DuckDB service is healthy"""
        return self.is_healthy_status
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process uploaded file with DuckDB"""
        try:
            start_time = time.time()
            
            # Read file based on type
            if file_path.endswith('.csv'):
                # Process CSV with DuckDB
                result = self.conn.execute(f"SELECT * FROM read_csv_auto('{file_path}')").fetchdf()
                
            elif file_path.endswith('.parquet'):
                # Read Parquet directly with DuckDB
                result = self.conn.execute(f"SELECT * FROM read_parquet('{file_path}')").fetchdf()
                
            elif file_path.endswith(('.xlsx', '.xls')):
                # Convert Excel to CSV first, then process
                import openpyxl
                wb = openpyxl.load_workbook(file_path, data_only=True)
                sheet = wb.active
                
                # Convert to DataFrame
                data = []
                for row in sheet.iter_rows(values_only=True):
                    data.append(row)
                
                df = pd.DataFrame(data[1:], columns=data[0])
                result = df
                
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
            
            processing_time = time.time() - start_time
            
            # Analyze data structure
            analysis = self.analyze_data_structure(result)
            
            return {
                'filename': os.path.basename(file_path),
                'row_count': len(result),
                'column_count': len(result.columns),
                'columns': list(result.columns),
                'data_types': result.dtypes.to_dict(),
                'processing_time': processing_time,
                'analysis': analysis,
                'sample_data': result.head(10).to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            raise
    
    def execute_query(self, query: str, data_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute complex SQL query on data sources"""
        try:
            start_time = time.time()
            
            # Register data sources with DuckDB
            for source in data_sources:
                if 'data' in source and 'name' in source:
                    # Convert data to DataFrame if needed
                    if isinstance(source['data'], list):
                        df = pd.DataFrame(source['data'])
                    else:
                        df = source['data']
                    
                    # Register as table
                    table_name = source['name'].replace(' ', '_').lower()
                    self.conn.register(table_name, df)
            
            # Execute query
            result = self.conn.execute(query).fetchdf()
            
            execution_time = time.time() - start_time
            
            return {
                'data': result.to_dict('records'),
                'row_count': len(result),
                'column_count': len(result.columns),
                'columns': list(result.columns),
                'execution_time': execution_time,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def perform_complex_analytics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform complex multi-level analytics"""
        try:
            start_time = time.time()
            
            analytics_type = config.get('type', 'basic')
            data_source = config.get('data_source')
            parameters = config.get('parameters', {})
            
            if analytics_type == 'hierarchical_aggregation':
                result = self._hierarchical_aggregation(data_source, parameters)
            elif analytics_type == 'time_series_analysis':
                result = self._time_series_analysis(data_source, parameters)
            elif analytics_type == 'statistical_analysis':
                result = self._statistical_analysis(data_source, parameters)
            elif analytics_type == 'multi_dimensional_analysis':
                result = self._multi_dimensional_analysis(data_source, parameters)
            else:
                result = self._basic_analytics(data_source, parameters)
            
            execution_time = time.time() - start_time
            
            return {
                'analytics_type': analytics_type,
                'result': result,
                'execution_time': execution_time,
                'complexity_level': self._calculate_complexity_level(config),
                'parameters': parameters
            }
            
        except Exception as e:
            logger.error(f"Complex analytics failed: {e}")
            raise
    
    def _hierarchical_aggregation(self, data_source: str, parameters: Dict) -> Dict[str, Any]:
        """Perform hierarchical aggregation analysis"""
        try:
            hierarchy_levels = parameters.get('hierarchy_levels', [])
            aggregation_functions = parameters.get('aggregation_functions', ['COUNT', 'SUM', 'AVG'])
            
            # Build hierarchical query
            select_clause = []
            group_clause = []
            
            for level in hierarchy_levels:
                select_clause.append(f"'{level}' as level_name")
                select_clause.append(f"{level} as level_value")
                group_clause.append(level)
            
            for func in aggregation_functions:
                if func == 'COUNT':
                    select_clause.append("COUNT(*) as count")
                elif func == 'SUM':
                    select_clause.append("SUM(amount) as total_amount")
                elif func == 'AVG':
                    select_clause.append("AVG(amount) as avg_amount")
                elif func == 'PERCENTILE':
                    select_clause.append("PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_amount")
            
            query = f"""
                SELECT {', '.join(select_clause)}
                FROM {data_source}
                GROUP BY {', '.join(group_clause)}
                ORDER BY {', '.join(group_clause)}
            """
            
            result = self.conn.execute(query).fetchdf()
            
            return {
                'type': 'hierarchical_aggregation',
                'data': result.to_dict('records'),
                'hierarchy_levels': hierarchy_levels,
                'aggregation_functions': aggregation_functions
            }
            
        except Exception as e:
            logger.error(f"Hierarchical aggregation failed: {e}")
            raise
    
    def _time_series_analysis(self, data_source: str, parameters: Dict) -> Dict[str, Any]:
        """Perform time series analysis"""
        try:
            time_column = parameters.get('time_column', 'date')
            value_column = parameters.get('value_column', 'value')
            time_granularity = parameters.get('time_granularity', 'day')
            
            # Build time series query
            query = f"""
                SELECT 
                    DATE_TRUNC('{time_granularity}', {time_column}) as time_period,
                    COUNT(*) as count,
                    SUM({value_column}) as total_value,
                    AVG({value_column}) as avg_value,
                    MIN({value_column}) as min_value,
                    MAX({value_column}) as max_value,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {value_column}) as p25_value,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {value_column}) as p75_value
                FROM {data_source}
                WHERE {time_column} IS NOT NULL
                GROUP BY DATE_TRUNC('{time_granularity}', {time_column})
                ORDER BY time_period
            """
            
            result = self.conn.execute(query).fetchdf()
            
            return {
                'type': 'time_series_analysis',
                'data': result.to_dict('records'),
                'time_column': time_column,
                'value_column': value_column,
                'time_granularity': time_granularity
            }
            
        except Exception as e:
            logger.error(f"Time series analysis failed: {e}")
            raise
    
    def _statistical_analysis(self, data_source: str, parameters: Dict) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""
        try:
            numeric_columns = parameters.get('numeric_columns', [])
            
            if not numeric_columns:
                # Auto-detect numeric columns
                schema_query = f"DESCRIBE {data_source}"
                schema = self.conn.execute(schema_query).fetchdf()
                numeric_columns = [col for col in schema['column_name'] if 'int' in str(schema.loc[schema['column_name'] == col, 'column_type'].iloc[0]).lower() or 'float' in str(schema.loc[schema['column_name'] == col, 'column_type'].iloc[0]).lower()]
            
            stats_results = {}
            
            for column in numeric_columns:
                query = f"""
                    SELECT 
                        '{column}' as column_name,
                        COUNT(*) as count,
                        COUNT(DISTINCT {column}) as unique_count,
                        AVG({column}) as mean,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY {column}) as median,
                        MIN({column}) as min_value,
                        MAX({column}) as max_value,
                        STDDEV({column}) as std_dev,
                        VARIANCE({column}) as variance,
                        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {column}) as p25,
                        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {column}) as p75,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY {column}) as p95
                    FROM {data_source}
                    WHERE {column} IS NOT NULL
                """
                
                result = self.conn.execute(query).fetchdf()
                stats_results[column] = result.to_dict('records')[0]
            
            return {
                'type': 'statistical_analysis',
                'results': stats_results,
                'columns_analyzed': numeric_columns
            }
            
        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            raise
    
    def _multi_dimensional_analysis(self, data_source: str, parameters: Dict) -> Dict[str, Any]:
        """Perform multi-dimensional analysis with GROUPING SETS"""
        try:
            dimensions = parameters.get('dimensions', [])
            measures = parameters.get('measures', [])
            
            if not dimensions or not measures:
                raise ValueError("Dimensions and measures must be specified for multi-dimensional analysis")
            
            # Build multi-dimensional query
            select_clause = []
            group_clause = []
            
            for dim in dimensions:
                select_clause.append(dim)
                group_clause.append(dim)
            
            for measure in measures:
                if measure['type'] == 'sum':
                    select_clause.append(f"SUM({measure['column']}) as {measure['name']}")
                elif measure['type'] == 'avg':
                    select_clause.append(f"AVG({measure['column']}) as {measure['name']}")
                elif measure['type'] == 'count':
                    select_clause.append(f"COUNT({measure['column']}) as {measure['name']}")
                elif measure['type'] == 'percentile':
                    select_clause.append(f"PERCENTILE_CONT({measure['percentile']}) WITHIN GROUP (ORDER BY {measure['column']}) as {measure['name']}")
            
            # Create GROUPING SETS for all combinations
            grouping_sets = []
            for i in range(len(dimensions) + 1):
                for combo in self._combinations(dimensions, i):
                    grouping_sets.append(f"({', '.join(combo)})" if combo else "()")
            
            query = f"""
                SELECT {', '.join(select_clause)}
                FROM {data_source}
                GROUP BY GROUPING SETS ({', '.join(grouping_sets)})
                ORDER BY {', '.join(dimensions)}
            """
            
            result = self.conn.execute(query).fetchdf()
            
            return {
                'type': 'multi_dimensional_analysis',
                'data': result.to_dict('records'),
                'dimensions': dimensions,
                'measures': measures,
                'grouping_sets': grouping_sets
            }
            
        except Exception as e:
            logger.error(f"Multi-dimensional analysis failed: {e}")
            raise
    
    def _basic_analytics(self, data_source: str, parameters: Dict) -> Dict[str, Any]:
        """Perform basic analytics"""
        try:
            query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT *) as unique_rows
                FROM {data_source}
            """
            
            result = self.conn.execute(query).fetchdf()
            
            return {
                'type': 'basic_analytics',
                'data': result.to_dict('records'),
                'data_source': data_source
            }
            
        except Exception as e:
            logger.error(f"Basic analytics failed: {e}")
            raise
    
    def _calculate_complexity_level(self, config: Dict[str, Any]) -> int:
        """Calculate complexity level of analytics request"""
        complexity = 1
        
        if config.get('type') == 'hierarchical_aggregation':
            complexity += 2
        elif config.get('type') == 'multi_dimensional_analysis':
            complexity += 3
        elif config.get('type') == 'time_series_analysis':
            complexity += 1
        
        # Add complexity based on parameters
        if config.get('parameters', {}).get('hierarchy_levels'):
            complexity += len(config['parameters']['hierarchy_levels'])
        
        if config.get('parameters', {}).get('dimensions'):
            complexity += len(config['parameters']['dimensions'])
        
        return min(complexity, 10)  # Cap at 10
    
    def analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data structure and provide insights"""
        try:
            analysis = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_analysis': {},
                'data_quality': {},
                'recommendations': []
            }
            
            for column in df.columns:
                col_data = df[column]
                col_type = str(col_data.dtype)
                
                # Basic column analysis
                col_analysis = {
                    'data_type': col_type,
                    'unique_values': col_data.nunique(),
                    'null_count': col_data.isnull().sum(),
                    'null_percentage': (col_data.isnull().sum() / len(col_data)) * 100
                }
                
                # Numeric column analysis
                if col_type in ['int64', 'float64']:
                    col_analysis.update({
                        'min_value': col_data.min(),
                        'max_value': col_data.max(),
                        'mean_value': col_data.mean(),
                        'median_value': col_data.median(),
                        'std_dev': col_data.std()
                    })
                
                # String column analysis
                elif col_type == 'object':
                    col_analysis.update({
                        'max_length': col_data.astype(str).str.len().max(),
                        'min_length': col_data.astype(str).str.len().min(),
                        'avg_length': col_data.astype(str).str.len().mean()
                    })
                
                analysis['column_analysis'][column] = col_analysis
            
            # Data quality assessment
            total_cells = len(df) * len(df.columns)
            null_cells = sum(analysis['column_analysis'][col]['null_count'] for col in df.columns)
            analysis['data_quality']['completeness'] = ((total_cells - null_cells) / total_cells) * 100
            analysis['data_quality']['null_percentage'] = (null_cells / total_cells) * 100
            
            # Generate recommendations
            if analysis['data_quality']['null_percentage'] > 20:
                analysis['recommendations'].append("High percentage of null values detected. Consider data cleaning strategies.")
            
            numeric_cols = [col for col in df.columns if str(df[col].dtype) in ['int64', 'float64']]
            if len(numeric_cols) > 0:
                analysis['recommendations'].append(f"Found {len(numeric_cols)} numeric columns suitable for statistical analysis.")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Data structure analysis failed: {e}")
            return {'error': str(e)}
    
    def export_data(self, config: Dict[str, Any], format: str) -> Dict[str, Any]:
        """Export data in various formats"""
        try:
            query = config.get('query')
            data_source = config.get('data_source')
            
            if query:
                result = self.conn.execute(query).fetchdf()
            elif data_source:
                result = self.conn.execute(f"SELECT * FROM {data_source}").fetchdf()
            else:
                raise ValueError("Either query or data_source must be specified")
            
            # Create export directory
            export_dir = os.path.join(os.getcwd(), 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"export_{timestamp}.{format}"
            file_path = os.path.join(export_dir, filename)
            
            if format == 'csv':
                result.to_csv(file_path, index=False)
            elif format == 'excel':
                result.to_excel(file_path, index=False)
            elif format == 'json':
                result.to_json(file_path, orient='records', indent=2)
            elif format == 'parquet':
                result.to_parquet(file_path, index=False)
            
            file_size = os.path.getsize(file_path)
            
            return {
                'file_path': file_path,
                'file_size': file_size,
                'format': format,
                'row_count': len(result),
                'export_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            raise
    
    def _combinations(self, iterable, r):
        """Return r length subsequences of elements from the input iterable."""
        from itertools import combinations
        return list(combinations(iterable, r))
    
    def cleanup(self):
        """Clean up DuckDB resources"""
        try:
            if self.conn:
                self.conn.close()
                logger.info("DuckDB connection closed")
        except Exception as e:
            logger.error(f"DuckDB cleanup failed: {e}")
