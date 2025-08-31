use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

// Common response structures
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
    pub message: Option<String>,
    pub timestamp: String,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            message: Some("Operation completed successfully".to_string()),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }
    
    pub fn error(error: String) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(error),
            message: None,
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }
    
    pub fn message(message: String) -> Self {
        Self {
            success: true,
            data: None,
            error: None,
            message: Some(message),
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }
}

// Data processing models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataProcessingRequest {
    pub operation: String,
    pub data: Vec<f64>,
    pub parameters: Option<HashMap<String, Value>>,
    pub metadata: Option<HashMap<String, Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataProcessingResult {
    pub operation: String,
    pub input_size: usize,
    pub output_size: usize,
    pub result: Value,
    pub processing_time_ms: u64,
    pub memory_usage_mb: f64,
    pub metadata: Option<HashMap<String, Value>>,
}

// Workflow models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowDefinition {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub version: String,
    pub steps: Vec<WorkflowStepDefinition>,
    pub parameters: Option<HashMap<String, Value>>,
    pub metadata: Option<HashMap<String, Value>>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowStepDefinition {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub operation: String,
    pub dependencies: Vec<String>,
    pub parameters: Option<HashMap<String, Value>>,
    pub timeout_ms: Option<u64>,
    pub retry_count: Option<u32>,
    pub retry_delay_ms: Option<u64>,
    pub error_handling: Option<ErrorHandlingStrategy>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ErrorHandlingStrategy {
    Continue,
    Stop,
    Retry,
    Rollback,
}

// Data source models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataSource {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub source_type: DataSourceType,
    pub connection_config: ConnectionConfig,
    pub schema: Option<DataSourceSchema>,
    pub metadata: Option<HashMap<String, Value>>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DataSourceType {
    Csv,
    Json,
    Parquet,
    Database,
    Api,
    Stream,
    Custom,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConnectionConfig {
    pub connection_string: Option<String>,
    pub host: Option<String>,
    pub port: Option<u16>,
    pub database: Option<String>,
    pub username: Option<String>,
    pub password: Option<String>,
    pub ssl_mode: Option<String>,
    pub timeout_ms: Option<u64>,
    pub max_connections: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataSourceSchema {
    pub columns: Vec<ColumnDefinition>,
    pub primary_key: Option<Vec<String>>,
    pub indexes: Option<Vec<IndexDefinition>>,
    pub constraints: Option<Vec<ConstraintDefinition>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ColumnDefinition {
    pub name: String,
    pub data_type: String,
    pub nullable: bool,
    pub default_value: Option<Value>,
    pub description: Option<String>,
    pub constraints: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IndexDefinition {
    pub name: String,
    pub columns: Vec<String>,
    pub unique: bool,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConstraintDefinition {
    pub name: String,
    pub constraint_type: String,
    pub columns: Vec<String>,
    pub expression: Option<String>,
    pub description: Option<String>,
}

// Query models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryRequest {
    pub query: String,
    pub parameters: Option<Vec<Value>>,
    pub timeout_ms: Option<u64>,
    pub max_rows: Option<usize>,
    pub metadata: Option<HashMap<String, Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QueryResult {
    pub columns: Vec<String>,
    pub rows: Vec<Vec<Value>>,
    pub row_count: usize,
    pub execution_time_ms: u64,
    pub metadata: Option<HashMap<String, Value>>,
}

// Visualization models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChartRequest {
    pub chart_type: ChartType,
    pub data: Value,
    pub options: Option<ChartOptions>,
    pub metadata: Option<HashMap<String, Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ChartType {
    Line,
    Bar,
    Scatter,
    Pie,
    Histogram,
    Heatmap,
    BoxPlot,
    Custom,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChartOptions {
    pub title: Option<String>,
    pub x_label: Option<String>,
    pub y_label: Option<String>,
    pub colors: Option<Vec<String>>,
    pub width: Option<u32>,
    pub height: Option<u32>,
    pub interactive: Option<bool>,
    pub animation: Option<bool>,
}

// Performance metrics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub operation: String,
    pub execution_time_ms: u64,
    pub memory_usage_mb: f64,
    pub cpu_usage_percent: f64,
    pub io_operations: u64,
    pub network_requests: u64,
    pub timestamp: String,
}

// System status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemStatus {
    pub status: String,
    pub version: String,
    pub uptime_seconds: u64,
    pub memory_usage_mb: f64,
    pub cpu_usage_percent: f64,
    pub active_connections: u32,
    pub active_workflows: u32,
    pub database_status: String,
    pub timestamp: String,
}

// Error models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ErrorDetails {
    pub error_code: String,
    pub error_type: String,
    pub message: String,
    pub details: Option<Value>,
    pub stack_trace: Option<String>,
    pub timestamp: String,
}

// Configuration models
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub logging: LoggingConfig,
    pub security: SecurityConfig,
    pub performance: PerformanceConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub workers: u32,
    pub max_connections: u32,
    pub timeout_seconds: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub timeout_seconds: u64,
    pub pool_size: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoggingConfig {
    pub level: String,
    pub format: String,
    pub output: String,
    pub max_files: u32,
    pub max_size_mb: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub cors_origins: Vec<String>,
    pub api_key_required: bool,
    pub rate_limit_requests: u32,
    pub rate_limit_window_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceConfig {
    pub max_workflow_steps: u32,
    pub max_data_size_mb: u64,
    pub cache_size_mb: u64,
    pub cleanup_interval_hours: u32,
}

// Utility functions
impl<T> Default for ApiResponse<T> {
    fn default() -> Self {
        Self {
            success: false,
            data: None,
            error: None,
            message: None,
            timestamp: chrono::Utc::now().to_rfc3339(),
        }
    }
}

// Conversion traits
impl<T> From<Result<T, String>> for ApiResponse<T> {
    fn from(result: Result<T, String>) -> Self {
        match result {
            Ok(data) => ApiResponse::success(data),
            Err(error) => ApiResponse::error(error),
        }
    }
}

impl<T> From<Result<T, anyhow::Error>> for ApiResponse<T> {
    fn from(result: Result<T, anyhow::Error>) -> Self {
        match result {
            Ok(data) => ApiResponse::success(data),
            Err(error) => ApiResponse::error(error.to_string()),
        }
    }
}

// Validation traits
pub trait Validatable {
    fn validate(&self) -> Result<(), String>;
}

impl Validatable for DataProcessingRequest {
    fn validate(&self) -> Result<(), String> {
        if self.operation.is_empty() {
            return Err("Operation cannot be empty".to_string());
        }
        if self.data.is_empty() {
            return Err("Data cannot be empty".to_string());
        }
        Ok(())
    }
}

impl Validatable for WorkflowDefinition {
    fn validate(&self) -> Result<(), String> {
        if self.name.is_empty() {
            return Err("Workflow name cannot be empty".to_string());
        }
        if self.steps.is_empty() {
            return Err("Workflow must have at least one step".to_string());
        }
        
        // Check for duplicate step IDs
        let mut step_ids = std::collections::HashSet::new();
        for step in &self.steps {
            if !step_ids.insert(&step.id) {
                return Err(format!("Duplicate step ID: {}", step.id));
            }
        }
        
        Ok(())
    }
}

impl Validatable for DataSource {
    fn validate(&self) -> Result<(), String> {
        if self.name.is_empty() {
            return Err("Data source name cannot be empty".to_string());
        }
        
        match &self.source_type {
            DataSourceType::Database => {
                if self.connection_config.connection_string.is_none() {
                    return Err("Database connection string is required".to_string());
                }
            }
            DataSourceType::Api => {
                if self.connection_config.host.is_none() {
                    return Err("API host is required".to_string());
                }
            }
            _ => {}
        }
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_api_response_success() {
        let response = ApiResponse::success("test data");
        assert!(response.success);
        assert_eq!(response.data, Some("test data"));
        assert!(response.error.is_none());
    }
    
    #[test]
    fn test_api_response_error() {
        let response = ApiResponse::<String>::error("test error".to_string());
        assert!(!response.success);
        assert!(response.data.is_none());
        assert_eq!(response.error, Some("test error".to_string()));
    }
    
    #[test]
    fn test_data_processing_request_validation() {
        let valid_request = DataProcessingRequest {
            operation: "mean".to_string(),
            data: vec![1.0, 2.0, 3.0],
            parameters: None,
            metadata: None,
        };
        assert!(valid_request.validate().is_ok());
        
        let invalid_request = DataProcessingRequest {
            operation: "".to_string(),
            data: vec![1.0, 2.0, 3.0],
            parameters: None,
            metadata: None,
        };
        assert!(invalid_request.validate().is_err());
    }
    
    #[test]
    fn test_workflow_definition_validation() {
        let valid_workflow = WorkflowDefinition {
            id: "test".to_string(),
            name: "Test Workflow".to_string(),
            description: None,
            version: "1.0".to_string(),
            steps: vec![
                WorkflowStepDefinition {
                    id: "step1".to_string(),
                    name: "Step 1".to_string(),
                    description: None,
                    operation: "test".to_string(),
                    dependencies: vec![],
                    parameters: None,
                    timeout_ms: None,
                    retry_count: None,
                    retry_delay_ms: None,
                    error_handling: None,
                }
            ],
            parameters: None,
            metadata: None,
            created_at: "2023-01-01T00:00:00Z".to_string(),
            updated_at: "2023-01-01T00:00:00Z".to_string(),
        };
        assert!(valid_workflow.validate().is_ok());
        
        let invalid_workflow = WorkflowDefinition {
            id: "test".to_string(),
            name: "".to_string(),
            description: None,
            version: "1.0".to_string(),
            steps: vec![],
            parameters: None,
            metadata: None,
            created_at: "2023-01-01T00:00:00Z".to_string(),
            updated_at: "2023-01-01T00:00:00Z".to_string(),
        };
        assert!(invalid_workflow.validate().is_err());
    }
}
