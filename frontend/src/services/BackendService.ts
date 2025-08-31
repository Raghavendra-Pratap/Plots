import { FormulaDefinition } from '../utils/formulaService';

// Backend API configuration
const BACKEND_BASE_URL = 'http://127.0.0.1:5002';

// Types for backend communication
export interface BackendDataRequest {
  data: number[];
  operation: string;
  parameters?: any;
}

export interface BackendDataResponse {
  status: string;
  result: any;
  processing_time_ms: number;
  timestamp: string;
}

export interface BackendWorkflowStep {
  id: string;
  operation: string;
  dependencies: string[];
  data: any;
  parameters?: any;
  timeout_ms?: number;
  retry_count?: number;
}

export interface BackendWorkflowRequest {
  name: string;
  steps: BackendWorkflowStep[];
  parameters?: any;
}

export interface BackendWorkflowResponse {
  status: string;
  workflow_id: string;
  execution_time_ms: number;
  results: any;
  timestamp: string;
}

export interface BackendHealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  backend_type: string;
}

// Backend service class
export class BackendService {
  private baseUrl: string;

  constructor(baseUrl: string = BACKEND_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Check if backend is healthy
  async checkHealth(): Promise<BackendHealthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (!response.ok) {
        throw new Error(`Backend health check failed: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Backend health check error:', error);
      throw error;
    }
  }

  // Process data using backend
  async processData(request: BackendDataRequest): Promise<BackendDataResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/process-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Data processing failed: ${response.status} - ${errorData.error || 'Unknown error'}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Data processing error:', error);
      throw error;
    }
  }

  // Execute workflow using backend
  async executeWorkflow(request: BackendWorkflowRequest): Promise<BackendWorkflowResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/execute-workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Workflow execution failed: ${response.status} - ${errorData.error || 'Unknown error'}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Workflow execution error:', error);
      throw error;
    }
  }

  // Convert frontend workflow steps to backend format
  convertWorkflowSteps(frontendSteps: any[]): BackendWorkflowStep[] {
    return frontendSteps.map((step, index) => ({
      id: step.id || `step_${index + 1}`,
      operation: this.mapOperationToBackend(step.type, step.source),
      dependencies: step.dependencies || [],
      data: this.extractStepData(step),
      parameters: this.extractStepParameters(step),
      timeout_ms: 30000, // 30 seconds default timeout
      retry_count: 3, // 3 retries default
    }));
  }

  // Map frontend operation types to backend operations
  private mapOperationToBackend(stepType: string, source: string): string {
    switch (stepType) {
      case 'function':
        return 'data_transform';
      case 'column':
        return 'data_transform';
      case 'sheet':
        return 'file_operation';
      case 'custom':
        return 'data_transform';
      default:
        return 'data_transform';
    }
  }

  // Extract data for backend step
  private extractStepData(step: any): any {
    // This would need to be implemented based on your data structure
    // For now, return a placeholder
    return step.data || [];
  }

  // Extract parameters for backend step
  private extractStepParameters(step: any): any {
    const params: any = {};

    if (step.type === 'function') {
      params.operation = 'aggregate';
      params.function = step.source;
    } else if (step.type === 'column') {
      params.operation = 'select';
      params.columns = [step.source];
    } else if (step.type === 'sheet') {
      params.operation = 'read_csv';
      params.file_path = step.source;
    }

    return params;
  }

  // Test backend connectivity
  async testConnection(): Promise<boolean> {
    try {
      await this.checkHealth();
      return true;
    } catch (error) {
      console.error('Backend connection test failed:', error);
      return false;
    }
  }

  // Get backend status
  async getBackendStatus(): Promise<{ connected: boolean; version?: string; error?: string }> {
    try {
      const health = await this.checkHealth();
      return {
        connected: true,
        version: health.version,
      };
    } catch (error) {
      return {
        connected: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}

// Export singleton instance
export const backendService = new BackendService();
