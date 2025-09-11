#!/usr/bin/env python3
"""
Data Service for File Management and Metadata Storage
Handles file operations, project management, and data persistence
"""

import logging
import os
import sqlite3
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        """Initialize data service"""
        self.is_healthy_status = False
        self.db_path = "data/unified_data_studio.db"
        self.data_dir = "data"
        self.projects_dir = "data/projects"
        self.initialize_service()
    
    def initialize_service(self):
        """Initialize data service and database"""
        try:
            # Create data directories
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.projects_dir, exist_ok=True)
            
            # Initialize database
            self._init_database()
            
            self.is_healthy_status = True
            logger.info("Data service initialized successfully")
            
        except Exception as e:
            logger.error(f"Data service initialization failed: {e}")
            self.is_healthy_status = False
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
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
                    metadata TEXT
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
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id)
                )
            ''')
            
            # Create user_preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def is_healthy(self) -> bool:
        """Check if data service is healthy"""
        return self.is_healthy_status
    
    def create_project(self, name: str, description: str = "", metadata: Dict = None) -> Dict[str, Any]:
        """Create a new project"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create project directory
            project_dir = os.path.join(self.projects_dir, name.replace(' ', '_').lower())
            os.makedirs(project_dir, exist_ok=True)
            
            # Insert project record
            cursor.execute('''
                INSERT INTO projects (name, description, metadata)
                VALUES (?, ?, ?)
            ''', (name, description, json.dumps(metadata) if metadata else None))
            
            project_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Project created: {name} (ID: {project_id})")
            
            return {
                'id': project_id,
                'name': name,
                'description': description,
                'metadata': metadata,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Project creation failed: {e}")
            raise
    
    def get_projects(self, status: str = None) -> List[Dict[str, Any]]:
        """Get all projects or projects with specific status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT id, name, description, created_at, updated_at, status, metadata
                    FROM projects
                    WHERE status = ?
                    ORDER BY updated_at DESC
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT id, name, description, created_at, updated_at, status, metadata
                    FROM projects
                    ORDER BY updated_at DESC
                ''')
            
            projects = []
            for row in cursor.fetchall():
                project = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'status': row[5],
                    'metadata': json.loads(row[6]) if row[6] else {}
                }
                projects.append(project)
            
            conn.close()
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            raise
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, created_at, updated_at, status, metadata
                FROM projects
                WHERE id = ?
            ''', (project_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'status': row[5],
                    'metadata': json.loads(row[6]) if row[6] else {}
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            raise
    
    def update_project(self, project_id: int, updates: Dict[str, Any]) -> bool:
        """Update project information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            update_fields = []
            update_values = []
            
            for key, value in updates.items():
                if key in ['name', 'description', 'status']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
                elif key == 'metadata':
                    update_fields.append("metadata = ?")
                    update_values.append(json.dumps(value))
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(project_id)
                
                query = f"UPDATE projects SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                
                conn.commit()
                conn.close()
                
                logger.info(f"Project {project_id} updated successfully")
                return True
            else:
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            raise
    
    def delete_project(self, project_id: int) -> bool:
        """Delete project and all associated data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get project name for directory cleanup
            cursor.execute('SELECT name FROM projects WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return False
            
            project_name = row[0]
            
            # Delete associated records
            cursor.execute('DELETE FROM workflow_executions WHERE workflow_id IN (SELECT id FROM workflows WHERE project_id = ?)', (project_id,))
            cursor.execute('DELETE FROM workflows WHERE project_id = ?', (project_id,))
            cursor.execute('DELETE FROM files WHERE project_id = ?', (project_id,))
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            
            conn.commit()
            conn.close()
            
            # Remove project directory
            project_dir = os.path.join(self.projects_dir, project_name.replace(' ', '_').lower())
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            
            logger.info(f"Project {project_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            raise
    
    def store_file_metadata(self, filename: str, file_path: str, project_id: int = None, 
                           file_size: int = None, file_type: str = None, 
                           processing_result: Dict = None) -> int:
        """Store file metadata in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Determine file type if not provided
            if not file_type:
                file_type = os.path.splitext(filename)[1].lower()
            
            # Get file size if not provided
            if not file_size:
                file_size = os.path.getsize(file_path)
            
            # Store file metadata
            cursor.execute('''
                INSERT INTO files (project_id, filename, file_path, file_size, file_type, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project_id, filename, file_path, file_size, file_type, 
                  json.dumps(processing_result) if processing_result else None))
            
            file_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"File metadata stored: {filename} (ID: {file_id})")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to store file metadata: {e}")
            raise
    
    def get_project_files(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all files for a project"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, filename, file_path, file_size, file_type, upload_date, processing_status, metadata
                FROM files
                WHERE project_id = ?
                ORDER BY upload_date DESC
            ''', (project_id,))
            
            files = []
            for row in cursor.fetchall():
                file_info = {
                    'id': row[0],
                    'filename': row[1],
                    'file_path': row[2],
                    'file_size': row[3],
                    'file_type': row[4],
                    'upload_date': row[5],
                    'processing_status': row[6],
                    'metadata': json.loads(row[7]) if row[7] else {}
                }
                files.append(file_info)
            
            conn.close()
            return files
            
        except Exception as e:
            logger.error(f"Failed to get project files: {e}")
            raise
    
    def update_file_status(self, file_id: int, status: str, metadata: Dict = None) -> bool:
        """Update file processing status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if metadata:
                cursor.execute('''
                    UPDATE files 
                    SET processing_status = ?, metadata = ?
                    WHERE id = ?
                ''', (status, json.dumps(metadata), file_id))
            else:
                cursor.execute('''
                    UPDATE files 
                    SET processing_status = ?
                    WHERE id = ?
                ''', (status, file_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"File {file_id} status updated to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update file status: {e}")
            raise
    
    def save_workflow(self, project_id: int, name: str, description: str, 
                     workflow_config: Dict[str, Any]) -> int:
        """Save workflow configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO workflows (project_id, name, description, workflow_config)
                VALUES (?, ?, ?, ?)
            ''', (project_id, name, description, json.dumps(workflow_config)))
            
            workflow_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Workflow saved: {name} (ID: {workflow_id})")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            raise
    
    def get_project_workflows(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all workflows for a project"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, description, workflow_config, created_at, updated_at, status, execution_count, last_executed
                FROM workflows
                WHERE project_id = ?
                ORDER BY updated_at DESC
            ''', (project_id,))
            
            workflows = []
            for row in cursor.fetchall():
                workflow = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'workflow_config': json.loads(row[3]),
                    'created_at': row[4],
                    'updated_at': row[5],
                    'status': row[6],
                    'execution_count': row[7],
                    'last_executed': row[8]
                }
                workflows.append(workflow)
            
            conn.close()
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to get project workflows: {e}")
            raise
    
    def update_workflow_execution_count(self, workflow_id: int) -> bool:
        """Update workflow execution count and last executed time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE workflows 
                SET execution_count = execution_count + 1, last_executed = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (workflow_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update workflow execution count: {e}")
            raise
    
    def log_workflow_execution(self, workflow_id: int, execution_id: str, status: str,
                              start_time: datetime, end_time: datetime = None,
                              result_summary: str = None, error_log: str = None) -> int:
        """Log workflow execution details"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO workflow_executions (workflow_id, execution_id, status, start_time, end_time, result_summary, error_log)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (workflow_id, execution_id, status, start_time, end_time, result_summary, error_log))
            
            execution_log_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            logger.info(f"Workflow execution logged: {execution_id}")
            return execution_log_id
            
        except Exception as e:
            logger.error(f"Failed to log workflow execution: {e}")
            raise
    
    def get_user_preference(self, key: str) -> Optional[str]:
        """Get user preference value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            conn.close()
            
            return row[0] if row else None
            
        except Exception as e:
            logger.error(f"Failed to get user preference {key}: {e}")
            return None
    
    def set_user_preference(self, key: str, value: str) -> bool:
        """Set user preference value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User preference set: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set user preference: {e}")
            raise
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all data in the system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute('SELECT COUNT(*) FROM projects')
            project_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM files')
            file_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM workflows')
            workflow_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM workflow_executions')
            execution_count = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute('''
                SELECT name, updated_at FROM projects 
                ORDER BY updated_at DESC LIMIT 5
            ''')
            recent_projects = [{'name': row[0], 'updated_at': row[1]} for row in cursor.fetchall()]
            
            cursor.execute('''
                SELECT filename, upload_date FROM files 
                ORDER BY upload_date DESC LIMIT 5
            ''')
            recent_files = [{'filename': row[0], 'upload_date': row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'summary': {
                    'total_projects': project_count,
                    'total_files': file_count,
                    'total_workflows': workflow_count,
                    'total_executions': execution_count
                },
                'recent_activity': {
                    'recent_projects': recent_projects,
                    'recent_files': recent_files
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get data summary: {e}")
            raise
    
    def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up old data and files"""
        try:
            cleanup_stats = {
                'files_removed': 0,
                'executions_cleaned': 0,
                'projects_archived': 0
            }
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clean up old workflow executions
            cursor.execute('''
                DELETE FROM workflow_executions 
                WHERE start_time < datetime('now', '-{} days')
            '''.format(days_old))
            
            cleanup_stats['executions_cleaned'] = cursor.rowcount
            
            # Archive old projects (set status to archived)
            cursor.execute('''
                UPDATE projects 
                SET status = 'archived'
                WHERE updated_at < datetime('now', '-{} days') AND status = 'active'
            '''.format(days_old))
            
            cleanup_stats['projects_archived'] = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Data cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
            raise
