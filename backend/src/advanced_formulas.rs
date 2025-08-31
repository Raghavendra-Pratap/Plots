use anyhow::{Result, anyhow};
use polars::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use tracing::info;

// Advanced formula request structures
#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AdvancedFormulaRequest {
    pub formula_type: String,
    pub data: Vec<HashMap<String, Value>>,
    pub parameters: FormulaParameters,
    pub output_config: OutputConfig,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct FormulaParameters {
    pub input_columns: Vec<String>,
    pub criteria_columns: Option<Vec<String>>,
    pub criteria_values: Option<Vec<Value>>,
    pub separator: Option<String>,
    pub aggregation_type: Option<String>,
    pub lookup_table: Option<Vec<HashMap<String, Value>>>,
    pub lookup_key: Option<String>,
    pub return_column: Option<String>,
    pub optional_params: Vec<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct OutputConfig {
    pub output_column: String,
    pub include_metadata: bool,
    pub sample_size: Option<usize>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct FormulaResult {
    pub status: String,
    pub data: Vec<HashMap<String, Value>>,
    pub metadata: HashMap<String, Value>,
    pub processing_time_ms: u64,
    pub formula_type: String,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct FormulaInfo {
    pub name: String,
    pub description: String,
    pub complexity: String,
    pub required_params: Vec<String>,
    pub optional_params: Vec<String>,
    pub examples: Vec<String>,
}

pub struct AdvancedFormulaProcessor {
    supported_formulas: HashMap<String, FormulaInfo>,
}

impl AdvancedFormulaProcessor {
    pub fn new() -> Self {
        let mut processor = AdvancedFormulaProcessor {
            supported_formulas: HashMap::new(),
        };
        
        processor.register_formulas();
        processor
    }
    
    fn register_formulas(&mut self) {
        // SUMIFS - The ultimate business formula
        self.supported_formulas.insert("SUMIFS".to_string(), FormulaInfo {
            name: "SUMIFS".to_string(),
            description: "Sums values based on multiple criteria conditions".to_string(),
            complexity: "Advanced".to_string(),
            required_params: vec!["sum_range".to_string(), "criteria_ranges".to_string(), "criteria_values".to_string()],
            optional_params: vec!["group_by".to_string(), "output_format".to_string()],
            examples: vec![
                "Sum sales where Region = 'North' AND Product = 'Electronics'".to_string(),
                "Sum revenue where Status = 'Completed' AND Date >= '2024-01-01'".to_string(),
                "Sum amounts by Department AND Month".to_string(),
            ],
        });
        
        // PIVOT - Data summarization powerhouse
        self.supported_formulas.insert("PIVOT".to_string(), FormulaInfo {
            name: "PIVOT".to_string(),
            description: "Creates summary tables with aggregations".to_string(),
            complexity: "Advanced".to_string(),
            required_params: vec!["index_columns".to_string(), "value_columns".to_string()],
            optional_params: vec!["aggregation_type".to_string(), "fill_value".to_string(), "sort_by".to_string()],
            examples: vec![
                "Pivot sales by Region and Product with SUM aggregation".to_string(),
                "Pivot revenue by Department and Month with AVERAGE aggregation".to_string(),
                "Pivot counts by Status and Category".to_string(),
            ],
        });
        
        // TEXT_JOIN - Advanced text manipulation
        self.supported_formulas.insert("TEXT_JOIN".to_string(), FormulaInfo {
            name: "TEXT_JOIN".to_string(),
            description: "Combines multiple text columns with custom separators".to_string(),
            complexity: "Intermediate".to_string(),
            required_params: vec!["text_columns".to_string()],
            optional_params: vec!["separator".to_string(), "ignore_empty".to_string(), "case_sensitive".to_string()],
            examples: vec![
                "Join First Name + Last Name with space separator".to_string(),
                "Join Address components with comma separator".to_string(),
                "Join multiple tags with pipe separator".to_string(),
            ],
        });
        
        // VLOOKUP - Data relationship master
        self.supported_formulas.insert("VLOOKUP".to_string(), FormulaInfo {
            name: "VLOOKUP".to_string(),
            description: "Finds values in reference tables based on lookup keys".to_string(),
            complexity: "Advanced".to_string(),
            required_params: vec!["lookup_value".to_string(), "lookup_table".to_string(), "return_column".to_string()],
            optional_params: vec!["match_type".to_string(), "error_handling".to_string(), "default_value".to_string()],
            examples: vec![
                "Find product name using product ID".to_string(),
                "Find customer region using customer ID".to_string(),
                "Find employee department using employee ID".to_string(),
            ],
        });
    }
    
    pub async fn process_advanced_formula(&self, request: AdvancedFormulaRequest) -> Result<FormulaResult> {
        let start_time = std::time::Instant::now();
        let formula_type = request.formula_type.clone();
        
        info!("Processing advanced formula: {} with {} rows", formula_type, request.data.len());
        
        let result = match request.formula_type.to_uppercase().as_str() {
            "SUMIFS" => self.process_sumifs(request).await?,
            "PIVOT" => self.process_pivot(request).await?,
            "TEXT_JOIN" => self.process_text_join(request).await?,
            "VLOOKUP" => self.process_vlookup(request).await?,
            _ => return Err(anyhow!("Unsupported formula type: {}", formula_type)),
        };
        
        let processing_time = start_time.elapsed().as_millis() as u64;
        
        Ok(FormulaResult {
            status: "success".to_string(),
            data: result,
            metadata: HashMap::new(),
            processing_time_ms: processing_time,
            formula_type,
        })
    }
    
    // SUMIFS Implementation - The Ultimate Business Formula
    async fn process_sumifs(&self, request: AdvancedFormulaRequest) -> Result<Vec<HashMap<String, Value>>> {
        let data = request.data;
        if data.is_empty() {
            return Ok(vec![]);
        }
        
        let sum_range_col = request.parameters.input_columns.get(0)
            .ok_or_else(|| anyhow!("SUMIFS requires a sum range column"))?;
        
        let criteria_cols = request.parameters.criteria_columns
            .as_ref()
            .ok_or_else(|| anyhow!("SUMIFS requires criteria columns"))?;
        
        let criteria_vals = request.parameters.criteria_values
            .as_ref()
            .ok_or_else(|| anyhow!("SUMIFS requires criteria values"))?;
        
        if criteria_cols.len() != criteria_vals.len() {
            return Err(anyhow!("Criteria columns and values must have the same length"));
        }
        
        // Convert to Polars DataFrame for high-performance processing
        let _df = self.json_to_dataframe(&data)?;
        
        // Apply SUMIFS logic
        let mut result_data = Vec::new();
        
        // Check if we should group by criteria columns
        let should_group = request.parameters.optional_params.iter().any(|p| p == "group_by");
        
        if should_group {
            // Grouped SUMIFS - simplified implementation
            let mut grouped_results = HashMap::new();
            
            for row in data {
                let mut group_key = String::new();
                for criteria_col in criteria_cols {
                    if let Some(value) = row.get(criteria_col) {
                        group_key.push_str(&value.to_string());
                        group_key.push('|');
                    }
                }
                
                let sum_value = row.get(sum_range_col)
                    .and_then(|v| v.as_f64())
                    .unwrap_or(0.0);
                
                let entry = grouped_results.entry(group_key).or_insert((0.0, 0));
                entry.0 += sum_value;
                entry.1 += 1;
            }
            
            for (group_key, (sum_result, count_result)) in grouped_results {
                let mut result_row = HashMap::new();
                result_row.insert("group_key".to_string(), Value::String(group_key));
                result_row.insert("sum_result".to_string(), Value::Number(serde_json::Number::from_f64(sum_result).unwrap()));
                result_row.insert("count_result".to_string(), Value::Number(serde_json::Number::from_f64(count_result as f64).unwrap()));
                result_data.push(result_row);
            }
        } else {
            // Simple SUMIFS - sum all rows that match criteria
            let mut total_sum = 0.0;
            let mut matching_rows = 0;
            
            for row in data {
                let mut matches_criteria = true;
                
                for (criteria_col, criteria_val) in criteria_cols.iter().zip(criteria_vals.iter()) {
                    let row_value = row.get(criteria_col);
                    let matches = match (row_value, criteria_val) {
                        (Some(Value::String(s1)), Value::String(s2)) => s1 == s2,
                        (Some(Value::Number(n1)), Value::Number(n2)) => n1.as_f64() == n2.as_f64(),
                        (Some(Value::Bool(b1)), Value::Bool(b2)) => b1 == b2,
                        _ => false,
                    };
                    
                    if !matches {
                        matches_criteria = false;
                        break;
                    }
                }
                
                if matches_criteria {
                    if let Some(sum_value) = row.get(sum_range_col).and_then(|v| v.as_f64()) {
                        total_sum += sum_value;
                        matching_rows += 1;
                    }
                }
            }
            
            let mut result_row = HashMap::new();
            result_row.insert("sum_result".to_string(), Value::Number(serde_json::Number::from_f64(total_sum).unwrap()));
            result_row.insert("count_result".to_string(), Value::Number(serde_json::Number::from_f64(matching_rows as f64).unwrap()));
            result_row.insert("criteria_applied".to_string(), Value::String(format!("{} criteria", criteria_cols.len())));
            
            result_data.push(result_row);
        }
        
        Ok(result_data)
    }
    
    // PIVOT Implementation - Data Summarization Powerhouse
    async fn process_pivot(&self, request: AdvancedFormulaRequest) -> Result<Vec<HashMap<String, Value>>> {
        let data = request.data;
        if data.is_empty() {
            return Ok(vec![]);
        }
        
        let index_cols = request.parameters.input_columns.get(0)
            .ok_or_else(|| anyhow!("PIVOT requires index columns"))?;
        
        let value_cols = request.parameters.input_columns.get(1)
            .ok_or_else(|| anyhow!("PIVOT requires value columns"))?;
        
        let agg_type = request.parameters.aggregation_type.as_deref().unwrap_or("sum");
        
        // Parse index columns (can be multiple)
        let index_col_names: Vec<&str> = index_cols.split(',').map(|s| s.trim()).collect();
        
        // Parse value columns (can be multiple)
        let value_col_names: Vec<&str> = value_cols.split(',').map(|s| s.trim()).collect();
        
        // Create pivot table using HashMap for grouping
        let mut pivot_groups: HashMap<String, HashMap<String, Vec<f64>>> = HashMap::new();
        
        for row in data {
            // Create group key from index columns
            let mut group_key = String::new();
            for index_col in &index_col_names {
                if let Some(value) = row.get(*index_col) {
                    group_key.push_str(&value.to_string());
                    group_key.push('|');
                }
            }
            
            // Get values from value columns
            for value_col in &value_col_names {
                if let Some(value) = row.get(*value_col).and_then(|v| v.as_f64()) {
                    let group = pivot_groups.entry(group_key.clone()).or_insert_with(HashMap::new);
                    let values = group.entry(value_col.to_string()).or_insert_with(Vec::new);
                    values.push(value);
                }
            }
        }
        
        // Convert grouped data to result format
        let mut pivot_result = Vec::new();
        for (group_key, value_map) in pivot_groups {
            let mut result_row = HashMap::new();
            
            // Add index columns
            let index_parts: Vec<&str> = group_key.split('|').filter(|s| !s.is_empty()).collect();
            for (i, index_col) in index_col_names.iter().enumerate() {
                if i < index_parts.len() {
                    result_row.insert(index_col.to_string(), Value::String(index_parts[i].to_string()));
                }
            }
            
            // Add aggregated values
            for (value_col, values) in value_map {
                let aggregated_value = match agg_type {
                    "sum" => values.iter().sum(),
                    "mean" | "average" => values.iter().sum::<f64>() / values.len() as f64,
                    "count" => values.len() as f64,
                    "min" => values.iter().fold(f64::INFINITY, |a, &b| a.min(b)),
                    "max" => values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b)),
                    _ => values.iter().sum(), // Default to sum
                };
                
                result_row.insert(format!("{}_{}", value_col, agg_type), Value::Number(serde_json::Number::from_f64(aggregated_value).unwrap()));
            }
            
            pivot_result.push(result_row);
        }
        
        Ok(pivot_result)
    }
    
    // TEXT_JOIN Implementation - Advanced Text Manipulation
    async fn process_text_join(&self, request: AdvancedFormulaRequest) -> Result<Vec<HashMap<String, Value>>> {
        let data = request.data;
        if data.is_empty() {
            return Ok(vec![]);
        }
        
        let text_cols = &request.parameters.input_columns;
        let separator = request.parameters.separator.as_deref().unwrap_or(" ");
        let ignore_empty = request.parameters.optional_params.iter().any(|p| p == "ignore_empty");
        
        let mut result_data = Vec::new();
        
        for row in data {
            let mut text_parts = Vec::new();
            
            for col_name in text_cols {
                if let Some(value) = row.get(col_name) {
                    let text_value = match value {
                        Value::String(s) => s.clone(),
                        Value::Number(n) => n.to_string(),
                        Value::Bool(b) => b.to_string(),
                        _ => value.to_string(),
                    };
                    
                    if !ignore_empty || !text_value.is_empty() {
                        text_parts.push(text_value);
                    }
                }
            }
            
            let joined_text = text_parts.join(separator);
            
            let mut result_row = row.clone();
            result_row.insert(request.output_config.output_column.clone(), Value::String(joined_text));
            result_data.push(result_row);
        }
        
        Ok(result_data)
    }
    
    // VLOOKUP Implementation - Data Relationship Master
    async fn process_vlookup(&self, request: AdvancedFormulaRequest) -> Result<Vec<HashMap<String, Value>>> {
        let data = request.data;
        if data.is_empty() {
            return Ok(vec![]);
        }
        
        let lookup_table = request.parameters.lookup_table
            .as_ref()
            .ok_or_else(|| anyhow!("VLOOKUP requires a lookup table"))?;
        
        let lookup_key = request.parameters.lookup_key
            .as_ref()
            .ok_or_else(|| anyhow!("VLOOKUP requires a lookup key column"))?;
        
        let return_col = request.parameters.return_column
            .as_ref()
            .ok_or_else(|| anyhow!("VLOOKUP requires a return column"))?;
        
        // Convert lookup table to HashMap for fast lookups
        let mut lookup_map = HashMap::new();
        for row in lookup_table {
            if let Some(key_value) = row.get(lookup_key) {
                if let Some(return_value) = row.get(return_col) {
                    lookup_map.insert(key_value.clone(), return_value.clone());
                }
            }
        }
        
        let mut result_data = Vec::new();
        
        for row in data {
            let mut result_row = row.clone();
            
            // Find the lookup value in the current row
            let lookup_value = request.parameters.input_columns.iter().find_map(|col_name| {
                row.get(col_name).cloned()
            });
            
            if let Some(lookup_val) = lookup_value {
                if let Some(found_value) = lookup_map.get(&lookup_val) {
                    result_row.insert(request.output_config.output_column.clone(), found_value.clone());
                } else {
                    // Handle missing lookup - insert default or error value
                    let default_value = request.parameters.optional_params.iter()
                        .find(|p| p.starts_with("default_value:"))
                        .map(|p| p.split(':').nth(1).unwrap_or("Not Found"))
                        .unwrap_or("Not Found");
                    
                    result_row.insert(request.output_config.output_column.clone(), Value::String(default_value.to_string()));
                }
            }
            
            result_data.push(result_row);
        }
        
        Ok(result_data)
    }
    
    // Helper functions
    fn json_to_dataframe(&self, _data: &[HashMap<String, Value>]) -> Result<DataFrame> {
        // Simplified implementation - return empty DataFrame for now
        // This can be enhanced later with proper Polars DataFrame creation
        let empty_series = vec![Series::new("placeholder".into(), vec![0i32])];
        Ok(DataFrame::new(empty_series.into_iter().map(|s| s.into()).collect())?)
    }
    
    fn dataframe_to_json(&self, _df: &DataFrame) -> Result<Vec<HashMap<String, Value>>> {
        // Simplified implementation - return empty result for now
        Ok(vec![])
    }
    
    // Public API methods
    pub fn get_supported_formulas(&self) -> &HashMap<String, FormulaInfo> {
        &self.supported_formulas
    }
    
    pub fn get_formula_info(&self, formula_name: &str) -> Option<&FormulaInfo> {
        self.supported_formulas.get(&formula_name.to_uppercase())
    }
    
    pub fn validate_formula_request(&self, request: &AdvancedFormulaRequest) -> Result<()> {
        let formula_name = request.formula_type.to_uppercase();
        
        let formula_info = match self.supported_formulas.get(&formula_name) {
            Some(info) => info,
            None => return Err(anyhow!("Unsupported formula: {}", request.formula_type)),
        };
        
        // Basic validation - ensure we have input columns
        if request.parameters.input_columns.is_empty() {
            return Err(anyhow!("At least one input column is required"));
        }
        
        // Formula-specific validation
        match formula_name.as_str() {
            "SUMIFS" => {
                if request.parameters.criteria_columns.is_none() || request.parameters.criteria_values.is_none() {
                    return Err(anyhow!("SUMIFS requires criteria_columns and criteria_values"));
                }
                if request.parameters.criteria_columns.as_ref().unwrap().len() != request.parameters.criteria_values.as_ref().unwrap().len() {
                    return Err(anyhow!("Criteria columns and values must have the same length"));
                }
            },
            "PIVOT" => {
                if request.parameters.input_columns.len() < 2 {
                    return Err(anyhow!("PIVOT requires at least 2 input columns (index and value columns)"));
                }
            },
            "TEXT_JOIN" => {
                if request.parameters.input_columns.len() < 1 {
                    return Err(anyhow!("TEXT_JOIN requires at least one text column"));
                }
            },
            "VLOOKUP" => {
                if request.parameters.lookup_table.is_none() || request.parameters.lookup_key.is_none() || request.parameters.return_column.is_none() {
                    return Err(anyhow!("VLOOKUP requires lookup_table, lookup_key, and return_column"));
                }
            },
            _ => {}
        }
        
        Ok(())
    }
}
