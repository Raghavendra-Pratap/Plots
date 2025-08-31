use anyhow::{Result, anyhow};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::{HashMap, HashSet, VecDeque};
use tokio::sync::Mutex;
use tracing::{info, warn, error};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowStep {
    pub id: String,
    pub operation: String,
    pub dependencies: Vec<String>,
    pub data: Value,
    pub parameters: Option<Value>,
    pub timeout_ms: Option<u64>,
    pub retry_count: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowExecution {
    pub id: String,
    pub name: String,
    pub steps: Vec<WorkflowStep>,
    pub status: WorkflowStatus,
    pub current_step: Option<String>,
    pub results: HashMap<String, Value>,
    pub errors: HashMap<String, String>,
    pub start_time: chrono::DateTime<chrono::Utc>,
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    pub total_duration_ms: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum WorkflowStatus {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowResult {
    pub workflow_id: String,
    pub status: WorkflowStatus,
    pub results: HashMap<String, Value>,
    pub errors: HashMap<String, String>,
    pub execution_time_ms: u64,
    pub step_count: usize,
    pub successful_steps: usize,
    pub failed_steps: usize,
}

pub struct WorkflowEngine {
    workflows: Mutex<HashMap<String, WorkflowExecution>>,
    step_processors: HashMap<String, Box<dyn Fn(&Value, Option<&Value>) -> Result<Value> + Send + Sync>>,
}

impl WorkflowEngine {
    pub async fn new() -> Self {
        let mut engine = WorkflowEngine {
            workflows: Mutex::new(HashMap::new()),
            step_processors: HashMap::new(),
        };
        
        // Register built-in step processors
        engine.register_step_processors();
        
        info!("Workflow engine initialized with {} step processors", engine.step_processors.len());
        engine
    }
    
    fn register_step_processors(&mut self) {
        // Data processing steps
        self.step_processors.insert("data_transform".to_string(), Box::new(|data, params| {
            let operation = params.and_then(|p| p.get("operation"))
                .and_then(|p| p.as_str())
                .ok_or_else(|| anyhow!("Data transform requires 'operation' parameter"))?;
            
            match operation {
                "filter" => {
                    let threshold = params.and_then(|p| p.get("threshold"))
                        .and_then(|p| p.as_f64())
                        .unwrap_or(0.0);
                    
                    let data_array = data.as_array()
                        .ok_or_else(|| anyhow!("Data must be an array"))?;
                    
                    let filtered: Vec<Value> = data_array.iter()
                        .filter(|&v| v.as_f64().unwrap_or(0.0) > threshold)
                        .cloned()
                        .collect();
                    
                    Ok(serde_json::json!({
                        "filtered_data": filtered,
                        "original_count": data_array.len(),
                        "filtered_count": filtered.len(),
                        "threshold": threshold
                    }))
                }
                "sort" => {
                    let order = params.and_then(|p| p.get("order"))
                        .and_then(|p| p.as_str())
                        .unwrap_or("asc");
                    
                    let data_array = data.as_array()
                        .ok_or_else(|| anyhow!("Data must be an array"))?;
                    
                    let mut sorted_data = data_array.clone();
                    sorted_data.sort_by(|a, b| {
                        let a_val = a.as_f64().unwrap_or(0.0);
                        let b_val = b.as_f64().unwrap_or(0.0);
                        if order == "desc" {
                            b_val.partial_cmp(&a_val).unwrap()
                        } else {
                            a_val.partial_cmp(&b_val).unwrap()
                        }
                    });
                    
                    Ok(serde_json::json!({
                        "sorted_data": sorted_data,
                        "order": order,
                        "count": sorted_data.len()
                    }))
                }
                "aggregate" => {
                    let function = params.and_then(|p| p.get("function"))
                        .and_then(|p| p.as_str())
                        .ok_or_else(|| anyhow!("Aggregate requires 'function' parameter"))?;
                    
                    let data_array = data.as_array()
                        .ok_or_else(|| anyhow!("Data must be an array"))?;
                    
                    let result = match function {
                        "sum" => {
                            let sum: f64 = data_array.iter()
                                .filter_map(|v| v.as_f64())
                                .sum();
                            serde_json::json!({ "sum": sum })
                        }
                        "average" => {
                            let values: Vec<f64> = data_array.iter()
                                .filter_map(|v| v.as_f64())
                                .collect();
                            let avg = if values.is_empty() { 0.0 } else { values.iter().sum::<f64>() / values.len() as f64 };
                            serde_json::json!({ "average": avg, "count": values.len() })
                        }
                        "count" => {
                            let count = data_array.len();
                            serde_json::json!({ "count": count })
                        }
                        _ => return Err(anyhow!("Unknown aggregate function: {}", function))
                    };
                    
                    Ok(result)
                }
                _ => Err(anyhow!("Unknown data transform operation: {}", operation))
            }
        }));
        
        // File operations
        self.step_processors.insert("file_operation".to_string(), Box::new(|_data, params| {
            let operation = params.and_then(|p| p.get("operation"))
                .and_then(|p| p.as_str())
                .ok_or_else(|| anyhow!("File operation requires 'operation' parameter"))?;
            
            match operation {
                "read_csv" => {
                    let file_path = params.and_then(|p| p.get("file_path"))
                        .and_then(|p| p.as_str())
                        .ok_or_else(|| anyhow!("File operation requires 'file_path' parameter"))?;
                    
                    // Simulate CSV reading
                    Ok(serde_json::json!({
                        "operation": "read_csv",
                        "file_path": file_path,
                        "status": "success",
                        "message": "CSV file read successfully (simulated)"
                    }))
                }
                "write_json" => {
                    let file_path = params.and_then(|p| p.get("file_path"))
                        .and_then(|p| p.as_str())
                        .ok_or_else(|| anyhow!("File operation requires 'file_path' parameter"))?;
                    
                    Ok(serde_json::json!({
                        "operation": "write_json",
                        "file_path": file_path,
                        "status": "success",
                        "message": "JSON file written successfully (simulated)"
                    }))
                }
                _ => Err(anyhow!("Unknown file operation: {}", operation))
            }
        }));
        
        // Conditional steps
        self.step_processors.insert("conditional".to_string(), Box::new(|data, params| {
            let condition = params.and_then(|p| p.get("condition"))
                .and_then(|p| p.as_str())
                .ok_or_else(|| anyhow!("Conditional requires 'condition' parameter"))?;
            
            let value = data.as_f64().unwrap_or(0.0);
            let threshold = params.and_then(|p| p.get("threshold"))
                .and_then(|p| p.as_f64())
                .unwrap_or(0.0);
            
            let result = match condition {
                "greater_than" => value > threshold,
                "less_than" => value < threshold,
                "equals" => (value - threshold).abs() < f64::EPSILON,
                "not_equals" => (value - threshold).abs() >= f64::EPSILON,
                _ => return Err(anyhow!("Unknown condition: {}", condition))
            };
            
            Ok(serde_json::json!({
                "condition": condition,
                "value": value,
                "threshold": threshold,
                "result": result
            }))
        }));
        
        // Delay steps
        self.step_processors.insert("delay".to_string(), Box::new(|_data, params| {
            let duration_ms = params.and_then(|p| p.get("duration_ms"))
                .and_then(|p| p.as_u64())
                .unwrap_or(1000);
            
            // In a real implementation, this would actually delay
            Ok(serde_json::json!({
                "operation": "delay",
                "duration_ms": duration_ms,
                "status": "completed"
            }))
        }));
    }
    
    pub async fn execute_workflow(
        &self,
        name: &str,
        steps: &[WorkflowStep],
        _parameters: Option<&Value>,
    ) -> Result<(String, Value)> {
        let workflow_id = Uuid::new_v4().to_string();
        info!("Starting workflow execution: {} (ID: {})", name, workflow_id);
        
        // Validate workflow
        self.validate_workflow(steps)?;
        
        // Create workflow execution
        let mut execution = WorkflowExecution {
            id: workflow_id.clone(),
            name: name.to_string(),
            steps: steps.to_vec(),
            status: WorkflowStatus::Running,
            current_step: None,
            results: HashMap::new(),
            errors: HashMap::new(),
            start_time: chrono::Utc::now(),
            end_time: None,
            total_duration_ms: None,
        };
        
        // Store workflow
        {
            let mut workflows = self.workflows.lock().await;
            workflows.insert(workflow_id.clone(), execution.clone());
        }
        
        // Execute workflow
        let _result = self.execute_workflow_steps(&mut execution).await;
        
        // Update final status
        execution.status = if execution.errors.is_empty() {
            WorkflowStatus::Completed
        } else {
            WorkflowStatus::Failed
        };
        execution.end_time = Some(chrono::Utc::now());
        execution.total_duration_ms = Some(
            (execution.end_time.unwrap() - execution.start_time).num_milliseconds() as u64
        );
        
        // Update stored workflow
        {
            let mut workflows = self.workflows.lock().await;
            workflows.insert(workflow_id.clone(), execution.clone());
        }
        
        // Create result
        let workflow_result = WorkflowResult {
            workflow_id: workflow_id.clone(),
            status: execution.status.clone(),
            results: execution.results.clone(),
            errors: execution.errors.clone(),
            execution_time_ms: execution.total_duration_ms.unwrap_or(0),
            step_count: execution.steps.len(),
            successful_steps: execution.results.len(),
            failed_steps: execution.errors.len(),
        };
        
        info!("Workflow execution completed: {} (ID: {})", name, workflow_id);
        
        Ok((workflow_id, serde_json::to_value(workflow_result)?))
    }
    
    fn validate_workflow(&self, steps: &[WorkflowStep]) -> Result<()> {
        if steps.is_empty() {
            return Err(anyhow!("Workflow must have at least one step"));
        }
        
        // Check for circular dependencies
        let mut visited = HashSet::new();
        let mut rec_stack = HashSet::new();
        
        for step in steps {
            if self.has_cycle(step.id.clone(), steps, &mut visited, &mut rec_stack) {
                return Err(anyhow!("Circular dependency detected in workflow"));
            }
        }
        
        // Check that all dependencies exist
        let step_ids: HashSet<String> = steps.iter().map(|s| s.id.clone()).collect();
        for step in steps {
            for dep in &step.dependencies {
                if !step_ids.contains(dep) {
                    return Err(anyhow!("Step '{}' depends on non-existent step '{}'", step.id, dep));
                }
            }
        }
        
        Ok(())
    }
    
    fn has_cycle(
        &self,
        step_id: String,
        steps: &[WorkflowStep],
        visited: &mut HashSet<String>,
        rec_stack: &mut HashSet<String>,
    ) -> bool {
        if rec_stack.contains(&step_id) {
            return true;
        }
        
        if visited.contains(&step_id) {
            return false;
        }
        
        visited.insert(step_id.clone());
        rec_stack.insert(step_id.clone());
        
        let step = steps.iter().find(|s| s.id == step_id).unwrap();
        for dep in &step.dependencies {
            if self.has_cycle(dep.clone(), steps, visited, rec_stack) {
                return true;
            }
        }
        
        rec_stack.remove(&step_id);
        false
    }
    
    async fn execute_workflow_steps(&self, execution: &mut WorkflowExecution) -> Result<()> {
        let execution_order = self.topological_sort(&execution.steps)?;
        
        for step_id in execution_order {
            let step = execution.steps.iter().find(|s| s.id == step_id).unwrap();
            execution.current_step = Some(step_id.clone());
            
            info!("Executing workflow step: {} ({})", step.operation, step.id);
            
            match self.execute_step(step, &execution.results).await {
                Ok(result) => {
                    execution.results.insert(step_id.clone(), result);
                    info!("Step {} completed successfully", step.id);
                }
                Err(e) => {
                    let error_msg = format!("Step execution failed: {}", e);
                    execution.errors.insert(step_id.clone(), error_msg.clone());
                    error!("Step {} failed: {}", step.id, e);
                    
                    // Check if we should continue or fail fast
                    if step.retry_count.unwrap_or(0) > 0 {
                        warn!("Retrying step {} (retries remaining: {})", step.id, step.retry_count.unwrap());
                        // In a real implementation, this would retry the step
                    }
                }
            }
        }
        
        Ok(())
    }
    
    fn topological_sort(&self, steps: &[WorkflowStep]) -> Result<Vec<String>> {
        let mut in_degree: HashMap<String, usize> = HashMap::new();
        let mut graph: HashMap<String, Vec<String>> = HashMap::new();
        
        // Initialize
        for step in steps {
            in_degree.insert(step.id.clone(), 0);
            graph.insert(step.id.clone(), Vec::new());
        }
        
        // Build graph and calculate in-degrees
        for step in steps {
            for dep in &step.dependencies {
                if let Some(adj_list) = graph.get_mut(dep) {
                    adj_list.push(step.id.clone());
                }
                if let Some(degree) = in_degree.get_mut(&step.id) {
                    *degree += 1;
                }
            }
        }
        
        // Topological sort using Kahn's algorithm
        let mut queue: VecDeque<String> = VecDeque::new();
        let mut result: Vec<String> = Vec::new();
        
        // Add nodes with no dependencies
        for (step_id, &degree) in &in_degree {
            if degree == 0 {
                queue.push_back(step_id.clone());
            }
        }
        
        while let Some(current) = queue.pop_front() {
            result.push(current.clone());
            
            if let Some(adj_list) = graph.get(&current) {
                for neighbor in adj_list {
                    if let Some(degree) = in_degree.get_mut(neighbor) {
                        *degree -= 1;
                        if *degree == 0 {
                            queue.push_back(neighbor.clone());
                        }
                    }
                }
            }
        }
        
        if result.len() != steps.len() {
            return Err(anyhow!("Circular dependency detected in workflow"));
        }
        
        Ok(result)
    }
    
    async fn execute_step(
        &self,
        step: &WorkflowStep,
        previous_results: &HashMap<String, Value>,
    ) -> Result<Value> {
        // Get input data (either from step data or previous results)
        let input_data = if step.dependencies.is_empty() {
            step.data.clone()
        } else {
            // Combine data from dependencies
            let mut combined_data = Vec::new();
            for dep in &step.dependencies {
                if let Some(result) = previous_results.get(dep) {
                    combined_data.push(result.clone());
                }
            }
            serde_json::json!(combined_data)
        };
        
        // Get step processor
        let processor = self.step_processors.get(&step.operation)
            .ok_or_else(|| anyhow!("Unknown step operation: {}", step.operation))?;
        
        // Execute step
        let result = processor(&input_data, step.parameters.as_ref())?;
        
        Ok(result)
    }
    
    pub async fn get_workflow_status(&self, workflow_id: &str) -> Option<WorkflowExecution> {
        let workflows = self.workflows.lock().await;
        workflows.get(workflow_id).cloned()
    }
    
    pub async fn cancel_workflow(&self, workflow_id: &str) -> Result<()> {
        let mut workflows = self.workflows.lock().await;
        if let Some(execution) = workflows.get_mut(workflow_id) {
            execution.status = WorkflowStatus::Cancelled;
            execution.end_time = Some(chrono::Utc::now());
            info!("Workflow {} cancelled", workflow_id);
            Ok(())
        } else {
            Err(anyhow!("Workflow {} not found", workflow_id))
        }
    }
    
    pub fn get_available_operations(&self) -> Vec<String> {
        self.step_processors.keys().cloned().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_workflow_engine_creation() {
        let engine = WorkflowEngine::new().await;
        assert!(!engine.get_available_operations().is_empty());
    }
    
    #[tokio::test]
    async fn test_simple_workflow() {
        let engine = WorkflowEngine::new().await;
        
        let steps = vec![
            WorkflowStep {
                id: "step1".to_string(),
                operation: "data_transform".to_string(),
                dependencies: vec![],
                data: serde_json::json!([1.0, 2.0, 3.0, 4.0, 5.0]),
                parameters: Some(serde_json::json!({
                    "operation": "sum"
                })),
                timeout_ms: None,
                retry_count: None,
            }
        ];
        
        let (workflow_id, result) = engine.execute_workflow("test_workflow", &steps, None).await.unwrap();
        
        assert!(!workflow_id.is_empty());
        assert_eq!(result["status"], "completed");
    }
}
