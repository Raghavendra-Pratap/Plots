import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from './ui/card';
import { Eye, Loader2, Info, AlertCircle } from 'lucide-react';
import { dataProcessor, ProcessedData, WorkflowStep, FileData } from '../utils/dataProcessor';

interface LivePreviewProps {
  workflowSteps: WorkflowStep[];
  importedFiles: any[];
  sampleSize: number;
  isExecuting: boolean;
  previewResultMode: 'step' | 'final';
  onPreviewResultModeChange: (mode: 'step' | 'final') => void;
  currentStepIndex: number;
  selectedColumnsPreview?: {
    columns: string[];
    data: any[];
    sourceFile: string;
    rowCount: number;
  } | null;
}

const LivePreview: React.FC<LivePreviewProps> = ({
  workflowSteps,
  importedFiles,
  sampleSize,
  isExecuting,
  previewResultMode,
  onPreviewResultModeChange,
  currentStepIndex,
  selectedColumnsPreview
}) => {
  const [previewResults, setPreviewResults] = useState<ProcessedData[]>([]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  // Generate preview data for a specific step using data processor
  const generateStepPreview = useCallback(async (stepIndex: number, previousStepData?: any[]): Promise<ProcessedData> => {
    try {
      const step = workflowSteps[stepIndex];
      
      // Convert importedFiles to FileData format for data processor
      const fileData: FileData[] = importedFiles.map(file => ({
        name: file.name,
        type: file.type,
        data: file.data || [],
        columns: file.columns || [],
        sheets: file.sheets,
        currentSheet: file.currentSheet
      }));
      
      console.log(`Generating preview for step ${stepIndex + 1}:`, { step, fileDataLength: fileData.length, hasPreviousData: !!previousStepData });
      
      // If this is a function step and we have previous step data, use that instead of file data
      let inputData: FileData[] = fileData;
      if (step.type === 'function' && previousStepData && previousStepData.length > 0) {
        // Create a virtual file with the previous step's output data
        inputData = [{
          name: `step_${stepIndex - 1}_output`,
          type: 'workflow_step',
          data: previousStepData,
          columns: Object.keys(previousStepData[0] || {}),
          sheets: {},
          currentSheet: undefined
        }];
        console.log(`Function step using previous step data:`, inputData);
      }
      
      // Process the step using data processor
      const result = await dataProcessor.processWorkflowStep(step, inputData, sampleSize);
      
      // Update the step index
      result.stepIndex = stepIndex;
      
      return result;
    } catch (error) {
      console.error(`Error generating preview for step ${stepIndex + 1}:`, error);
      throw new Error(`Failed to generate preview for step ${stepIndex + 1}: ${error}`);
    }
  }, [workflowSteps, importedFiles, sampleSize]);

  // Generate preview for all steps up to a specific point
  const generateWorkflowPreview = useCallback(async () => {
    if (workflowSteps.length === 0) return;
    
    setIsPreviewLoading(true);
    setPreviewError(null);
    
    try {
      console.log('Generating workflow preview...', { workflowSteps, sampleSize });
      
      const results: ProcessedData[] = [];
      let previousStepData: any[] = [];
      
      // Generate preview for each step, passing previous step's output
      for (let i = 0; i < workflowSteps.length; i++) {
        const result = await generateStepPreview(i, previousStepData);
        results.push(result);
        
        // Store this step's output for the next step
        previousStepData = result.data;
        console.log(`Step ${i + 1} completed, output data:`, result.data.slice(0, 2));
      }
      
      setPreviewResults(results);
      
      console.log('Workflow preview generated successfully:', results);
    } catch (error) {
      console.error('Error generating workflow preview:', error);
      setPreviewError(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      setIsPreviewLoading(false);
    }
  }, [workflowSteps, sampleSize, generateStepPreview]);

  // Auto-generate preview when workflow steps change
  useEffect(() => {
    if (workflowSteps.length > 0) {
      generateWorkflowPreview();
    } else {
      setPreviewResults([]);
    }
  }, [workflowSteps, sampleSize, generateWorkflowPreview]);

  // Get current preview result
  const currentPreview = currentStepIndex >= 0 && currentStepIndex < previewResults.length 
    ? previewResults[currentStepIndex] 
    : null;



  // Refresh preview
  const handleRefresh = useCallback(() => {
    generateWorkflowPreview();
  }, [generateWorkflowPreview]);

  return (
    <Card className="h-full">
      <CardContent className="p-4 h-full flex flex-col">
        {/* Simple Header - Controls are in main Playground header */}
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            {previewResultMode === 'step' ? 'Step-by-step results' : 'Final workflow results'}
          </p>
        </div>

        {/* Error Display */}
        {previewError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2 text-red-700">
              <AlertCircle className="w-4 h-4" />
              <span className="font-medium">Preview Error:</span>
              <span>{previewError}</span>
            </div>
            <button
              onClick={handleRefresh}
              className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          {workflowSteps.length === 0 ? (
            // Empty State
            <div className="h-full flex flex-col items-center justify-center text-gray-500">
              <Eye className="w-16 h-16 mb-4 text-gray-300" />
              <h3 className="text-lg font-medium mb-2">No Workflow to Preview</h3>
              <p className="text-sm text-center">
                Build a workflow in the Workflow Builder to see live previews here
              </p>
            </div>
          ) : isPreviewLoading ? (
            // Loading State
            <div className="h-full flex flex-col items-center justify-center">
              <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
              <p className="text-gray-600">Generating preview...</p>
            </div>
          ) : (
            // Preview Content
            <div className="h-full flex flex-col">

              {/* Data Preview Table */}
              {selectedColumnsPreview && selectedColumnsPreview.data && selectedColumnsPreview.data.length > 0 ? (
                // Selected Columns Live Preview
                <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
                  <div className="bg-blue-50 p-3 border-b border-blue-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-semibold text-blue-800">
                          Live Preview - Selected Columns
                        </h3>
                        <p className="text-xs text-blue-600 mt-1">
                          Source: {selectedColumnsPreview.sourceFile} | 
                          Columns: {selectedColumnsPreview.columns.join(', ')} | 
                          Showing first {sampleSize} rows
                        </p>
                        {/* Debug info for column mapping */}
                        <div className="text-xs text-blue-500 mt-1">
                          Debug: {selectedColumnsPreview.data.length > 0 ? 
                            `First row keys: ${Object.keys(selectedColumnsPreview.data[0]).join(', ')}` : 
                            'No data available'
                          }
                        </div>
                      </div>
                      <div className="text-xs text-blue-600">
                        Total: {selectedColumnsPreview.rowCount} rows
                      </div>
                    </div>
                  </div>
                  
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          {selectedColumnsPreview.columns.map((column: string, index: number) => (
                            <th
                              key={index}
                              className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {column}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {selectedColumnsPreview.data.map((row: any, rowIndex: number) => (
                          <tr key={rowIndex} className="hover:bg-gray-50">
                            {selectedColumnsPreview.columns.map((column: string, colIndex: number) => {
                              const cellValue = row[column];
                              const displayValue = cellValue !== undefined && cellValue !== null 
                                ? String(cellValue) 
                                : '';
                              
                              return (
                                <td
                                  key={colIndex}
                                  className="px-3 py-2 text-sm text-gray-900 max-w-xs truncate"
                                  title={displayValue}
                                >
                                  {displayValue}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : currentPreview && currentPreview.data && currentPreview.data.length > 0 ? (
                // Workflow Step Preview (existing functionality)
                <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
                  {/* Debug Info */}
                  <div className="bg-yellow-50 p-2 text-xs text-yellow-800 border-b border-yellow-200">
                    <strong>Debug:</strong> Columns: {JSON.stringify(currentPreview.columns)} | 
                    First row: {JSON.stringify(currentPreview.data[0])} | 
                    Note: This is workflow step preview, not live column preview
                  </div>
                  
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          {currentPreview.columns.map((column: string, index: number) => (
                            <th
                              key={index}
                              className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {column}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {currentPreview.data.map((row: any, rowIndex: number) => {
                          try {
                            return (
                              <tr key={rowIndex} className="hover:bg-gray-50">
                                {currentPreview.columns.map((column: string, colIndex: number) => {
                                  try {
                                    const cellValue = row[column];
                                    const displayValue = cellValue !== undefined && cellValue !== null 
                                      ? String(cellValue) 
                                      : '';
                                    
                                    return (
                                      <td
                                        key={colIndex}
                                        className="px-3 py-2 text-sm text-gray-900 max-w-xs truncate"
                                        title={displayValue}
                                      >
                                        {displayValue}
                                      </td>
                                    );
                                  } catch (cellError) {
                                    console.error(`Error rendering cell at row ${rowIndex}, col ${colIndex}:`, cellError, { row, column });
                                    return (
                                      <td
                                        key={colIndex}
                                        className="px-3 py-2 text-sm text-red-600 max-w-xs"
                                        title="Error rendering cell"
                                      >
                                        [Error]
                                      </td>
                                    );
                                  }
                                })}
                              </tr>
                            );
                          } catch (rowError) {
                            console.error(`Error rendering row ${rowIndex}:`, rowError, { row: currentPreview.data[rowIndex] });
                            return (
                              <tr key={rowIndex} className="hover:bg-gray-50 bg-red-50">
                                <td colSpan={currentPreview.columns.length} className="px-3 py-2 text-sm text-red-600">
                                  Error rendering row: {rowError instanceof Error ? rowError.message : 'Unknown error'}
                                </td>
                              </tr>
                            );
                          }
                        })}
                      </tbody>
                    </table>
                  </div>
                  
                  {/* Preview Info */}
                  <div className="bg-gray-50 px-3 py-2 border-t border-gray-200">
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <span>
                        Showing {currentPreview.data.length} of {currentPreview.rowCount} rows 
                        (Sample size: {currentPreview.sampleSize})
                      </span>
                      <span>
                        {currentPreview.executionTime.toFixed(2)}ms • {currentPreview.memoryUsage.toFixed(2)}MB
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                // No Data State
                <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                  <Info className="w-16 h-16 mb-4 text-gray-300" />
                  <h3 className="text-lg font-medium mb-2">No Preview Data</h3>
                  <p className="text-sm text-center">
                    {previewError 
                      ? 'Error occurred while generating preview'
                      : selectedColumnsPreview 
                        ? 'Select columns from Data Sources to see live preview'
                        : 'No data available for the selected step'
                    }
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default LivePreview;
