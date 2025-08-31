use anyhow::{Result, anyhow};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::{sqlite::SqlitePool, Row};
use std::path::Path;
use tracing::{info, warn, error};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub database_url: String,
    pub max_connections: u32,
    pub timeout_seconds: u64,
}

impl Default for DatabaseConfig {
    fn default() -> Self {
        Self {
            database_url: "sqlite:data/uds_v2.db".to_string(),
            max_connections: 5,
            timeout_seconds: 30,
        }
    }
}

pub struct Database {
    pool: SqlitePool,
    config: DatabaseConfig,
}

impl Database {
    pub async fn new() -> Result<Self> {
        let config = DatabaseConfig::default();
        
        // Ensure data directory exists
        if let Some(parent) = Path::new(&config.database_url).parent() {
            if !parent.exists() {
                std::fs::create_dir_all(parent)
                    .map_err(|e| anyhow!("Failed to create data directory: {}", e))?;
            }
        }
        
        // Create connection pool
        let pool = SqlitePool::connect(&config.database_url).await
            .map_err(|e| anyhow!("Failed to connect to database: {}", e))?;
        
        info!("Database connection pool created with {} max connections", config.max_connections);
        
        // Initialize database schema
        let db = Database { pool, config };
        db.initialize_schema().await?;
        
        Ok(db)
    }
    
    async fn initialize_schema(&self) -> Result<()> {
        info!("Initializing database schema...");
        
        // Create tables
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            "#
        ).execute(&self.pool).await
            .map_err(|e| anyhow!("Failed to create workflows table: {}", e))?;
        
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS workflow_steps (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                step_order INTEGER NOT NULL,
                operation TEXT NOT NULL,
                parameters TEXT,
                status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                started_at DATETIME,
                completed_at DATETIME,
                FOREIGN KEY (workflow_id) REFERENCES workflows (id)
            )
            "#
        ).execute(&self.pool).await
            .map_err(|e| anyhow!("Failed to create workflow_steps table: {}", e))?;
        
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS data_sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                connection_string TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            "#
        ).execute(&self.pool).await
            .map_err(|e| anyhow!("Failed to create data_sources table: {}", e))?;
        
        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS data_operations (
                id TEXT PRIMARY KEY,
                data_source_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                parameters TEXT,
                result TEXT,
                execution_time_ms INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (data_source_id) REFERENCES data_sources (id)
            )
            "#
        ).execute(&self.pool).await
            .map_err(|e| anyhow!("Failed to create data_operations table: {}", e))?;
        
        // Create indexes
        sqlx::query("CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows (status)").execute(&self.pool).await?;
        sqlx::query("CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow_id ON workflow_steps (workflow_id)").execute(&self.pool).await?;
        sqlx::query("CREATE INDEX IF NOT EXISTS idx_data_operations_data_source_id ON data_operations (data_source_id)").execute(&self.pool).await?;
        
        info!("Database schema initialized successfully");
        Ok(())
    }
    
    // Workflow management
    pub async fn save_workflow(&self, workflow_id: &str, name: &str, status: &str) -> Result<()> {
        sqlx::query(
            r#"
            INSERT OR REPLACE INTO workflows (id, name, status, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            "#
        )
        .bind(workflow_id)
        .bind(name)
        .bind(status)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to save workflow: {}", e))?;
        
        Ok(())
    }
    
    pub async fn update_workflow_status(&self, workflow_id: &str, status: &str) -> Result<()> {
        sqlx::query(
            r#"
            UPDATE workflows 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            "#
        )
        .bind(status)
        .bind(workflow_id)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to update workflow status: {}", e))?;
        
        Ok(())
    }
    
    pub async fn get_workflow(&self, workflow_id: &str) -> Result<Option<Value>> {
        let row = sqlx::query(
            r#"
            SELECT id, name, status, created_at, updated_at
            FROM workflows
            WHERE id = ?
            "#
        )
        .bind(workflow_id)
        .fetch_optional(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to fetch workflow: {}", e))?;
        
        if let Some(row) = row {
            let workflow = serde_json::json!({
                "id": row.get::<String, _>("id"),
                "name": row.get::<String, _>("name"),
                "status": row.get::<String, _>("status"),
                "created_at": row.get::<String, _>("created_at"),
                "updated_at": row.get::<String, _>("updated_at")
            });
            Ok(Some(workflow))
        } else {
            Ok(None)
        }
    }
    
    pub async fn get_workflows_by_status(&self, status: &str) -> Result<Vec<Value>> {
        let rows = sqlx::query(
            r#"
            SELECT id, name, status, created_at, updated_at
            FROM workflows
            WHERE status = ?
            ORDER BY updated_at DESC
            "#
        )
        .bind(status)
        .fetch_all(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to fetch workflows: {}", e))?;
        
        let workflows: Vec<Value> = rows.iter().map(|row| {
            serde_json::json!({
                "id": row.get::<String, _>("id"),
                "name": row.get::<String, _>("name"),
                "status": row.get::<String, _>("status"),
                "created_at": row.get::<String, _>("created_at"),
                "updated_at": row.get::<String, _>("updated_at")
            })
        }).collect();
        
        Ok(workflows)
    }
    
    // Workflow steps management
    pub async fn save_workflow_step(&self, step_id: &str, workflow_id: &str, step_order: i32, 
                                   operation: &str, parameters: Option<&Value>) -> Result<()> {
        let params_json = parameters.map(|p| serde_json::to_string(p).unwrap_or_default());
        
        sqlx::query(
            r#"
            INSERT OR REPLACE INTO workflow_steps 
            (id, workflow_id, step_order, operation, parameters, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
            "#
        )
        .bind(step_id)
        .bind(workflow_id)
        .bind(step_order)
        .bind(operation)
        .bind(params_json)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to save workflow step: {}", e))?;
        
        Ok(())
    }
    
    pub async fn update_step_status(&self, step_id: &str, status: &str, result: Option<&Value>, 
                                   error: Option<&str>) -> Result<()> {
        let result_json = result.map(|r| serde_json::to_string(r).unwrap_or_default());
        let now = chrono::Utc::now().to_rfc3339();
        
        sqlx::query(
            r#"
            UPDATE workflow_steps 
            SET status = ?, result = ?, error = ?, completed_at = ?
            WHERE id = ?
            "#
        )
        .bind(status)
        .bind(result_json)
        .bind(error)
        .bind(now)
        .bind(step_id)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to update step status: {}", e))?;
        
        Ok(())
    }
    
    pub async fn get_workflow_steps(&self, workflow_id: &str) -> Result<Vec<Value>> {
        let rows = sqlx::query(
            r#"
            SELECT id, step_order, operation, parameters, status, result, error, started_at, completed_at
            FROM workflow_steps
            WHERE workflow_id = ?
            ORDER BY step_order
            "#
        )
        .bind(workflow_id)
        .fetch_all(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to fetch workflow steps: {}", e))?;
        
        let steps: Vec<Value> = rows.iter().map(|row| {
            serde_json::json!({
                "id": row.get::<String, _>("id"),
                "step_order": row.get::<i32, _>("step_order"),
                "operation": row.get::<String, _>("operation"),
                "parameters": row.get::<Option<String>, _>("parameters")
                    .and_then(|p| serde_json::from_str(&p).ok()),
                "status": row.get::<String, _>("status"),
                "result": row.get::<Option<String>, _>("result")
                    .and_then(|r| serde_json::from_str(&r).ok()),
                "error": row.get::<Option<String>, _>("error"),
                "started_at": row.get::<Option<String>, _>("started_at"),
                "completed_at": row.get::<Option<String>, _>("completed_at")
            })
        }).collect();
        
        Ok(steps)
    }
    
    // Data source management
    pub async fn save_data_source(&self, id: &str, name: &str, source_type: &str, 
                                 connection_string: Option<&str>, metadata: Option<&Value>) -> Result<()> {
        let metadata_json = metadata.map(|m| serde_json::to_string(m).unwrap_or_default());
        
        sqlx::query(
            r#"
            INSERT OR REPLACE INTO data_sources 
            (id, name, type, connection_string, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            "#
        )
        .bind(id)
        .bind(name)
        .bind(source_type)
        .bind(connection_string)
        .bind(metadata_json)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to save data source: {}", e))?;
        
        Ok(())
    }
    
    pub async fn get_data_sources(&self) -> Result<Vec<Value>> {
        let rows = sqlx::query(
            r#"
            SELECT id, name, type, connection_string, metadata, created_at, updated_at
            FROM data_sources
            ORDER BY name
            "#
        )
        .fetch_all(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to fetch data sources: {}", e))?;
        
        let sources: Vec<Value> = rows.iter().map(|row| {
            serde_json::json!({
                "id": row.get::<String, _>("id"),
                "name": row.get::<String, _>("name"),
                "type": row.get::<String, _>("type"),
                "connection_string": row.get::<Option<String>, _>("connection_string"),
                "metadata": row.get::<Option<String>, _>("metadata")
                    .and_then(|m| serde_json::from_str(&m).ok()),
                "created_at": row.get::<String, _>("created_at"),
                "updated_at": row.get::<String, _>("updated_at")
            })
        }).collect();
        
        Ok(sources)
    }
    
    // Data operations logging
    pub async fn log_data_operation(&self, id: &str, data_source_id: &str, operation: &str, 
                                   parameters: Option<&Value>, result: Option<&Value>, 
                                   execution_time_ms: u64) -> Result<()> {
        let params_json = parameters.map(|p| serde_json::to_string(p).unwrap_or_default());
        let result_json = result.map(|r| serde_json::to_string(r).unwrap_or_default());
        
        sqlx::query(
            r#"
            INSERT INTO data_operations 
            (id, data_source_id, operation, parameters, result, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?)
            "#
        )
        .bind(id)
        .bind(data_source_id)
        .bind(operation)
        .bind(params_json)
        .bind(result_json)
        .bind(execution_time_ms)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to log data operation: {}", e))?;
        
        Ok(())
    }
    
    // Database health check
    pub async fn health_check(&self) -> Result<Value> {
        // Test database connection
        let _ = sqlx::query("SELECT 1").fetch_one(&self.pool).await
            .map_err(|e| anyhow!("Database health check failed: {}", e))?;
        
        // Get basic stats
        let workflow_count: i64 = sqlx::query("SELECT COUNT(*) FROM workflows")
            .fetch_one(&self.pool).await?
            .get(0);
        
        let data_source_count: i64 = sqlx::query("SELECT COUNT(*) FROM data_sources")
            .fetch_one(&self.pool).await?
            .get(0);
        
        Ok(serde_json::json!({
            "status": "healthy",
            "database": "SQLite",
            "workflow_count": workflow_count,
            "data_source_count": data_source_count,
            "timestamp": chrono::Utc::now().to_rfc3339()
        }))
    }
    
    // Cleanup old data
    pub async fn cleanup_old_data(&self, days_to_keep: i32) -> Result<u64> {
        let cutoff_date = chrono::Utc::now() - chrono::Duration::days(days_to_keep as i64);
        let cutoff_str = cutoff_date.to_rfc3339();
        
        // Clean up old workflow steps
        let steps_deleted = sqlx::query(
            r#"
            DELETE FROM workflow_steps 
            WHERE workflow_id IN (
                SELECT id FROM workflows 
                WHERE updated_at < ?
            )
            "#
        )
        .bind(&cutoff_str)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to cleanup old workflow steps: {}", e))?
        .rows_affected();
        
        // Clean up old workflows
        let workflows_deleted = sqlx::query(
            "DELETE FROM workflows WHERE updated_at < ?"
        )
        .bind(&cutoff_str)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to cleanup old workflows: {}", e))?
        .rows_affected();
        
        // Clean up old data operations
        let operations_deleted = sqlx::query(
            "DELETE FROM data_operations WHERE created_at < ?"
        )
        .bind(&cutoff_str)
        .execute(&self.pool)
        .await
        .map_err(|e| anyhow!("Failed to cleanup old data operations: {}", e))?
        .rows_affected();
        
        let total_deleted = steps_deleted + workflows_deleted + operations_deleted;
        
        info!("Database cleanup completed: {} records deleted", total_deleted);
        
        Ok(total_deleted)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_database_creation() {
        let db = Database::new().await.unwrap();
        assert!(db.health_check().await.is_ok());
    }
    
    #[tokio::test]
    async fn test_workflow_operations() {
        let db = Database::new().await.unwrap();
        
        // Test saving workflow
        db.save_workflow("test_workflow", "Test Workflow", "running").await.unwrap();
        
        // Test retrieving workflow
        let workflow = db.get_workflow("test_workflow").await.unwrap();
        assert!(workflow.is_some());
        
        // Test updating workflow status
        db.update_workflow_status("test_workflow", "completed").await.unwrap();
        
        let updated_workflow = db.get_workflow("test_workflow").await.unwrap().unwrap();
        assert_eq!(updated_workflow["status"], "completed");
    }
}
