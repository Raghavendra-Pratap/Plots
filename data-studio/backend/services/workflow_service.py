#!/usr/bin/env python3
"""
Workflow Service for Complex Data Processing Orchestration
Handles workflow execution, step management, and result tracking
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class WorkflowService:
    def __init__(self):
        """Initialize workflow service"""
        self.is_healthy_status = False
        self.active_executions = {}  # Track active workflow executions
        self.execution_lock = threading.Lock()
        self.initialize_service()
    
    def initialize_service(self):
        """Initialize workflow service"""
        try:
            self.is_healthy_status = True
            logger.info("Workflow service initialized successfully")
        except Exception as e:
            logger.error(f"Workflow service initialization failed: {e}")
            self.is_healthy_status = False
    
    def is_healthy(self) -> bool:
        """Check if workflow service is healthy"""
        return self.is_healthy_status
    
    def validate_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow configuration"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'complexity_score': 0
            }
            
            # Check required fields
            required_fields = ['name', 'workflow_config']
            for field in required_fields:
                if field not in workflow_config:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"Missing required field: {field}")
            
            if not validation_result['valid']:
                return validation_result
            
            # Validate workflow configuration structure
            workflow_steps = workflow_config.get('workflow_config', {}).get('steps', [])
            if not workflow_steps:
                validation_result['warnings'].append("No workflow steps defined")
            else:
                # Validate each step
                for i, step in enumerate(workflow_steps):
                    step_validation = self._validate_workflow_step(step, i)
                    if not step_validation['valid']:
                        validation_result['valid'] = False
                        validation_result['errors'].extend(step_validation['errors'])
                    validation_result['warnings'].extend(step_validation['warnings'])
                    
                    # Calculate complexity score
                    validation_result['complexity_score'] += step_validation.get('complexity', 1)
            
            # Validate dependencies
            dependency_validation = self._validate_dependencies(workflow_steps)
            if not dependency_validation['valid']:
                validation_result['valid'] = False
                validation_result['errors'].extend(dependency_validation['errors'])
            
            # Check for circular dependencies
            circular_check = self._check_circular_dependencies(workflow_steps)
            if circular_check['has_circular']:
                validation_result['valid'] = False
                validation_result['errors'].append("Circular dependencies detected in workflow")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Workflow validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'complexity_score': 0
            }
    
    def _validate_workflow_step(self, step: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """Validate individual workflow step"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'complexity': 1
        }
        
        # Check required step fields
        required_step_fields = ['type', 'name']
        for field in required_step_fields:
            if field not in step:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Step {step_index}: Missing required field '{field}'")
        
        if not validation_result['valid']:
            return validation_result
        
        # Validate step type
        valid_step_types = ['data_source', 'transformation', 'analysis', 'output', 'custom']
        if step['type'] not in valid_step_types:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Step {step_index}: Invalid step type '{step['type']}'")
        
        # Validate step configuration
        if 'config' not in step:
            validation_result['warnings'].append(f"Step {step_index}: No configuration provided")
        else:
            # Type-specific validation
            if step['type'] == 'transformation':
                config_validation = self._validate_transformation_config(step['config'])
                if not config_validation['valid']:
                    validation_result['valid'] = False
                    validation_result['errors'].extend(config_validation['errors'])
                validation_result['complexity'] += config_validation.get('complexity', 0)
            
            elif step['type'] == 'analysis':
                config_validation = self._validate_analysis_config(step['config'])
                if not config_validation['valid']:
                    validation_result['valid'] = False
                    validation_result['errors'].extend(config_validation['errors'])
                validation_result['complexity'] += config_validation.get('complexity', 0)
        
        # Check dependencies
        if 'dependencies' in step:
            if not isinstance(step['dependencies'], list):
                validation_result['valid'] = False
                validation_result['errors'].append(f"Step {step_index}: Dependencies must be a list")
            else:
                for dep in step['dependencies']:
                    if not isinstance(dep, int) or dep < 0 or dep >= step_index:
                        validation_result['valid'] = False
                        validation_result['errors'].append(f"Step {step_index}: Invalid dependency index {dep}")
        
        return validation_result
    
    def _validate_transformation_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transformation step configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'complexity': 1
        }
        
        # Check transformation type
        if 'type' not in config:
            validation_result['valid'] = False
            validation_result['errors'].append("Transformation type not specified")
        else:
            valid_transformation_types = ['filter', 'sort', 'join', 'aggregate', 'transform', 'custom']
            if config['type'] not in valid_transformation_types:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Invalid transformation type: {config['type']}")
            
            # Increase complexity for complex transformations
            if config['type'] in ['join', 'aggregate']:
                validation_result['complexity'] += 2
            elif config['type'] == 'custom':
                validation_result['complexity'] += 1
        
        # Validate parameters based on type
        if config.get('type') == 'filter':
            if 'condition' not in config:
                validation_result['valid'] = False
                validation_result['errors'].append("Filter transformation requires condition parameter")
        
        elif config.get('type') == 'join':
            if 'join_type' not in config or 'join_columns' not in config:
                validation_result['valid'] = False
                validation_result['errors'].append("Join transformation requires join_type and join_columns parameters")
        
        elif config.get('type') == 'aggregate':
            if 'group_by' not in config or 'aggregations' not in config:
                validation_result['valid'] = False
                validation_result['errors'].append("Aggregate transformation requires group_by and aggregations parameters")
        
        return validation_result
    
    def _validate_analysis_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis step configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'complexity': 1
        }
        
        # Check analysis type
        if 'type' not in config:
            validation_result['valid'] = False
            validation_result['errors'].append("Analysis type not specified")
        else:
            valid_analysis_types = ['statistical', 'time_series', 'hierarchical', 'multi_dimensional', 'custom']
            if config['type'] not in valid_analysis_types:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Invalid analysis type: {config['type']}")
            
            # Increase complexity for complex analyses
            if config['type'] in ['hierarchical', 'multi_dimensional']:
                validation_result['complexity'] += 2
            elif config['type'] == 'time_series':
                validation_result['complexity'] += 1
        
        # Validate parameters based on type
        if config.get('type') == 'statistical':
            if 'columns' not in config:
                validation_result['warnings'].append("Statistical analysis: No columns specified, will auto-detect")
        
        elif config.get('type') == 'time_series':
            if 'time_column' not in config:
                validation_result['valid'] = False
                validation_result['errors'].append("Time series analysis requires time_column parameter")
        
        elif config.get('type') == 'hierarchical':
            if 'hierarchy_levels' not in config:
                validation_result['valid'] = False
                validation_result['errors'].append("Hierarchical analysis requires hierarchy_levels parameter")
        
        return validation_result
    
    def _validate_dependencies(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate workflow dependencies"""
        validation_result = {
            'valid': True,
            'errors': []
        }
        
        for i, step in enumerate(workflow_steps):
            if 'dependencies' in step:
                for dep in step['dependencies']:
                    if dep >= i:
                        validation_result['valid'] = False
                        validation_result['errors'].append(f"Step {i}: Dependency {dep} must be less than current step index")
        
        return validation_result
    
    def _check_circular_dependencies(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for circular dependencies in workflow"""
        try:
            # Build dependency graph
            graph = {}
            for i, step in enumerate(workflow_steps):
                graph[i] = step.get('dependencies', [])
            
            # Check for cycles using DFS
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            # Check all nodes
            for node in graph:
                if node not in visited:
                    if has_cycle(node):
                        return {'has_circular': True, 'cycle_nodes': list(rec_stack)}
            
            return {'has_circular': False, 'cycle_nodes': []}
            
        except Exception as e:
            logger.error(f"Circular dependency check failed: {e}")
            return {'has_circular': False, 'cycle_nodes': []}
    
    def execute_workflow(self, workflow_config: Dict[str, Any], data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with data sources"""
        try:
            # Validate workflow first
            validation = self.validate_workflow(workflow_config)
            if not validation['valid']:
                return {
                    'success': False,
                    'errors': validation['errors'],
                    'warnings': validation['warnings']
                }
            
            # Generate execution ID
            execution_id = str(uuid.uuid4())
            
            # Initialize execution tracking
            with self.execution_lock:
                self.active_executions[execution_id] = {
                    'status': 'running',
                    'start_time': datetime.now(),
                    'steps_completed': 0,
                    'total_steps': len(workflow_config.get('workflow_config', {}).get('steps', [])),
                    'results': {},
                    'errors': []
                }
            
            # Execute workflow steps
            try:
                result = self._execute_workflow_steps(workflow_config, data_sources, execution_id)
                
                # Update execution status
                with self.execution_lock:
                    self.active_executions[execution_id]['status'] = 'completed'
                    self.active_executions[execution_id]['end_time'] = datetime.now()
                    self.active_executions[execution_id]['results'] = result
                
                return {
                    'success': True,
                    'execution_id': execution_id,
                    'results': result,
                    'execution_time': (datetime.now() - self.active_executions[execution_id]['start_time']).total_seconds()
                }
                
            except Exception as e:
                # Update execution status on error
                with self.execution_lock:
                    self.active_executions[execution_id]['status'] = 'failed'
                    self.active_executions[execution_id]['end_time'] = datetime.now()
                    self.active_executions[execution_id]['errors'].append(str(e))
                
                return {
                    'success': False,
                    'execution_id': execution_id,
                    'error': str(e),
                    'execution_time': (datetime.now() - self.active_executions[execution_id]['start_time']).total_seconds()
                }
                
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_workflow_steps(self, workflow_config: Dict[str, Any], data_sources: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute individual workflow steps"""
        steps = workflow_config.get('workflow_config', {}).get('steps', [])
        step_results = {}
        current_data = data_sources.copy()
        
        for i, step in enumerate(steps):
            try:
                # Update execution progress
                with self.execution_lock:
                    self.active_executions[execution_id]['steps_completed'] = i + 1
                
                # Execute step
                step_result = self._execute_step(step, current_data, step_results)
                step_results[f"step_{i}"] = step_result
                
                # Update current data for next steps
                if 'output' in step_result:
                    current_data[step['name']] = step_result['output']
                
                logger.info(f"Step {i} completed: {step['name']}")
                
            except Exception as e:
                logger.error(f"Step {i} failed: {e}")
                raise Exception(f"Step {i} ({step.get('name', 'Unknown')}) failed: {str(e)}")
        
        return {
            'workflow_name': workflow_config.get('name'),
            'steps_executed': len(steps),
            'step_results': step_results,
            'final_data': current_data
        }
    
    def _execute_step(self, step: Dict[str, Any], current_data: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow step"""
        step_type = step.get('type')
        step_name = step.get('name')
        step_config = step.get('config', {})
        
        try:
            if step_type == 'data_source':
                return self._execute_data_source_step(step, current_data, step_results)
            elif step_type == 'transformation':
                return self._execute_transformation_step(step, current_data, step_results)
            elif step_type == 'analysis':
                return self._execute_analysis_step(step, current_data, step_results)
            elif step_type == 'output':
                return self._execute_output_step(step, current_data, step_results)
            elif step_type == 'custom':
                return self._execute_custom_step(step, current_data, step_results)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
                
        except Exception as e:
            logger.error(f"Step execution failed: {step_name} - {e}")
            raise
    
    def _execute_data_source_step(self, step: Dict[str, Any], current_data: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data source step"""
        step_config = step.get('config', {})
        data_source_name = step_config.get('source')
        
        if data_source_name not in current_data:
            raise ValueError(f"Data source '{data_source_name}' not found")
        
        return {
            'step_type': 'data_source',
            'step_name': step.get('name'),
            'output': current_data[data_source_name],
            'metadata': {
                'source': data_source_name,
                'data_type': type(current_data[data_source_name]).__name__
            }
        }
    
    def _execute_transformation_step(self, step: Dict[str, Any], current_data: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transformation step"""
        step_config = step.get('config', {})
        transformation_type = step_config.get('type')
        
        # Get input data from dependencies
        input_data = self._get_step_input_data(step, current_data, step_results)
        
        if transformation_type == 'filter':
            result = self._apply_filter_transformation(input_data, step_config)
        elif transformation_type == 'sort':
            result = self._apply_sort_transformation(input_data, step_config)
        elif transformation_type == 'join':
            result = self._apply_join_transformation(input_data, step_config, current_data)
        elif transformation_type == 'aggregate':
            result = self._apply_aggregate_transformation(input_data, step_config)
        else:
            result = input_data  # Default to no transformation
        
        return {
            'step_type': 'transformation',
            'step_name': step.get('name'),
            'output': result,
            'metadata': {
                'transformation_type': transformation_type,
                'input_size': len(input_data) if hasattr(input_data, '__len__') else 'unknown'
            }
        }
    
    def _execute_analysis_step(self, step: Dict[str, Any], current_data: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis step"""
        step_config = step.get('config', {})
        analysis_type = step_config.get('type')
        
        # Get input data from dependencies
        input_data = self._get_step_input_data(step, current_data, step_results)
        
        # This would integrate with the DuckDB service for actual analysis
        # For now, return a placeholder result
        result = {
            'analysis_type': analysis_type,
            'input_data_size': len(input_data) if hasattr(input_data, '__len__') else 'unknown',
            'status': 'analysis_completed'
        }
        
        return {
            'step_type': 'analysis',
            'step_name': step.get('name'),
            'output': result,
            'metadata': {
                'analysis_type': analysis_type
            }
        }
    
    def _execute_output_step(self, step: Dict[str, Any], current_data: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute output step"""
        step_config = step.get('config', {})
        output_format = step_config.get('format', 'data')
        
        # Get input data from dependencies
        input_data = self._get_step_input_data(step, current_data, step_results)
        
        return {
            'step_type': 'output',
            'step_name': step.get('name'),
            'output': input_data,
            'metadata': {
                'output_format': output_format
            }
        }
    
    def _execute_custom_step(self, step: Dict[str, Any], current_data: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom step"""
        step_config = step.get('config', {})
        custom_function = step_config.get('function')
        
        if not custom_function:
            raise ValueError("Custom step requires function parameter")
        
        # Get input data from dependencies
        input_data = self._get_step_input_data(step, current_data, step_results)
        
        # Execute custom function (this would need to be implemented based on requirements)
        result = f"Custom function '{custom_function}' executed on input data"
        
        return {
            'step_type': 'custom',
            'step_name': step.get('name'),
            'output': result,
            'metadata': {
                'custom_function': custom_function
            }
        }
    
    def _get_step_input_data(self, step: Dict[str, Any], current_data: Dict[str, Any], step_results: Dict[str, Any]):
        """Get input data for a step based on dependencies"""
        dependencies = step.get('dependencies', [])
        
        if not dependencies:
            # No dependencies, use default data source
            return list(current_data.values())[0] if current_data else None
        
        # Get data from dependency steps
        dependency_data = []
        for dep_index in dependencies:
            dep_key = f"step_{dep_index}"
            if dep_key in step_results and 'output' in step_results[dep_key]:
                dependency_data.append(step_results[dep_key]['output'])
        
        if len(dependency_data) == 1:
            return dependency_data[0]
        else:
            return dependency_data
    
    def _apply_filter_transformation(self, data, config):
        """Apply filter transformation"""
        # Placeholder implementation
        return data
    
    def _apply_sort_transformation(self, data, config):
        """Apply sort transformation"""
        # Placeholder implementation
        return data
    
    def _apply_join_transformation(self, data, config, current_data):
        """Apply join transformation"""
        # Placeholder implementation
        return data
    
    def _apply_aggregate_transformation(self, data, config):
        """Apply aggregate transformation"""
        # Placeholder implementation
        return data
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            return {
                'execution_id': execution_id,
                'status': execution['status'],
                'start_time': execution['start_time'].isoformat() if execution['start_time'] else None,
                'end_time': execution['end_time'].isoformat() if execution.get('end_time') else None,
                'steps_completed': execution['steps_completed'],
                'total_steps': execution['total_steps'],
                'progress': (execution['steps_completed'] / execution['total_steps']) * 100 if execution['total_steps'] > 0 else 0,
                'errors': execution.get('errors', [])
            }
        else:
            return {'error': 'Execution ID not found'}
    
    def get_all_executions(self) -> List[Dict[str, Any]]:
        """Get all workflow executions"""
        executions = []
        for execution_id, execution in self.active_executions.items():
            executions.append({
                'execution_id': execution_id,
                'status': execution['status'],
                'start_time': execution['start_time'].isoformat() if execution['start_time'] else None,
                'end_time': execution['end_time'].isoformat() if execution.get('end_time') else None,
                'steps_completed': execution['steps_completed'],
                'total_steps': execution['total_steps']
            })
        return executions
    
    def cleanup_execution(self, execution_id: str) -> bool:
        """Clean up completed execution"""
        try:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                if execution['status'] in ['completed', 'failed']:
                    del self.active_executions[execution_id]
                    return True
                else:
                    return False  # Cannot clean up running execution
            return False
        except Exception as e:
            logger.error(f"Execution cleanup failed: {e}")
            return False
