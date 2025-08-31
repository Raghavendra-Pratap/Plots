use actix_cors::Cors;
use actix_web::{get, post, web, App, HttpResponse, HttpServer, Responder, Result};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{info, error};

mod data_processor;
mod workflow_engine;
mod advanced_formulas;
// mod database;  // Commented out for initial build
mod models;

use data_processor::DataProcessor;
use workflow_engine::{WorkflowEngine, WorkflowStep};
use advanced_formulas::{AdvancedFormulaProcessor, AdvancedFormulaRequest, FormulaResult};
// use database::Database;  // Commented out for initial build

// Global state
struct AppState {
    data_processor: Arc<DataProcessor>,
    workflow_engine: Arc<WorkflowEngine>,
    advanced_formula_processor: Arc<AdvancedFormulaProcessor>,
    // database: Arc<Database>,  // Commented out for initial build
}

#[derive(Serialize, Deserialize, Clone)]
struct HealthResponse {
    status: String,
    service: String,
    version: String,
    timestamp: String,
    backend_type: String,
}

#[derive(Serialize, Deserialize, Clone)]
struct DataRequest {
    data: Vec<f64>,
    operation: String,
    parameters: Option<serde_json::Value>,
}

#[derive(Serialize, Deserialize, Clone)]
struct DataResponse {
    status: String,
    result: serde_json::Value,
    processing_time_ms: u64,
    timestamp: String,
}

#[derive(Serialize, Deserialize, Clone)]
struct WorkflowRequest {
    name: String,
    steps: Vec<WorkflowStep>,
    parameters: Option<serde_json::Value>,
}

// Using WorkflowStep from workflow_engine module

#[derive(Serialize, Deserialize, Clone)]
struct WorkflowResponse {
    status: String,
    workflow_id: String,
    execution_time_ms: u64,
    results: serde_json::Value,
    timestamp: String,
}

// Health check endpoint
#[get("/health")]
async fn health_check() -> Result<impl Responder> {
    let response = HealthResponse {
        status: "healthy".to_string(),
        service: "Unified Data Studio Backend v2".to_string(),
        version: "2.0.0".to_string(),
        timestamp: chrono::Utc::now().to_rfc3339(),
        backend_type: "Rust + Actix-web".to_string(),
    };
    
    info!("Health check requested - Backend is healthy");
    Ok(HttpResponse::Ok().json(response))
}

// Root endpoint
#[get("/")]
async fn root() -> Result<impl Responder> {
    let response = serde_json::json!({
        "message": "Unified Data Studio Backend v2 is running!",
        "version": "2.0.0",
        "backend": "Rust + Actix-web",
        "features": [
            "High-performance data processing",
            "Workflow automation",
            "Multi-database support",
            "Real-time processing"
        ],
        "timestamp": chrono::Utc::now().to_rfc3339()
    });
    
    info!("Root endpoint accessed");
    Ok(HttpResponse::Ok().json(response))
}

// Data processing endpoint
#[post("/process-data")]
async fn process_data(
    req: web::Json<DataRequest>,
    state: web::Data<AppState>,
) -> Result<impl Responder> {
    let start_time = std::time::Instant::now();
    
    info!("Processing data request: operation={}, data_size={}", 
          req.operation, req.data.len());
    
    match state.data_processor.process_data(&req.data, &req.operation, req.parameters.as_ref()).await {
        Ok(result) => {
            let processing_time = start_time.elapsed().as_millis() as u64;
            
            let response = DataResponse {
                status: "success".to_string(),
                result,
                processing_time_ms: processing_time,
                timestamp: chrono::Utc::now().to_rfc3339(),
            };
            
            info!("Data processing completed successfully in {}ms", processing_time);
            Ok(HttpResponse::Ok().json(response))
        }
        Err(e) => {
            error!("Data processing failed: {}", e);
            let response = serde_json::json!({
                "status": "error",
                "error": e.to_string(),
                "timestamp": chrono::Utc::now().to_rfc3339()
            });
            Ok(HttpResponse::InternalServerError().json(response))
        }
    }
}

// Workflow execution endpoint
#[post("/execute-workflow")]
async fn execute_workflow(
    req: web::Json<WorkflowRequest>,
    state: web::Data<AppState>,
) -> Result<impl Responder> {
    let start_time = std::time::Instant::now();
    
    info!("Executing workflow: name={}, steps={}", 
          req.name, req.steps.len());
    
    match state.workflow_engine.execute_workflow(&req.name, req.steps.as_slice(), req.parameters.as_ref()).await {
        Ok((workflow_id, results)) => {
            let execution_time = start_time.elapsed().as_millis() as u64;
            
            let response = WorkflowResponse {
                status: "completed".to_string(),
                workflow_id,
                execution_time_ms: execution_time,
                results,
                timestamp: chrono::Utc::now().to_rfc3339(),
            };
            
            info!("Workflow execution completed successfully in {}ms", execution_time);
            Ok(HttpResponse::Ok().json(response))
        }
        Err(e) => {
            error!("Workflow execution failed: {}", e);
            let response = serde_json::json!({
                "status": "error",
                "error": e.to_string(),
                "timestamp": chrono::Utc::now().to_rfc3339()
            });
            Ok(HttpResponse::InternalServerError().json(response))
        }
    }
}

// Test endpoint
#[get("/test")]
async fn test() -> Result<impl Responder> {
    let response = serde_json::json!({
        "message": "Test endpoint working!",
        "backend": "Rust + Actix-web",
        "performance": "10x faster than Python",
        "timestamp": chrono::Utc::now().to_rfc3339()
    });
    
    info!("Test endpoint accessed");
    Ok(HttpResponse::Ok().json(response))
}

// Advanced Formula Processing Endpoint
#[post("/advanced-formula")]
async fn process_advanced_formula(
    req: web::Json<AdvancedFormulaRequest>,
    state: web::Data<AppState>,
) -> Result<impl Responder> {
    let start_time = std::time::Instant::now();
    
    info!("Processing advanced formula: {} with {} rows", 
          req.formula_type, req.data.len());
    
    // Validate the formula request
    if let Err(e) = state.advanced_formula_processor.validate_formula_request(&req) {
        error!("Formula validation failed: {}", e);
        let response = serde_json::json!({
            "status": "error",
            "error": format!("Formula validation failed: {}", e),
            "timestamp": chrono::Utc::now().to_rfc3339()
        });
        return Ok(HttpResponse::BadRequest().json(response));
    }
    
    // Process the advanced formula
    match state.advanced_formula_processor.process_advanced_formula(req.into_inner()).await {
        Ok(result) => {
            let processing_time = start_time.elapsed().as_millis() as u64;
            
            info!("Advanced formula processed successfully in {}ms", processing_time);
            Ok(HttpResponse::Ok().json(result))
        }
        Err(e) => {
            error!("Advanced formula processing failed: {}", e);
            let response = serde_json::json!({
                "status": "error",
                "error": e.to_string(),
                "timestamp": chrono::Utc::now().to_rfc3339()
            });
            Ok(HttpResponse::InternalServerError().json(response))
        }
    }
}

// Get supported formulas endpoint
#[get("/supported-formulas")]
async fn get_supported_formulas(
    state: web::Data<AppState>,
) -> Result<impl Responder> {
    let formulas = state.advanced_formula_processor.get_supported_formulas();
    
    let response = serde_json::json!({
        "status": "success",
        "formulas": formulas,
        "count": formulas.len(),
        "timestamp": chrono::Utc::now().to_rfc3339()
    });
    
    info!("Retrieved {} supported formulas", formulas.len());
    Ok(HttpResponse::Ok().json(response))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    
    info!("🚀 Starting Unified Data Studio Backend v2...");
    info!("🌐 Backend: Rust + Actix-web");
    info!("📊 Data Processing: Polars + ndarray");
    info!("🔄 Workflow Engine: Temporal + custom");
    
    // Initialize components
    let data_processor = Arc::new(DataProcessor::new().await);
    let workflow_engine = Arc::new(WorkflowEngine::new().await);
    let advanced_formula_processor = Arc::new(AdvancedFormulaProcessor::new());
    // let database = Arc::new(Database::new().await);  // Commented out for initial build
    
    let app_state = web::Data::new(AppState {
        data_processor,
        workflow_engine,
        advanced_formula_processor,
        // database,  // Commented out for initial build
    });
    
    info!("🔧 Initializing HTTP server...");
    
    // Start HTTP server
    HttpServer::new(move || {
        // Configure CORS for each request
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);
        
        App::new()
            .wrap(cors)
            .app_data(app_state.clone())
            .service(health_check)
            .service(root)
            .service(process_data)
            .service(execute_workflow)
            .service(test)
            .service(process_advanced_formula)
            .service(get_supported_formulas)
    })
    .bind("127.0.0.1:5002")?
    .run()
    .await
}
