#!/usr/bin/env python3
"""
Database Models and Initialization for Unified Data Studio
Handles database setup, connection management, and model definitions
"""

import sqlite3
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str = "data/unified_data_studio.db"):
        self.db_path = db_path
        self.connection = None
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection, creating if necessary"""
        if self.connection is None or self.connection.closed:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable row factory for named access
        return self.connection
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return [{'affected_rows': cursor.rowcount}]
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_transaction(self, queries: list) -> bool:
        """Execute multiple queries in a transaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for query, params in queries:
                cursor.execute(query, params)
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise

def init_database(db_path: str = "data/unified_data_studio.db") -> bool:
    """Initialize the database with required tables"""
    try:
        db_manager = DatabaseManager(db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                tags TEXT
            )
        ''')
        
        # Create files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_status TEXT DEFAULT 'pending',
                metadata TEXT,
                checksum TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Create workflows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                workflow_config TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'draft',
                execution_count INTEGER DEFAULT 0,
                last_executed TIMESTAMP,
                version TEXT DEFAULT '1.0',
                tags TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Create workflow_executions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER,
                execution_id TEXT UNIQUE,
                status TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                result_summary TEXT,
                error_log TEXT,
                performance_metrics TEXT,
                user_id TEXT,
                FOREIGN KEY (workflow_id) REFERENCES workflows (id)
            )
        ''')
        
        # Create user_preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                category TEXT DEFAULT 'general',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')
        
        # Create data_sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                connection_string TEXT,
                credentials TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Create analytics_results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                workflow_id INTEGER,
                analysis_type TEXT NOT NULL,
                result_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time REAL,
                parameters TEXT,
                status TEXT DEFAULT 'completed',
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (workflow_id) REFERENCES workflows (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflows_project_id ON workflows(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON workflow_executions(workflow_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow_executions(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_project_id ON analytics_results(project_id)')
        
        # Insert default user preferences
        default_preferences = [
            ('theme', 'light', 'appearance', 'Application theme (light/dark)'),
            ('auto_save', 'true', 'workflow', 'Auto-save workflow changes'),
            ('max_file_size', '100', 'file', 'Maximum file size in MB'),
            ('default_project', '', 'project', 'Default project to open'),
            ('language', 'en', 'localization', 'Application language'),
            ('timezone', 'UTC', 'localization', 'User timezone'),
            ('notifications', 'true', 'app', 'Enable notifications'),
            ('data_preview_rows', '100', 'data', 'Number of rows to show in data preview'),
            ('export_format', 'csv', 'export', 'Default export format'),
            ('backup_frequency', 'daily', 'backup', 'Backup frequency')
        ]
        
        for pref_key, pref_value, category, description in default_preferences:
            cursor.execute('''
                INSERT OR IGNORE INTO user_preferences (key, value, category, description)
                VALUES (?, ?, ?, ?)
            ''', (pref_key, pref_value, category, description))
        
        # Insert sample project if none exist
        cursor.execute('SELECT COUNT(*) FROM projects')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO projects (name, description, status, tags)
                VALUES (?, ?, ?, ?)
            ''', ('Sample Project', 'A sample project to get you started', 'active', 'sample,getting-started'))
        
        conn.commit()
        db_manager.close_connection()
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def get_database_info(db_path: str = "data/unified_data_studio.db") -> Dict[str, Any]:
    """Get database information and statistics"""
    try:
        db_manager = DatabaseManager(db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get row counts for each table
        table_stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            table_stats[table] = cursor.fetchone()[0]
        
        # Get database file size
        file_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        # Get database version
        cursor.execute("SELECT sqlite_version()")
        sqlite_version = cursor.fetchone()[0]
        
        db_manager.close_connection()
        
        return {
            'database_path': db_path,
            'sqlite_version': sqlite_version,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'tables': tables,
            'table_stats': table_stats,
            'total_records': sum(table_stats.values())
        }
        
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {'error': str(e)}

def backup_database(db_path: str = "data/unified_data_studio.db", backup_path: str = None) -> bool:
    """Create a backup of the database"""
    try:
        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            return False
        
        if backup_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{db_path}.backup_{timestamp}"
        
        # Create backup directory if it doesn't exist
        backup_dir = Path(backup_path).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy database file
        import shutil
        shutil.copy2(db_path, backup_path)
        
        logger.info(f"Database backed up to: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return False

def restore_database(backup_path: str, db_path: str = "data/unified_data_studio.db") -> bool:
    """Restore database from backup"""
    try:
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Create backup of current database if it exists
        if os.path.exists(db_path):
            current_backup = f"{db_path}.before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_database(db_path, current_backup)
        
        # Restore from backup
        import shutil
        shutil.copy2(backup_path, db_path)
        
        logger.info(f"Database restored from: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"Database restore failed: {e}")
        return False

def optimize_database(db_path: str = "data/unified_data_studio.db") -> bool:
    """Optimize database performance"""
    try:
        db_manager = DatabaseManager(db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Analyze tables for better query planning
        cursor.execute("ANALYZE")
        
        # Vacuum database to reclaim space
        cursor.execute("VACUUM")
        
        # Update statistics
        cursor.execute("UPDATE sqlite_stat1 SET stat = stat")
        
        conn.commit()
        db_manager.close_connection()
        
        logger.info("Database optimization completed")
        return True
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return False

# Convenience functions for common operations
def get_project_by_id(project_id: int, db_path: str = "data/unified_data_studio.db") -> Optional[Dict[str, Any]]:
    """Get project by ID"""
    try:
        db_manager = DatabaseManager(db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, created_at, updated_at, status, metadata, tags
            FROM projects WHERE id = ?
        ''', (project_id,))
        
        row = cursor.fetchone()
        db_manager.close_connection()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        return None

def get_workflows_by_project(project_id: int, db_path: str = "data/unified_data_studio.db") -> list:
    """Get all workflows for a project"""
    try:
        db_manager = DatabaseManager(db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, workflow_config, created_at, updated_at, status, execution_count, last_executed, version, tags
            FROM workflows WHERE project_id = ? ORDER BY updated_at DESC
        ''', (project_id,))
        
        workflows = [dict(row) for row in cursor.fetchall()]
        db_manager.close_connection()
        
        return workflows
        
    except Exception as e:
        logger.error(f"Failed to get workflows for project {project_id}: {e}")
        return []

def get_file_info(file_id: int, db_path: str = "data/unified_data_studio.db") -> Optional[Dict[str, Any]]:
    """Get file information by ID"""
    try:
        db_manager = DatabaseManager(db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, project_id, filename, file_path, file_size, file_type, upload_date, processing_status, metadata, checksum
            FROM files WHERE id = ?
        ''', (file_id,))
        
        row = cursor.fetchone()
        db_manager.close_connection()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        logger.error(f"Failed to get file {file_id}: {e}")
        return None
