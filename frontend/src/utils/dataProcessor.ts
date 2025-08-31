// @ts-ignore
import Papa from 'papaparse';
import * as tf from '@tensorflow/tfjs';

export interface ProcessedData {
  data: any[];
  columns: string[];
  rowCount: number;
  executionTime: number;
  memoryUsage: number;
  sampleSize: number;
  stepIndex: number;
}

export interface WorkflowStep {
  id: string;
  type: 'column' | 'function' | 'break' | 'custom' | 'sheet';
  source: string;
  target?: string;
  sheet?: string;
  parameters?: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  columnReference?: { fileName: string; columnName: string };
}

export interface FileData {
  name: string;
  type: string;
  data: any[];
  columns: string[];
  sheets?: { [sheetName: string]: any[] };
  currentSheet?: string;
}

class DataProcessor {
  private isInitialized = false;

  constructor() {
    this.initializeProcessor();
  }

  private async initializeProcessor() {
    try {
      // Initialize TensorFlow.js
      await tf.ready();
      this.isInitialized = true;
      console.log('Data processor initialized successfully with TensorFlow.js');
    } catch (error) {
      console.error('Failed to initialize data processor:', error);
      this.isInitialized = false;
    }
  }

  private async ensureInitialized(): Promise<boolean> {
    if (!this.isInitialized) {
      await this.initializeProcessor();
    }
    return this.isInitialized;
  }

  // Parse CSV data using PapaParse
  parseCSVData(csvText: string): { data: any[], columns: string[] } {
    const result = Papa.parse(csvText, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: false
    });

    if (result.errors.length > 0) {
      console.warn('CSV parsing warnings:', result.errors);
    }

    return {
      data: result.data as any[],
      columns: result.meta.fields || []
    };
  }

  // Process workflow step and return preview data
  async processWorkflowStep(
    step: WorkflowStep,
    fileData: FileData[],
    sampleSize: number
  ): Promise<ProcessedData> {
    if (!(await this.ensureInitialized())) {
      throw new Error('Data processor not initialized');
    }

    const startTime = performance.now();
    
    try {
      // Validate input data
      if (!fileData || fileData.length === 0) {
        throw new Error('No file data provided');
      }

      if (!fileData[0].data || fileData[0].data.length === 0) {
        throw new Error('No data available in files');
      }

      let resultData: any[] = [];
      let resultColumns: string[] = [];

      console.log(`Processing workflow step: ${step.type}`, { step, fileDataLength: fileData.length });

      switch (step.type) {
        case 'column':
          // Select specific columns
          resultData = await this.processColumnSelection(step, fileData, sampleSize);
          resultColumns = step.target ? [step.source, step.target] : [step.source];
          break;

        case 'function':
          // Apply function transformation
          resultData = await this.processFunctionApplication(step, fileData, sampleSize);
          resultColumns = ['Input_Column', 'Output_Column'];
          break;

        case 'custom':
          // Custom value operation
          resultData = await this.processCustomOperation(step, sampleSize);
          resultColumns = ['Custom_Value', 'Row_Index'];
          break;

        case 'sheet':
          // Handle sheet selection
          resultData = await this.processSheetSelection(step, fileData, sampleSize);
          resultColumns = fileData[0]?.columns || [];
          break;

        default:
          // Default to showing source data
          resultData = await this.processDefaultView(step, fileData, sampleSize);
          resultColumns = fileData[0]?.columns || [];
      }

      const executionTime = performance.now() - startTime;
      const memoryUsage = this.estimateMemoryUsage(resultData);

      console.log(`Step processed successfully: ${resultData.length} rows, ${resultColumns.length} columns`);

      return {
        data: resultData,
        columns: resultColumns,
        rowCount: resultData.length,
        executionTime,
        memoryUsage,
        sampleSize: Math.min(sampleSize, resultData.length),
        stepIndex: 0 // Will be set by caller
      };

    } catch (error) {
      console.error('Error processing workflow step:', error);
      throw error;
    }
  }

  // Process column selection step
  private async processColumnSelection(
    step: WorkflowStep,
    fileData: FileData[],
    sampleSize: number
  ): Promise<any[]> {
    if (fileData.length === 0) return [];
    
    console.log(`Processing column selection: ${step.source} -> ${step.target || 'same'}`);
    console.log(`Step details:`, step);
    
    // Find the source file using columnReference if available
    let sourceFile: FileData | null = null;
    let actualColumnName = step.source;
    
    if (step.columnReference) {
      // Use the column reference to find the correct file
      sourceFile = fileData.find(file => file.name === step.columnReference!.fileName) || null;
      actualColumnName = step.columnReference.columnName;
      console.log(`Using column reference:`, step.columnReference);
      console.log(`Found source file:`, sourceFile?.name);
    } else {
      // Fallback: use first file (old behavior)
      sourceFile = fileData[0];
      console.log(`No column reference, using first file:`, sourceFile?.name);
    }
    
    if (!sourceFile || !sourceFile.data || sourceFile.data.length === 0) {
      console.warn(`No data found for source file: ${sourceFile?.name}`);
      return [];
    }
    
    const sourceData = sourceFile.data;
    const sampleData = sourceData.slice(0, sampleSize);
    
    console.log(`Processing ${sampleData.length} rows from file ${sourceFile.name}, column: ${actualColumnName}`);
    console.log(`Sample data keys:`, Object.keys(sampleData[0] || {}));
    
    return sampleData.map(row => {
      const newRow: any = {};
      
      if (actualColumnName in row) {
        newRow[step.source] = row[actualColumnName];
        if (step.target && step.target !== step.source) {
          newRow[step.target] = row[actualColumnName]; // Copy source to target
        }
        console.log(`Row data: ${actualColumnName} = ${row[actualColumnName]}`);
      } else {
        // Handle missing column gracefully
        console.warn(`Column "${actualColumnName}" not found in row:`, Object.keys(row));
        newRow[step.source] = `[Column not found: ${actualColumnName}]`;
        if (step.target) {
          newRow[step.target] = `[Column not found: ${actualColumnName}]`;
        }
      }
      return newRow;
    });
  }

  // Process function application step with enhanced formula support
  private async processFunctionApplication(
    step: WorkflowStep,
    fileData: FileData[],
    sampleSize: number
  ): Promise<any[]> {
    if (fileData.length === 0) return [];
    
    console.log(`Processing function application: ${step.source} with parameters:`, step.parameters);
    console.log(`Input file data:`, fileData[0]);
    
    // Get the function name and parameters
    const functionName = step.source.toUpperCase();
    const parameters = step.parameters || [];
    
    // Get the input data - this should be from the previous step
    const sourceData = fileData[0].data;
    const sampleData = sourceData.slice(0, sampleSize);
    
    console.log(`Function ${functionName} processing ${sampleData.length} rows with parameters:`, parameters);
    console.log(`Sample input data:`, sampleData.slice(0, 2));
    
    return sampleData.map((row, rowIndex) => {
      // For function steps, we need to determine which column to process
      // If parameters are provided, use the first parameter as the input column
      // Otherwise, try to use the first available column
      let inputColumn = parameters[0];
      if (!inputColumn) {
        // Fallback: use the first available column
        const availableColumns = Object.keys(row);
        inputColumn = availableColumns[0] || 'unknown';
        console.log(`No parameter specified, using first available column: ${inputColumn}`);
      }
      
      const inputValue = row[inputColumn] || '';
      let outputValue = inputValue;
      
      console.log(`Row ${rowIndex}: processing column "${inputColumn}" with value "${inputValue}"`);
      
      try {
        // Apply transformations based on function name
        switch (functionName) {
          case 'UPPER':
          case 'UPPERCASE':
            outputValue = String(inputValue).toUpperCase();
            break;
            
          case 'LOWER':
          case 'LOWERCASE':
            outputValue = String(inputValue).toLowerCase();
            break;
            
          case 'TRIM':
            outputValue = String(inputValue).trim();
            break;
            
          case 'TEXT_LENGTH':
          case 'LEN':
            outputValue = String(inputValue).length;
            break;
            
          case 'TITLE_CASE':
          case 'PROPER':
          case 'PROPER_CASE':
            outputValue = String(inputValue).replace(/\w\S*/g, (txt) => 
              txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
            );
            break;
            
          case 'REVERSE':
            outputValue = String(inputValue).split('').reverse().join('');
            break;
            
          case 'CAPITALIZE':
            outputValue = String(inputValue).charAt(0).toUpperCase() + String(inputValue).slice(1);
            break;
            
          case 'ADD':
          case 'ADD_VALUES':
            if (parameters.length >= 2) {
              const val1 = parseFloat(row[parameters[0]] || 0);
              const val2 = parseFloat(row[parameters[1]] || 0);
              outputValue = val1 + val2;
            }
            break;
            
          case 'SUBTRACT':
            if (parameters.length >= 2) {
              const val1 = parseFloat(row[parameters[0]] || 0);
              const val2 = parseFloat(row[parameters[1]] || 0);
              outputValue = val1 - val2;
            }
            break;
            
          case 'MULTIPLY':
            if (parameters.length >= 2) {
              const val1 = parseFloat(row[parameters[0]] || 0);
              const val2 = parseFloat(row[parameters[1]] || 0);
              outputValue = val1 * val2;
            }
            break;
            
          default:
            outputValue = `[Unknown function: ${functionName}]`;
        }
        
        console.log(`Row ${rowIndex}: ${functionName}("${inputValue}") = "${outputValue}"`);
        
        return {
          'Input_Column': inputValue,
          'Output_Column': outputValue
        };
        
      } catch (error) {
        console.error(`Error processing row ${rowIndex} with function ${functionName}:`, error);
        return {
          'Input_Column': inputValue,
          'Output_Column': `[Error: ${error}]`
        };
      }
    });
  }

  // Process custom operation step
  private async processCustomOperation(
    step: WorkflowStep,
    sampleSize: number
  ): Promise<any[]> {
    console.log(`Processing custom operation: ${step.source}`);
    
    const result = [];
    for (let i = 0; i < sampleSize; i++) {
      result.push({
        'Custom_Value': step.source,
        'Row_Index': i + 1
      });
    }
    return result;
  }

  // Process sheet selection step
  private async processSheetSelection(
    step: WorkflowStep,
    fileData: FileData[],
    sampleSize: number
  ): Promise<any[]> {
    if (fileData.length === 0) return [];
    
    const file = fileData[0];
    if (step.sheet && file.sheets && file.sheets[step.sheet]) {
      const sheetData = file.sheets[step.sheet];
      return sheetData.slice(0, sampleSize);
    }
    
    // Fallback to current sheet or main data
    return file.data.slice(0, sampleSize);
  }

  // Process default view (show source data)
  private async processDefaultView(
    step: WorkflowStep,
    fileData: FileData[],
    sampleSize: number
  ): Promise<any[]> {
    if (fileData.length === 0) return [];
    
    const sourceData = fileData[0].data;
    console.log(`Processing default view: showing ${Math.min(sampleSize, sourceData.length)} rows`);
    return sourceData.slice(0, sampleSize);
  }

  // Estimate memory usage of data
  private estimateMemoryUsage(data: any[]): number {
    if (data.length === 0) return 0;
    
    try {
      // Rough estimation: each row ~100 bytes + overhead
      const rowSize = JSON.stringify(data[0]).length;
      const totalSize = data.length * rowSize;
      return Math.round(totalSize / (1024 * 1024) * 100) / 100; // MB
    } catch (error) {
      console.warn('Could not estimate memory usage:', error);
      return 0;
    }
  }

  // Execute full workflow on complete dataset
  async executeFullWorkflow(
    workflowSteps: WorkflowStep[],
    fileData: FileData[]
  ): Promise<ProcessedData> {
    if (!(await this.ensureInitialized())) {
      throw new Error('Data processor not initialized');
    }

    const startTime = performance.now();
    
    try {
      console.log(`Executing full workflow with ${workflowSteps.length} steps`);
      
      // Process all steps sequentially
      let currentData = fileData[0]?.data || [];
      let currentColumns = fileData[0]?.columns || [];

      for (let i = 0; i < workflowSteps.length; i++) {
        const step = workflowSteps[i];
        console.log(`Processing step ${i + 1}/${workflowSteps.length}: ${step.type}`);
        
        // Process each step and update current data
        const stepResult = await this.processWorkflowStep(step, fileData, currentData.length);
        currentData = stepResult.data;
        currentColumns = stepResult.columns;
        
        // Update step status
        step.status = 'completed';
      }

      const executionTime = performance.now() - startTime;
      const memoryUsage = this.estimateMemoryUsage(currentData);

      console.log(`Full workflow completed: ${currentData.length} rows, ${executionTime.toFixed(2)}ms`);

      return {
        data: currentData,
        columns: currentColumns,
        rowCount: currentData.length,
        executionTime,
        memoryUsage,
        sampleSize: currentData.length,
        stepIndex: workflowSteps.length - 1
      };

    } catch (error) {
      console.error('Error executing full workflow:', error);
      throw error;
    }
  }

  // Clean up resources
  async cleanup() {
    try {
      // Clean up TensorFlow.js tensors if any
      tf.engine().endScope();
      this.isInitialized = false;
      console.log('Data processor cleaned up successfully');
    } catch (error) {
      console.warn('Error during cleanup:', error);
    }
  }
}

// Export singleton instance
export const dataProcessor = new DataProcessor();
