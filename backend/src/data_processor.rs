use anyhow::{Result, anyhow};
use ndarray::{Array1, Array2};
use polars::prelude::*;
use serde_json::Value;
use std::collections::HashMap;
use tracing::{info, warn};

pub struct DataProcessor {
    operations: HashMap<String, Box<dyn Fn(&[f64], Option<&Value>) -> Result<Value> + Send + Sync>>,
}

impl DataProcessor {
    pub async fn new() -> Self {
        let mut processor = DataProcessor {
            operations: HashMap::new(),
        };
        
        // Register built-in operations
        processor.register_operations();
        
        info!("Data processor initialized with {} operations", processor.operations.len());
        processor
    }
    
    fn register_operations(&mut self) {
        // Statistical operations
        self.operations.insert("mean".to_string(), Box::new(|data, _| {
            let array = Array1::from_vec(data.to_vec());
            let mean = array.mean().unwrap_or(0.0);
            Ok(serde_json::json!({
                "mean": mean,
                "count": data.len()
            }))
        }));
        
        self.operations.insert("std".to_string(), Box::new(|data, _| {
            let array = Array1::from_vec(data.to_vec());
            let mean = array.mean().unwrap_or(0.0);
            let variance = array.iter().map(|&x| (x - mean).powi(2)).sum::<f64>() / data.len() as f64;
            let std = variance.sqrt();
            Ok(serde_json::json!({
                "std": std,
                "variance": variance,
                "count": data.len()
            }))
        }));
        
        self.operations.insert("min_max".to_string(), Box::new(|data, _| {
            let min = data.iter().fold(f64::INFINITY, |a, &b| a.min(b));
            let max = data.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
            Ok(serde_json::json!({
                "min": min,
                "max": max,
                "range": max - min,
                "count": data.len()
            }))
        }));
        
        // Mathematical operations
        self.operations.insert("sum".to_string(), Box::new(|data, _| {
            let sum: f64 = data.iter().sum();
            Ok(serde_json::json!({
                "sum": sum,
                "count": data.len()
            }))
        }));
        
        self.operations.insert("product".to_string(), Box::new(|data, _| {
            let product: f64 = data.iter().product();
            Ok(serde_json::json!({
                "product": product,
                "count": data.len()
            }))
        }));
        
        // Advanced operations
        self.operations.insert("percentiles".to_string(), Box::new(|data, params| {
            let mut sorted_data = data.to_vec();
            sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
            
            let percentiles = params.and_then(|p| p.get("percentiles"))
                .and_then(|p| p.as_array())
                .map(|arr| arr.iter().filter_map(|v| v.as_f64()).collect::<Vec<f64>>())
                .unwrap_or_else(|| vec![25.0, 50.0, 75.0, 90.0, 95.0, 99.0]);
            
            let mut results = HashMap::new();
            for percentile in percentiles {
                let index = (percentile / 100.0 * (sorted_data.len() - 1) as f64).round() as usize;
                let index = index.min(sorted_data.len() - 1);
                results.insert(format!("p{}", percentile), sorted_data[index]);
            }
            
            Ok(serde_json::json!(results))
        }));
        
        self.operations.insert("histogram".to_string(), Box::new(|data, params| {
            let bins = params.and_then(|p| p.get("bins"))
                .and_then(|p| p.as_u64())
                .unwrap_or(10) as usize;
            
            let min = data.iter().fold(f64::INFINITY, |a, &b| a.min(b));
            let max = data.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
            let bin_width = (max - min) / bins as f64;
            
            let mut histogram = vec![0; bins];
            for &value in data {
                let bin_index = ((value - min) / bin_width).floor() as usize;
                let bin_index = bin_index.min(bins - 1);
                histogram[bin_index] += 1;
            }
            
            let bin_edges: Vec<f64> = (0..=bins).map(|i| min + i as f64 * bin_width).collect();
            
            Ok(serde_json::json!({
                "histogram": histogram,
                "bin_edges": bin_edges,
                "bin_width": bin_width,
                "count": data.len()
            }))
        }));
        
        // Matrix operations
        self.operations.insert("matrix_multiply".to_string(), Box::new(|data, params| {
            let matrix_size = params.and_then(|p| p.get("matrix_size"))
                .and_then(|p| p.as_u64())
                .unwrap_or(2) as usize;
            
            if data.len() != matrix_size * matrix_size * 2 {
                return Err(anyhow!("Data length must be 2 * matrix_size^2 for matrix multiplication"));
            }
            
            let split_point = matrix_size * matrix_size;
            let matrix_a_data = &data[..split_point];
            let matrix_b_data = &data[split_point..];
            
            let matrix_a = Array2::from_shape_vec((matrix_size, matrix_size), matrix_a_data.to_vec())?;
            let matrix_b = Array2::from_shape_vec((matrix_size, matrix_size), matrix_b_data.to_vec())?;
            
            let result = matrix_a.dot(&matrix_b);
            
            Ok(serde_json::json!({
                "result": result.into_raw_vec_and_offset().0,
                "dimensions": [matrix_size, matrix_size],
                "operation": "matrix_multiplication"
            }))
        }));
        
        // Custom operations
        self.operations.insert("custom".to_string(), Box::new(|data, params| {
            let operation = params.and_then(|p| p.get("operation"))
                .and_then(|p| p.as_str())
                .ok_or_else(|| anyhow!("Custom operation requires 'operation' parameter"))?;
            
            match operation {
                "normalize" => {
                    let mean = data.iter().sum::<f64>() / data.len() as f64;
                    let std = (data.iter().map(|&x| (x - mean).powi(2)).sum::<f64>() / data.len() as f64).sqrt();
                    let normalized: Vec<f64> = data.iter().map(|&x| (x - mean) / std).collect();
                    
                    Ok(serde_json::json!({
                        "normalized_data": normalized,
                        "mean": mean,
                        "std": std,
                        "count": data.len()
                    }))
                }
                "log_transform" => {
                    let transformed: Vec<f64> = data.iter()
                        .map(|&x| if x > 0.0 { x.ln() } else { f64::NEG_INFINITY })
                        .collect();
                    
                    Ok(serde_json::json!({
                        "transformed_data": transformed,
                        "operation": "log_transform",
                        "count": data.len()
                    }))
                }
                "exponential" => {
                    let transformed: Vec<f64> = data.iter().map(|&x| x.exp()).collect();
                    
                    Ok(serde_json::json!({
                        "transformed_data": transformed,
                        "operation": "exponential",
                        "count": data.len()
                    }))
                }
                _ => Err(anyhow!("Unknown custom operation: {}", operation))
            }
        }));
    }
    
    pub async fn process_data(
        &self,
        data: &[f64],
        operation: &str,
        _parameters: Option<&Value>,
    ) -> Result<Value> {
        info!("Processing data with operation: {}, data size: {}", operation, data.len());
        
        if data.is_empty() {
            return Err(anyhow!("Data cannot be empty"));
        }
        
        let operation_func = self.operations.get(operation)
            .ok_or_else(|| anyhow!("Unknown operation: {}", operation))?;
        
        let result = operation_func(data, _parameters)?;
        
        info!("Data processing completed successfully for operation: {}", operation);
        Ok(result)
    }
    
    pub async fn process_dataframe(
        &self,
        csv_data: &str,
        operations: &[String],
        _parameters: Option<&Value>,
    ) -> Result<Value> {
        info!("Processing DataFrame with {} operations", operations.len());
        
        // Parse CSV data
        let df = CsvReader::new(std::io::Cursor::new(csv_data))
            .finish()
            .map_err(|e| anyhow!("Failed to parse CSV: {}", e))?;
        
        let mut results = Vec::new();
        
        for operation in operations {
            let result = match operation.as_str() {
                "describe" => {
                    // Polars 0.50 doesn't have describe method, using alternative
                    serde_json::json!({
                        "operation": "describe",
                        "columns": df.get_column_names(),
                        "shape": [df.height(), df.width()],
                        "dtypes": df.dtypes().iter().map(|dt| dt.to_string()).collect::<Vec<_>>()
                    })
                }
                "head" => {
                    let head = df.head(Some(10));
                    serde_json::json!({
                        "operation": "head",
                        "rows": head.height(),
                        "columns": head.width(),
                        "data": "Data preview available (to_json not available in Polars 0.50)"
                    })
                }
                "tail" => {
                    let tail = df.tail(Some(10));
                    serde_json::json!({
                        "operation": "tail",
                        "rows": tail.height(),
                        "columns": tail.width(),
                        "data": "Data preview available (to_json not available in Polars 0.50)"
                    })
                }
                "shape" => {
                    serde_json::json!({
                        "operation": "shape",
                        "rows": df.height(),
                        "columns": df.width()
                    })
                }
                "columns" => {
                    let columns: Vec<String> = df.get_column_names().iter().map(|s| s.to_string()).collect();
                    serde_json::json!({
                        "operation": "columns",
                        "result": columns
                    })
                }
                "dtypes" => {
                    let dtypes: Vec<String> = df.dtypes().iter().map(|dt| format!("{:?}", dt)).collect();
                    serde_json::json!({
                        "operation": "dtypes",
                        "result": dtypes
                    })
                }
                _ => {
                    warn!("Unknown DataFrame operation: {}", operation);
                    continue;
                }
            };
            
            results.push(result);
        }
        
        Ok(serde_json::json!({
            "operations": results,
            "total_rows": df.height(),
            "total_columns": df.width()
        }))
    }
    
    pub fn get_available_operations(&self) -> Vec<String> {
        self.operations.keys().cloned().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_data_processor_creation() {
        let processor = DataProcessor::new().await;
        assert!(!processor.get_available_operations().is_empty());
    }
    
    #[tokio::test]
    async fn test_mean_operation() {
        let processor = DataProcessor::new().await;
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let result = processor.process_data(&data, "mean", None).await.unwrap();
        
        assert_eq!(result["mean"], 3.0);
        assert_eq!(result["count"], 5);
    }
    
    #[tokio::test]
    async fn test_std_operation() {
        let processor = DataProcessor::new().await;
        let data = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let result = processor.process_data(&data, "std", None).await.unwrap();
        
        assert!(result["std"].as_f64().unwrap() > 0.0);
        assert_eq!(result["count"], 5);
    }
}
