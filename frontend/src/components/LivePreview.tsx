import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent } from './ui/card';
import { Eye, Loader2, Info, AlertCircle, ChevronUp, ChevronDown, ArrowUp, ArrowDown } from 'lucide-react';
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
  
  // Scroll state and refs
  const [scrollPosition, setScrollPosition] = useState({ x: 0, y: 0 });
  const [canScrollUp, setCanScrollUp] = useState(false);
  const [canScrollDown, setCanScrollDown] = useState(false);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const tableContainerRef = useRef<HTMLDivElement>(null);
  const selectedColumnsTableRef = useRef<HTMLDivElement>(null);

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



  // Scroll utility functions
  const updateScrollState = useCallback((container: HTMLDivElement) => {
    const { scrollTop, scrollLeft, scrollHeight, scrollWidth, clientHeight, clientWidth } = container;
    
    setScrollPosition({ x: scrollLeft, y: scrollTop });
    setCanScrollUp(scrollTop > 0);
    setCanScrollDown(scrollTop < scrollHeight - clientHeight);
    setCanScrollLeft(scrollLeft > 0);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth);
  }, []);

  const scrollToTop = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      container.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, []);

  const scrollToBottom = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }
  }, []);

  const scrollUp = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      container.scrollBy({ top: -100, behavior: 'smooth' });
    }
  }, []);

  const scrollDown = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      container.scrollBy({ top: 100, behavior: 'smooth' });
    }
  }, []);

  const scrollLeft = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      container.scrollBy({ left: -100, behavior: 'smooth' });
    }
  }, []);

  const scrollRight = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      container.scrollBy({ left: 100, behavior: 'smooth' });
    }
  }, []);

  // Scroll position memory
  const saveScrollPosition = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      const scrollData = {
        x: container.scrollLeft,
        y: container.scrollTop,
        timestamp: Date.now()
      };
      sessionStorage.setItem('livePreviewScrollPosition', JSON.stringify(scrollData));
    }
  }, []);

  const restoreScrollPosition = useCallback(() => {
    const container = tableContainerRef.current || selectedColumnsTableRef.current;
    if (container) {
      const saved = sessionStorage.getItem('livePreviewScrollPosition');
      if (saved) {
        try {
          const scrollData = JSON.parse(saved);
          // Only restore if saved within last 5 minutes
          if (Date.now() - scrollData.timestamp < 300000) {
            container.scrollTo(scrollData.x, scrollData.y);
          }
        } catch (error) {
          console.warn('Failed to restore scroll position:', error);
        }
      }
    }
  }, []);

  // Save scroll position on unmount
  useEffect(() => {
    return () => {
      saveScrollPosition();
    };
  }, [saveScrollPosition]);

  // Restore scroll position when data changes
  useEffect(() => {
    if (currentPreview || selectedColumnsPreview) {
      // Small delay to ensure DOM is updated
      const timer = setTimeout(() => {
        restoreScrollPosition();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [currentPreview, selectedColumnsPreview, restoreScrollPosition]);

  // Keyboard shortcuts for scrolling
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Only handle if no input is focused
      if (document.activeElement?.tagName === 'INPUT' || document.activeElement?.tagName === 'TEXTAREA') {
        return;
      }

      const container = tableContainerRef.current || selectedColumnsTableRef.current;
      if (!container) return;

      switch (event.key) {
        case 'ArrowUp':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            scrollToTop();
          } else {
            event.preventDefault();
            scrollUp();
          }
          break;
        case 'ArrowDown':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            scrollToBottom();
          } else {
            event.preventDefault();
            scrollDown();
          }
          break;
        case 'ArrowLeft':
          event.preventDefault();
          scrollLeft();
          break;
        case 'ArrowRight':
          event.preventDefault();
          scrollRight();
          break;
        case 'Home':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            scrollToTop();
          }
          break;
        case 'End':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            scrollToBottom();
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [scrollToTop, scrollToBottom, scrollUp, scrollDown, scrollLeft, scrollRight]);

  // Refresh preview
  const handleRefresh = useCallback(() => {
    generateWorkflowPreview();
  }, [generateWorkflowPreview]);

  return (
    <>
      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e0;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #a0aec0;
        }
        .custom-scrollbar::-webkit-scrollbar-corner {
          background: #f1f5f9;
        }
      `}</style>
      <Card className="h-full">
        <CardContent className="p-4 h-full flex flex-col">
        {/* Header with Scroll Controls */}
        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-gray-600">
            {previewResultMode === 'step' ? 'Step-by-step results' : 'Final workflow results'}
          </p>
          
          {/* Scroll Controls */}
          <div className="flex items-center space-x-2">
            {/* Vertical Scroll Controls */}
            <div className="flex items-center space-x-1">
              <button
                onClick={scrollToTop}
                disabled={!canScrollUp}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Scroll to top"
              >
                <ArrowUp className="w-4 h-4" />
              </button>
              <button
                onClick={scrollUp}
                disabled={!canScrollUp}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Scroll up"
              >
                <ChevronUp className="w-4 h-4" />
              </button>
              <button
                onClick={scrollDown}
                disabled={!canScrollDown}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Scroll down"
              >
                <ChevronDown className="w-4 h-4" />
              </button>
              <button
                onClick={scrollToBottom}
                disabled={!canScrollDown}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Scroll to bottom"
              >
                <ArrowDown className="w-4 h-4" />
              </button>
            </div>
            
            {/* Horizontal Scroll Controls */}
            <div className="flex items-center space-x-1">
              <button
                onClick={scrollLeft}
                disabled={!canScrollLeft}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Scroll left"
              >
                <ChevronUp className="w-4 h-4 rotate-90" />
              </button>
              <button
                onClick={scrollRight}
                disabled={!canScrollRight}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Scroll right"
              >
                <ChevronDown className="w-4 h-4 rotate-90" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Scroll Position Indicator */}
        {(canScrollUp || canScrollDown || canScrollLeft || canScrollRight) && (
          <div className="mb-2 text-xs text-gray-500 flex items-center justify-between">
            <span>
              Scroll: {scrollPosition.y > 0 ? `↓ ${Math.round(scrollPosition.y)}px` : 'Top'} 
              {scrollPosition.x > 0 && ` | → ${Math.round(scrollPosition.x)}px`}
            </span>
            <span className="text-gray-400">
              Use controls, mouse wheel, or arrow keys (Ctrl+↑/↓ for top/bottom)
            </span>
          </div>
        )}

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
                <div className="flex-1 border border-gray-200 rounded-lg">
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
                  
                  <div 
                    ref={selectedColumnsTableRef}
                    className="overflow-auto max-h-96 custom-scrollbar"
                    onScroll={(e) => updateScrollState(e.currentTarget)}
                    style={{
                      scrollbarWidth: 'thin',
                      scrollbarColor: '#cbd5e0 #f7fafc'
                    }}
                  >
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50 sticky top-0 z-10">
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
                <div className="flex-1 border border-gray-200 rounded-lg">
                  {/* Debug Info */}
                  <div className="bg-yellow-50 p-2 text-xs text-yellow-800 border-b border-yellow-200">
                    <strong>Debug:</strong> Columns: {JSON.stringify(currentPreview.columns)} | 
                    First row: {JSON.stringify(currentPreview.data[0])} | 
                    Note: This is workflow step preview, not live column preview
                  </div>
                  
                  <div 
                    ref={tableContainerRef}
                    className="overflow-auto max-h-96 custom-scrollbar"
                    onScroll={(e) => updateScrollState(e.currentTarget)}
                    style={{
                      scrollbarWidth: 'thin',
                      scrollbarColor: '#cbd5e0 #f7fafc'
                    }}
                  >
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50 sticky top-0 z-10">
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
    </>
  );
};

export default LivePreview;
