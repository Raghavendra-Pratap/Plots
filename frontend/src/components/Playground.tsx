import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent } from './ui/card';
import DataSources from './DataSources';
import LivePreview from './LivePreview';
import { useNavigate } from 'react-router-dom';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { dataProcessor } from '../utils/dataProcessor';
// @ts-ignore
import Papa from 'papaparse';
import SaveWorkflowDialog, { WorkflowTemplate } from './SaveWorkflowDialog';
import ExecuteWorkflowDialog, { ExecuteWorkflowTemplate } from './ExecuteWorkflowDialog';
import { formulaService, FormulaDefinition } from '../utils/formulaService';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { backendService, BackendWorkflowRequest } from '../services/BackendService';
import ErrorBoundary from './ErrorBoundary';
import { 
  FileText, 
  File, 
  Upload, 
  Eye,
  CheckCircle,
  Trash2,
  ArrowLeft,
  Code,
  Search,
  ChevronDown,
  ChevronRight,
  Grid3X3,
  List,
  Star,
  ArrowUpDown,
  Undo2,
  Redo2,
  Link,
  Plus,
  Type,
  X,
  MoreHorizontal,
  Edit3,
  RefreshCw,
  Download,
  Play,
  Save
} from 'lucide-react';
import * as XLSX from 'xlsx';
import { useBackendStatus } from '../hooks/useBackendStatus';

// Types for Playground
interface FileData {
  name: string;
  type: string;
  size: number;
  columns: string[];
  sheets?: { [sheetName: string]: string[] };
  headerConfig?: {
    row: number; // Which row to use as headers (1-based)
    merged: boolean; // Whether headers are merged across columns
    customHeaders?: string[]; // Custom header names
    autoDetected: boolean; // Whether headers were auto-detected
  };
}

// Column Reference for proper file/column mapping
interface ColumnReference {
  displayName: string;        // "12474.csv ▸ Store" (UI display)
  columnName: string;         // "Store" (actual column name)
  fileName: string;           // "12474.csv" (file identifier)
  sheetName?: string;         // "Sheet1" (for Excel files)
  fullPath: string;           // "12474.csv ▸ Store" or "12474.csv ▸ Sheet1 ▸ Store"
}

interface PlaygroundFile extends FileData {
  executionStatus?: 'pending' | 'processing' | 'completed' | 'failed';
  lastProcessed?: Date;
  currentSheet?: string; // For header configuration at sheet level
  data?: any[]; // Actual file data for processing
}

// Formula interface for enhanced management with alias mapping
// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface Formula {
  name: string;
  category: string;
  description: string;
  usageCount: number;
  isFavorite: boolean;
  syntax: string;
  isAlias?: boolean; // Indicates if this is an alias function
  primaryFunction?: string; // The primary function this alias maps to
  aliases?: string[]; // List of aliases for this function (if it's a primary function)
}

interface PlaygroundProps {
  isEmbedded?: boolean;
  onBack?: () => void;
}

const Playground: React.FC<PlaygroundProps> = ({ isEmbedded = false, onBack }) => {
  const [importedFiles, setImportedFiles] = useState<PlaygroundFile[]>([]);
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);
  const [collapsedSheets, setCollapsedSheets] = useState<{ [key: string]: boolean }>({});

  
  // Workflow Builder State
  const [workflowSteps, setWorkflowSteps] = useState<Array<{
    id: string;
    type: 'column' | 'function' | 'break' | 'custom' | 'sheet';
    source: string;
    target?: string;
    sheet?: string;
    parameters?: string[];
    status: 'pending' | 'processing' | 'completed' | 'failed';
    columnReference?: ColumnReference; // For column steps
  }>>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isWorkflowStarted, setIsWorkflowStarted] = useState(false);

  
  // Enhanced workflow state for interactive building
  const [activeFunction, setActiveFunction] = useState<string | null>(null);
  const [functionParameters, setFunctionParameters] = useState<string[]>([]);
  const [isFunctionOpen, setIsFunctionOpen] = useState(false);

  // Enhanced Formula Engine State
  const [formulaSearchTerm, setFormulaSearchTerm] = useState('');
  const [formulaViewMode, setFormulaViewMode] = useState<'normal' | 'categories' | 'favorites'>('categories');
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  const [formulaSortBy, setFormulaSortBy] = useState<'name' | 'category' | 'usage'>('name');
  const [favoriteFormulas, setFavoriteFormulas] = useState<string[]>([]);

  // File Selection State (matching AppLayout)
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]); // Track selected files
  
  // Text wrapping state for file and sheet names
  const [textWrapEnabled, setTextWrapEnabled] = useState(false); // Default to disabled to save space
  
  // Preview mode state (icon-based toggle instead of tabs)
  const [previewMode, setPreviewMode] = useState<'structure' | 'live'>('structure');
  
  // Live Preview state
  const [sampleSize, setSampleSize] = useState<10 | 50 | 100>(50);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [previewResultMode, setPreviewResultMode] = useState<'step' | 'final'>('step');
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  
  // Enhanced Execute state
  const [executionProgress, setExecutionProgress] = useState(0);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [executionStatus, setExecutionStatus] = useState<'idle' | 'preparing' | 'processing' | 'completed' | 'cancelled' | 'error'>('idle');
  const [executionResults, setExecutionResults] = useState<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [canCancelExecution, setCanCancelExecution] = useState(false);
  
  // Backend integration state - using the hook
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { status: backendStatus, isConnected: backendConnected, checkHealth } = useBackendStatus();
  
  // Live Preview State for Selected Columns
  const [selectedColumnsPreview, setSelectedColumnsPreview] = useState<{
    columns: string[];
    data: any[];
    sourceFile: string;
    rowCount: number;
  } | null>(null);
  
  // Save Workflow Dialog state
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showExecuteDialog, setShowExecuteDialog] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [savedTemplates, setSavedTemplates] = useState<WorkflowTemplate[]>([]);
  const [workflowName, setWorkflowName] = useState('Untitled Workflow');
  
  // Header configuration state (matching AppLayout)
  const [showHeaderConfig, setShowHeaderConfig] = useState(false);
  const [selectedFileForHeader, setSelectedFileForHeader] = useState<PlaygroundFile | null>(null);
  const [headerRow, setHeaderRow] = useState(1);
  const [isMergedHeaders, setIsMergedHeaders] = useState(false);
  const [customHeaders, setCustomHeaders] = useState<string[]>([]);

  // Workflow Builder Enhanced State
  const [workflowMode, setWorkflowMode] = useState<'column' | 'sheet'>('column');
  const [customInput, setCustomInput] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [showNewDropdown, setShowNewDropdown] = useState(false);
  const [newColumnInput, setNewColumnInput] = useState('');
  const [newFileInput, setNewFileInput] = useState('');
  const [showNewColumnInput, setShowNewColumnInput] = useState(false);
  const [showNewFileInput, setShowNewFileInput] = useState(false);
  const [showSearchBar, setShowSearchBar] = useState(false);
  const [showSortDropdown, setShowSortDropdown] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [workflowScrollTop, setWorkflowScrollTop] = useState(0);

  const [isExecuting, setIsExecuting] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Replace hardcoded formulas with formula service
  const [allFormulas, setAllFormulas] = useState<FormulaDefinition[]>([]);

  // Initialize formulas from service
  useEffect(() => {
    const formulas = formulaService.getAllFormulas();
    setAllFormulas(formulas);
    
    // Initialize expanded categories
    const categories = formulaService.getFormulasByCategory();
    const expanded: Record<string, boolean> = {};
    Object.keys(categories).forEach(category => {
      expanded[category] = true; // Start with all categories expanded
    });
    setExpandedCategories(expanded);
  }, []);

  // Check backend connectivity on mount and periodically
  useEffect(() => {
    const checkBackend = async () => {
      try {
        await checkHealth();
      } catch (error) {
        console.error('Backend health check failed:', error);
      }
    };

    // Check immediately
    checkBackend();
    
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    
    return () => clearInterval(interval);
  }, [checkHealth]);

  // Helper function to parse column path and create ColumnReference
  const parseColumnPath = (columnPath: string, file: PlaygroundFile): ColumnReference => {
    const parts = columnPath.split(' ▸ ');
    
    if (parts.length === 2) {
      // CSV format: "filename.csv ▸ column_name"
      return {
        displayName: columnPath,
        columnName: parts[1],
        fileName: parts[0],
        fullPath: columnPath
      };
    } else if (parts.length === 3) {
      // Excel format: "filename.xlsx ▸ Sheet1 ▸ column_name"
      return {
        displayName: columnPath,
        columnName: parts[2],
        fileName: parts[0],
        sheetName: parts[1],
        fullPath: columnPath
      };
    } else {
      // Fallback: treat as single column name
      return {
        displayName: columnPath,
        columnName: columnPath,
        fileName: file.name,
        fullPath: columnPath
      };
    }
  };

  // Generate live preview data for selected columns
  const generateSelectedColumnsPreview = useCallback(() => {
    if (selectedColumns.length === 0 || importedFiles.length === 0) {
      setSelectedColumnsPreview(null);
      return;
    }

    try {
      console.log('Generating preview for selected columns:', selectedColumns);
      console.log('Available files:', importedFiles.map(f => ({ name: f.name, columns: f.columns, dataLength: f.data?.length })));

      // Parse column paths to get proper references
      const columnReferences = selectedColumns.map(colPath => {
        // Find the file that contains this column by checking the file name in the path
        const sourceFile = importedFiles.find(file => colPath.startsWith(file.name));
        
        if (sourceFile) {
          const columnRef = parseColumnPath(colPath, sourceFile);
          console.log(`Column path "${colPath}" parsed to:`, columnRef);
          return columnRef;
        }
        
        console.warn(`Could not find source file for column path: ${colPath}`);
        return null;
      }).filter(Boolean) as ColumnReference[];

      console.log('Parsed column references:', columnReferences);

      if (columnReferences.length === 0) {
        console.log('No valid column references found');
        setSelectedColumnsPreview(null);
        return;
      }

      // Group columns by file for processing
      const columnsByFile = new Map<string, { file: PlaygroundFile, columns: string[] }>();
      
      columnReferences.forEach(ref => {
        const key = ref.sheetName ? `${ref.fileName}::${ref.sheetName}` : ref.fileName;
        if (!columnsByFile.has(key)) {
          const sourceFile = importedFiles.find(f => f.name === ref.fileName);
          if (sourceFile) {
            columnsByFile.set(key, { file: sourceFile, columns: [] });
          }
        }
        const fileGroup = columnsByFile.get(key);
        if (fileGroup) {
          fileGroup.columns.push(ref.columnName);
        }
      });

      console.log('Columns grouped by file:', columnsByFile);

      // Generate preview data for each file
      let allPreviewData: any[] = [];
      let allColumns: string[] = [];
      
      columnsByFile.forEach(({ file, columns }, key) => {
        if (!file.data || file.data.length === 0) {
          console.warn(`No data found for file: ${file.name}`);
          return;
        }

        console.log(`Processing file ${file.name} with columns:`, columns);
        console.log(`File data sample:`, file.data.slice(0, 2));
        console.log(`Available data keys:`, Object.keys(file.data[0] || {}));

        const fileData = file.data.slice(0, sampleSize);
        
        if (allPreviewData.length === 0) {
          // First file - use its row count
          allPreviewData = fileData.map(row => ({})); // Create empty objects
        } else {
          // Subsequent files - ensure same row count
          allPreviewData = allPreviewData.slice(0, fileData.length);
        }

        // Add columns from this file
        columns.forEach(col => {
          if (!allColumns.includes(col)) {
            allColumns.push(col);
          }
          
          // Map data for this column
          allPreviewData.forEach((row, index) => {
            if (fileData[index] && fileData[index][col] !== undefined) {
              row[col] = fileData[index][col];
            } else {
              console.warn(`Column "${col}" not found in row ${index} of file ${file.name}`);
              row[col] = `[Data not available]`;
            }
          });
        });
      });

      if (allPreviewData.length === 0) {
        console.log('No preview data generated');
        setSelectedColumnsPreview(null);
        return;
      }

      console.log('Final preview data:', {
        columns: allColumns,
        dataCount: allPreviewData.length,
        firstRow: allPreviewData[0],
        firstRowKeys: Object.keys(allPreviewData[0] || {})
      });

      setSelectedColumnsPreview({
        columns: allColumns,
        data: allPreviewData,
        sourceFile: Array.from(columnsByFile.keys()).join(', '),
        rowCount: allPreviewData.length
      });

    } catch (error) {
      console.error('Error generating selected columns preview:', error);
      setSelectedColumnsPreview(null);
    }
  }, [selectedColumns, importedFiles, sampleSize]);

  // Convert workflow steps to backend format
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const convertWorkflowStepsToBackend = (steps: typeof workflowSteps) => {
    return steps.map(step => {
      if (step.type === 'column' && step.columnReference) {
        return {
          type: 'column',
          source: step.columnReference.columnName,
          fileName: step.columnReference.fileName,
          sheetName: step.columnReference.sheetName,
          displayPath: step.columnReference.displayName
        };
      } else if (step.type === 'function') {
        return {
          type: 'function',
          functionName: step.source,
          parameters: step.parameters || [],
          dependencies: [] // Will be populated based on workflow order
        };
      }
      return step;
    });
  };

  // Update live preview when selection changes
  useEffect(() => {
    generateSelectedColumnsPreview();
  }, [selectedColumns, importedFiles, sampleSize, generateSelectedColumnsPreview]);

  // Helper functions for formula management
  const getFilteredFormulas = () => {
    let filtered = allFormulas;
    
    // Apply search filter
    if (formulaSearchTerm) {
      filtered = formulaService.searchFormulas(formulaSearchTerm);
    }
    
    // Apply sorting
    switch (formulaSortBy) {
      case 'name':
        filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'category':
        filtered = [...filtered].sort((a, b) => a.category.localeCompare(b.category));
        break;
      case 'usage':
        // For now, sort by name since we don't have usage tracking yet
        filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name));
        break;
    }
    
    return filtered;
  };





  const getFormulasByCategory = () => {
    return formulaService.getFormulasByCategory();
  };

  const getEnhancedFunctionDisplay = (formula: FormulaDefinition) => {
    return (
      <div className="flex items-center space-x-2">
        <span className="font-medium">{formula.name}</span>
        {formula.aliases && Array.isArray(formula.aliases) && formula.aliases.length > 0 && (
          <span className="text-blue-600 text-xs font-medium">
            {formula.aliases[0]}
          </span>
        )}
      </div>
    );
  };

  const toggleCategoryExpansion = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const toggleFavorite = (formulaName: string) => {
    setFavoriteFormulas(prev => {
      if (prev.includes(formulaName)) {
        return prev.filter(name => name !== formulaName);
      } else {
        return [...prev, formulaName];
      }
    });
  };

  // Function click handler - now integrated with formula service
  const handleFunctionClick = (functionName: string) => {
    const formula = formulaService.getFormula(functionName);
    if (!formula) {
      console.error('Formula not found:', functionName);
      return;
    }

    setActiveFunction(functionName);
    setFunctionParameters([]);
    setIsFunctionOpen(true);
    
    // Add function step to workflow
    addWorkflowStep({
      type: 'function',
      source: functionName,
      parameters: []
    });

    // Auto-scroll to show the new function step
      setTimeout(() => {
        scrollWorkflowToBottom();
      }, 100);
  };

  // Complete function with parameters - now validates using formula service
  const completeFunction = () => {
    if (activeFunction && functionParameters.length > 0) {
      // Validate formula using service
      const validation = formulaService.validateFormula(activeFunction, functionParameters);
      if (!validation.isValid) {
        alert(`Formula validation failed: ${validation.errors.join(', ')}`);
        return;
      }

      // Update the last function step with parameters
      setWorkflowSteps(prev => {
        const newSteps = [...prev];
        const lastStep = newSteps[newSteps.length - 1];
        if (lastStep && lastStep.type === 'function') {
          lastStep.parameters = functionParameters;
        }
        return newSteps;
      });
      
      // Reset function state
      setActiveFunction(null);
      setFunctionParameters([]);
      setIsFunctionOpen(false);

      // Auto-scroll to show the completed function step
      setTimeout(() => {
        scrollWorkflowToBottom();
      }, 100);
    }
  };

  // Generate workflow preview for live preview mode
  const generateWorkflowPreview = async () => {
    if (workflowSteps.length === 0) return;
    
    setIsPreviewLoading(true);
    
    try {
      // Simulate preview generation
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // For now, just simulate loading
      // In real implementation, this would use data processor to process sample data
      console.log(`Generating preview for ${workflowSteps.length} steps with ${sampleSize} rows`);
        
      } catch (error) {
      console.error('Preview generation failed:', error);
      } finally {
      setIsPreviewLoading(false);
    }
  };

  // Add workflow step function
  const addWorkflowStep = (step: {
    type: 'column' | 'function' | 'break' | 'custom' | 'sheet';
    source: string;
    target?: string;
    sheet?: string;
    parameters?: string[];
    columnReference?: ColumnReference;
  }) => {
    const newStep = {
      id: `step_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ...step,
      status: 'pending' as const
    };
    
    setWorkflowSteps(prev => [...prev, newStep]);
  };

  // Remove workflow step function
  const removeWorkflowStep = (stepId: string) => {
    setWorkflowSteps(prev => prev.filter(step => step.id !== stepId));
  };

  // Clear all workflow steps
  const clearWorkflow = () => {
    setWorkflowSteps([]);
  };

  // Scroll to bottom of workflow
  const scrollWorkflowToBottom = () => {
    // Implementation for scrolling to bottom
    console.log('Scrolling to bottom of workflow');
  };

  // Handle Enter key for function completion
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && isFunctionOpen && activeFunction) {
      e.preventDefault();
      completeFunction();
    }
  };

  // Helper functions
  const getTruncatedFileName = (fileName: string, maxLength: number): string => {
    if (fileName.length <= maxLength) return fileName;
    const extension = fileName.split('.').pop();
    const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
    const truncatedName = nameWithoutExt.substring(0, maxLength - 3);
    return `${truncatedName}...${extension ? `.${extension}` : ''}`;
  };

  const toggleSheetCollapse = (fileKey: string) => {
    setCollapsedSheets(prev => ({
      ...prev,
      [fileKey]: !prev[fileKey]
    }));
  };

  const handleHeaderConfig = (file: PlaygroundFile, sheetName?: string) => {
    // Implementation for header configuration
    console.log('Header config for:', file.name, sheetName);
  };

  const handleColumnClick = (column: string, file: PlaygroundFile) => {
    // Create proper column reference
    const columnRef = parseColumnPath(column, file);
    
    console.log('Column clicked:', {
      displayPath: column,
      columnReference: columnRef
    });

    // Check if we're in function mode (function is open and needs parameters)
    if (isFunctionOpen && activeFunction) {
      // Add column as a parameter to the active function
      setFunctionParameters(prev => [...prev, column]);
      console.log(`Added column "${column}" as parameter for function "${activeFunction}"`);
    } else {
      // Add column selection to workflow as a new step
      addWorkflowStep({
        type: 'column',
        source: columnRef.columnName, // Use actual column name for data processing
        target: columnRef.columnName, // Use actual column name for target
        sheet: columnRef.sheetName, // Include sheet info for Excel files
        columnReference: columnRef // Store full reference for UI display
      });
      console.log(`Added column step:`, {
        displayPath: column,
        columnName: columnRef.columnName,
        fileName: columnRef.fileName,
        sheetName: columnRef.sheetName,
        source: columnRef.columnName, // This is what dataProcessor will use
        target: columnRef.columnName
      });
    }
    
    // Generate live preview for selected columns
    setTimeout(() => {
      generateSelectedColumnsPreview();
    }, 100);
  };

  const handleFileClick = (file: PlaygroundFile) => {
    // Handle file selection
    console.log('File clicked:', file.name);
  };

  // Workflow management functions
  const loadWorkflow = () => {
    // Implementation for loading workflow
    console.log('Loading workflow...');
  };

  const saveWorkflow = () => {
    // Open the Save Workflow Dialog
    if (workflowSteps.length > 0) {
      setShowSaveDialog(true);
    }
  };

  const executeWorkflowWithDialog = () => {
    // Open the Execute Workflow Dialog
    if (workflowSteps.length > 0) {
      setShowExecuteDialog(true);
    }
  };

  const cancelExecution = () => {
    // Implementation for canceling execution
    console.log('Canceling execution...');
  };

  const exportExecutionResults = (results: any) => {
    // Implementation for exporting results
    console.log('Exporting results:', results);
  };

  // Step Navigation Functions
  const goToPreviousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
    }
  };

  const goToNextStep = () => {
    if (currentStepIndex < workflowSteps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
    }
  };

  const handleBrowseFiles = () => {
    // Trigger the hidden file input
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileImport = async (files: FileList) => {
    console.log('Importing files:', files);
    
    try {
      const newFiles: PlaygroundFile[] = [];
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        console.log(`Processing file: ${file.name}, type: ${file.type}`);
        
        let fileData: PlaygroundFile = {
        name: file.name,
        type: file.type || 'unknown',
        size: file.size,
        columns: [],
        sheets: {},
        headerConfig: {
          row: 1,
          merged: false,
          autoDetected: true
          },
          data: [],
          currentSheet: undefined
      };

        // Process different file types
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        // Handle CSV files
          const text = await file.text();
          const parsed = Papa.parse(text, {
            header: true,
            skipEmptyLines: true,
            dynamicTyping: false
          });
          
          if (parsed.errors.length > 0) {
            console.warn('CSV parsing warnings:', parsed.errors);
          }
          
          fileData.columns = parsed.meta.fields || [];
          fileData.data = parsed.data as any[];
          fileData.type = 'text/csv';
          
          console.log(`CSV processed: ${fileData.columns.length} columns, ${fileData.data.length} rows`);
          
        } else if (file.type.includes('excel') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
          // Handle Excel files using xlsx library
          try {
            const arrayBuffer = await file.arrayBuffer();
            const workbook = XLSX.read(arrayBuffer, { type: 'array' });
            
            // Extract sheet names and data
            const sheetNames = workbook.SheetNames;
            const sheets: { [sheetName: string]: string[] } = {};
            let allColumns: string[] = [];
            let allData: any[] = [];
            
            console.log(`Excel file has ${sheetNames.length} sheets:`, sheetNames);
            
            // Process each sheet
            sheetNames.forEach(sheetName => {
              const worksheet = workbook.Sheets[sheetName];
              const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
              
              if (jsonData.length > 0) {
                // First row contains headers
                const headers = jsonData[0] as string[];
                const sheetColumns = headers.filter(header => header && header.trim() !== '');
                
                // Store columns for this sheet
                sheets[sheetName] = sheetColumns;
                
                // Add to all columns (avoid duplicates)
                sheetColumns.forEach(col => {
                  if (!allColumns.includes(col)) {
                    allColumns.push(col);
                  }
                });
                
                // Convert to object format for data processing
                const sheetData = jsonData.slice(1).map((row: any) => {
                  const rowObj: any = {};
                  headers.forEach((header, index) => {
                    if (header && header.trim() !== '') {
                      rowObj[header] = (row as any[])[index] || '';
                    }
                  });
                  return rowObj;
                }).filter(row => Object.keys(row).some(key => row[key] !== ''));
                
                // Use the first sheet as main data for now
                if (allData.length === 0) {
                  allData = sheetData;
                }
                
                console.log(`Sheet "${sheetName}": ${sheetColumns.length} columns, ${sheetData.length} rows`);
              }
            });
            
            fileData.columns = allColumns;
            fileData.data = allData;
            fileData.sheets = sheets;
            fileData.currentSheet = sheetNames[0] || 'Sheet1';
            fileData.type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
            
            console.log(`Excel processed successfully: ${allColumns.length} total columns, ${allData.length} rows, ${Object.keys(sheets).length} sheets`);
            console.log(`Sample data from first sheet:`, allData.slice(0, 2));
            
          } catch (excelError) {
            console.error('Error parsing Excel file:', excelError);
            // Fallback to mock data if parsing fails
            fileData.columns = ['Column A', 'Column B', 'Column C', 'Column D'];
            fileData.data = [
              { 'Column A': 'Sample Data 1', 'Column B': 'Sample Data 2', 'Column C': 'Sample Data 3', 'Column D': 'Sample Data 4' },
              { 'Column A': 'Sample Data 5', 'Column B': 'Sample Data 6', 'Column C': 'Sample Data 7', 'Column D': 'Sample Data 8' },
              { 'Column A': 'Sample Data 9', 'Column B': 'Sample Data 10', 'Column C': 'Sample Data 11', 'Column D': 'Sample Data 12' }
            ];
            fileData.sheets = {
              'Sheet1': ['Column A', 'Column B', 'Column C', 'Column D'],
              'Sheet2': ['Column A', 'Column B']
            };
            fileData.currentSheet = 'Sheet1';
            fileData.type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
            console.warn('Falling back to mock Excel data due to parsing error');
          }
        } else {
          // Handle other file types
          fileData.columns = ['File Content'];
          fileData.data = [{ 'File Content': `File: ${file.name} (${file.type})` }];
          console.log(`Other file type processed: ${file.name}`);
        }
        
        newFiles.push(fileData);
      }
      
      // Add new files to the importedFiles state
      setImportedFiles(prev => [...prev, ...newFiles]);
      
      console.log(`Successfully imported ${newFiles.length} files. Total files: ${importedFiles.length + newFiles.length}`);
      
      // Show success message
      alert(`Successfully imported ${newFiles.length} file(s)!`);
      
      // Clear the file input value to prevent the same file from being selected again
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (error) {
      console.error('Error importing files:', error);
      alert(`Error importing files: ${error instanceof Error ? error.message : 'Unknown error'}`);
      
      // Clear the file input value even on error
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteFile = (fileName: string) => {
    // Implementation for deleting files
    console.log('Deleting file:', fileName);
  };

  // Calculate section heights
  const topSectionHeight = Math.floor((windowHeight - 150) * 0.5);
  const bottomSectionHeight = Math.floor((windowHeight - 140) * 0.5);

  // Additional workflow management functions
  const undoWorkflowStep = () => {
    if (workflowSteps.length > 0) {
      setWorkflowSteps(prev => prev.slice(0, -1));
    }
  };

  const redoWorkflowStep = () => {
    // Basic redo implementation - re-add the last removed step
    // For a more sophisticated implementation, we would need a proper undo/redo stack
    if (workflowSteps.length === 0) {
      // Add a sample step for demonstration
      addWorkflowStep({
        type: 'column',
        source: 'Sample Column'
      });
      } else {
      // Duplicate the last step
      const lastStep = workflowSteps[workflowSteps.length - 1];
      const { id, status, ...stepData } = lastStep; // Remove id and status from spread
      addWorkflowStep(stepData);
    }
  };

  const promptForNewColumn = () => {
    setShowNewColumnInput(true);
    setShowNewDropdown(false);
  };

  const promptForNewFile = () => {
    setShowNewFileInput(true);
    setShowNewDropdown(false);
  };

  const addNewWorkflow = () => {
    // Add a workflow comment step
    addWorkflowStep({
      type: 'custom',
      source: `Workflow Comment: ${workflowName || 'Untitled Workflow'}`
    });
    setShowNewDropdown(false);
    console.log('Added workflow comment step');
  };

  const addNewColumnWithName = (name?: string) => {
    const columnName = name || newColumnInput;
    if (columnName.trim()) {
      // Check if we're in function mode
      if (isFunctionOpen && activeFunction) {
        // Add as function parameter
        setFunctionParameters(prev => [...prev, columnName]);
        console.log(`Added new column "${columnName}" as parameter for function "${activeFunction}"`);
      } else {
        // Add as workflow step
        addWorkflowStep({
          type: 'column',
          source: columnName,
          target: columnName
        });
        console.log(`Added new column "${columnName}" as workflow step`);
      }
      setNewColumnInput('');
      setShowNewColumnInput(false);
    }
  };

  const addNewFileWithName = (name?: string) => {
    const fileName = name || newFileInput;
    if (fileName.trim()) {
      // Check if we're in function mode
      if (isFunctionOpen && activeFunction) {
        // Add as function parameter
        setFunctionParameters(prev => [...prev, fileName]);
        console.log(`Added new file "${fileName}" as parameter for function "${activeFunction}"`);
      } else {
        // Add as workflow step
        addWorkflowStep({
          type: 'custom',
          source: fileName
        });
        console.log(`Added new file "${fileName}" as workflow step`);
      }
      setNewFileInput('');
      setShowNewFileInput(false);
    }
  };

  const addCustomToWorkflow = () => {
    if (customInput.trim()) {
      // Check if we're in function mode
      if (isFunctionOpen && activeFunction) {
        // Add as function parameter
        setFunctionParameters(prev => [...prev, customInput.trim()]);
        console.log(`Added custom value "${customInput.trim()}" as parameter for function "${activeFunction}"`);
      } else {
        // Add as workflow step
        addWorkflowStep({
          type: 'custom',
          source: customInput.trim()
        });
        console.log(`Added custom value "${customInput.trim()}" as workflow step`);
      }
      setCustomInput('');
      setShowCustomInput(false);
    } else {
      // Show some feedback that input is required
      console.log('Custom input is required');
    }
  };

  // Additional missing functions
  const saveAndSelectWorkflow = () => {
    if (workflowSteps.length > 0) {
      // Select workflow output without requiring save
      // This adds all current workflow steps to the selected items for the next operation
      const workflowOutput = workflowSteps.map(step => {
        if (step.type === 'column' && step.columnReference) {
          return `${step.type}: ${step.columnReference.displayName}`;
        }
        return `${step.type}: ${step.source}`;
      }).join(' → ');
      
      // Add workflow result to selected columns for further processing
      const workflowColumnPath = `Workflow Output: ${workflowOutput}`;
      if (!selectedColumns.includes(workflowColumnPath)) {
        setSelectedColumns(prev => [...prev, workflowColumnPath]);
      }
      
      // Show notification or feedback
      console.log('Workflow output selected for further processing:', workflowColumnPath);
    }
  };

  const toggleWorkflowMode = () => {
    setWorkflowMode(prev => prev === 'column' ? 'sheet' : 'column');
  };

  const reorderWorkflowSteps = (draggedId: string, targetId: string) => {
    // Implementation for reordering workflow steps
    console.log('Reordering workflow steps:', draggedId, targetId);
  };

  const editWorkflowStep = (stepId: string) => {
    // Implementation for editing workflow step
    console.log('Editing workflow step:', stepId);
  };

  const updateHeaderConfig = (file: PlaygroundFile) => {
    // Implementation for updating header configuration
    console.log('Updating header config for:', file.name);
  };

  const handleSaveWorkflowTemplate = (template: WorkflowTemplate) => {
    // Save the workflow template
    console.log('Saving workflow template:', template);
    
    // Add to saved templates
    setSavedTemplates(prev => [...prev, template]);
    
    // Update current workflow name
    setWorkflowName(template.name);
    
    // Close the dialog
    setShowSaveDialog(false);
    
    // Optionally save to localStorage or backend
    try {
      const existingTemplates = JSON.parse(localStorage.getItem('workflowTemplates') || '[]');
      const updatedTemplates = [...existingTemplates, template];
      localStorage.setItem('workflowTemplates', JSON.stringify(updatedTemplates));
      
      console.log('Workflow template saved successfully!');
    } catch (error) {
      console.error('Error saving workflow template:', error);
    }
  };

  const handleExecuteWorkflow = (template: ExecuteWorkflowTemplate) => {
    // Execute the workflow
    console.log('Executing workflow:', template);
    
    // Set execution state
    setIsExecuting(true);
    setExecutionStatus('preparing');
    setExecutionProgress(0);
    
    // Close the dialog
    setShowExecuteDialog(false);
    
    // Simulate workflow execution
      setTimeout(() => {
      setExecutionStatus('processing');
      setExecutionProgress(50);
      
      setTimeout(() => {
        setExecutionStatus('completed');
        setExecutionProgress(100);
        setIsExecuting(false);
        
        // Set execution results
        setExecutionResults({
          status: 'success',
          message: 'Workflow executed successfully',
          outputFiles: template.saveInputFiles ? ['output_file_1.csv', 'output_file_2.csv'] : ['output_file.csv'],
          timestamp: new Date().toISOString()
        });
        
        console.log('Workflow execution completed!');
      }, 2000);
    }, 1000);
  };

  // Render file columns with clickable functionality
  const renderFileColumns = (file: PlaygroundFile) => {
    if (file.sheets && Object.keys(file.sheets).length > 0) {
      // Excel file with multiple sheets
      const fileKey = `${file.name}-${file.type}`;
      const isCollapsed = collapsedSheets[fileKey];
      
      if (isCollapsed) {
        // Collapsed mode: show all sheet names under main file
        return (
          <div key={fileKey} className="w-[280px] min-w-[250px] max-w-[320px] flex-shrink-0 flex flex-col max-h-full">
            <div className="flex items-start space-x-2 pb-3 border-b border-gray-200 flex-shrink-0">
              <File className="w-4 h-4 text-gray-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <h3 className={`font-medium text-gray-800 leading-tight ${
                  textWrapEnabled ? 'break-words' : 'truncate'
                }`} title={!textWrapEnabled ? file.name : undefined}>
                  {textWrapEnabled ? file.name : getTruncatedFileName(file.name, 35)}
              </h3>
              </div>
              <button
                onClick={() => toggleSheetCollapse(fileKey)}
                className="text-xs text-blue-600 hover:text-blue-800 transition-colors flex-shrink-0"
              >
                ▶
              </button>
            </div>
            <div className="mt-2 space-y-1 flex-1 overflow-y-auto column-scrollbar min-h-0">
              {Object.entries(file.sheets).map(([sheetName, columns]) => (
                <div key={sheetName} className="flex items-center space-x-2 p-1 bg-gray-50 rounded-md">
                  <span className="text-xs font-medium text-blue-600">▸ {sheetName}</span>
                  <span className="text-xs text-gray-500">({Array.isArray(columns) ? columns.length : 0} columns)</span>
                </div>
              ))}
            </div>
          </div>
        );
      } else {
        // Expanded mode: show each sheet as a separate column
        return Object.entries(file.sheets).map(([sheetName, columns]) => (
          <div key={`${fileKey}-${sheetName}`} className="w-[280px] min-w-[250px] max-w-[320px] flex-shrink-0 flex flex-col max-h-full">
            <div className="flex items-start space-x-2 pb-3 border-b border-gray-200 flex-shrink-0">
              <File className="w-4 h-4 text-gray-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <h3 className={`font-medium text-gray-800 leading-tight ${
                  textWrapEnabled ? 'break-words' : 'truncate'
                }`} title={!textWrapEnabled ? file.name : undefined}>
                  {textWrapEnabled ? file.name : getTruncatedFileName(file.name, 35)}
                </h3>
                <span className={`text-xs text-blue-600 font-medium ${
                  textWrapEnabled ? 'break-words' : 'truncate'
                }`} title={!textWrapEnabled ? sheetName : undefined}>▸ {textWrapEnabled ? sheetName : getTruncatedFileName(sheetName, 20)}</span>
              </div>
              <div className="flex items-center space-x-1 flex-shrink-0">
                {/* Header Configuration Button (3 dots) for Sheet */}
                <button
                  onClick={() => handleHeaderConfig({ ...file, currentSheet: sheetName })}
                  className="text-blue-500 hover:text-blue-700 transition-colors p-1 hover:bg-blue-50 rounded-md"
                  title="Header configuration for this sheet"
                >
                  <MoreHorizontal className="w-4 h-4" />
                </button>
                <button
                  onClick={() => toggleSheetCollapse(fileKey)}
                  className="text-xs text-blue-600 hover:text-blue-800 transition-colors"
                >
                  ▼
                </button>
              </div>
            </div>
            <div className="mt-2 space-y-1 flex-1 overflow-y-auto column-scrollbar min-h-0">
              {Array.isArray(columns) && columns.map((column, colIndex) => {
                const columnPath = `${file.name} ▸ ${sheetName} ▸ ${column}`;
                const isSelected = selectedColumns.includes(columnPath);
                return (
                  <div 
                    key={colIndex}
                    onClick={() => handleColumnClick(columnPath, file)}
                    className={`flex items-start p-2 rounded-md hover:bg-gray-50 cursor-pointer text-sm group transition-colors ${
                      isSelected ? 'bg-blue-50 border border-blue-200' : ''
                    }`}
                  >
                    <div className={`w-2 h-2 rounded-full mr-2 flex-shrink-0 mt-1.5 ${
                      isSelected ? 'bg-blue-500' : 'bg-gray-400'
                    }`} />
                    <span className="break-words flex-1 leading-relaxed">{column}</span>
                    {isSelected && (
                      <CheckCircle className="w-4 h-4 text-blue-500 ml-2" />
                    )}
                  </div>
                );
              })}
            </div>
            
            {/* File Selection Button for Excel Sheets */}
            <div className="mt-1 mb-2 flex-shrink-0">
              <button
                onClick={() => handleFileClick(file)}
                className={`w-full px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedFiles.includes(file.name)
                    ? 'bg-green-100 text-green-700 border border-green-300 hover:bg-green-200'
                    : 'bg-blue-100 text-blue-700 border border-blue-300 hover:bg-blue-200'
                }`}
                title={selectedFiles.includes(file.name) ? 'File selected - click to deselect' : 'Click to select entire file'}
              >
                {selectedFiles.includes(file.name) ? '✓ File Selected' : 'Select File'}
              </button>
            </div>
          </div>
        ));
      }
    } else {
      // Single file (CSV or single sheet Excel)
      return (
        <div key={file.name} className="w-[280px] min-w-[250px] max-w-[320px] flex-shrink-0 flex flex-col max-h-full">
          <div className="flex items-start space-x-2 pb-3 border-b border-gray-200 flex-shrink-0">
            <File className="w-4 h-4 text-gray-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <h3 className={`font-medium text-gray-800 leading-tight ${
                textWrapEnabled ? 'break-words' : 'truncate'
              }`} title={!textWrapEnabled ? file.name : undefined}>
                {textWrapEnabled ? file.name : getTruncatedFileName(file.name, 35)}
              </h3>
              <span className="text-xs text-gray-500">({Array.isArray(file.columns) ? file.columns.length : 0} columns)</span>
            </div>
            <div className="flex items-center space-x-1 flex-shrink-0">
              {/* Header Configuration Button (3 dots) for CSV */}
              <button
                onClick={() => handleHeaderConfig({ ...file, currentSheet: 'main' })}
                className="text-blue-500 hover:text-blue-700 transition-colors p-1 hover:bg-blue-50 rounded-md"
                title="Header configuration for this file"
              >
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="mt-3 space-y-1 flex-1 overflow-y-auto column-scrollbar min-h-0">
            {Array.isArray(file.columns) && file.columns.map((column, colIndex) => {
              const columnPath = `${file.name} ▸ ${column}`;
              const isSelected = selectedColumns.includes(columnPath);
              return (
                <div 
                  key={colIndex}
                  onClick={() => handleColumnClick(columnPath, file)}
                  className={`flex items-start p-2 rounded-md hover:bg-gray-50 cursor-pointer text-sm group transition-colors ${
                    isSelected ? 'bg-blue-50 border border-blue-200' : ''
                  }`}
                >
                  <div className={`w-2 h-2 rounded-full mr-2 flex-shrink-0 mt-1.5 ${
                    isSelected ? 'bg-blue-500' : 'bg-gray-400'
                  }`} />
                  <span className="break-words flex-1 leading-relaxed">{column}</span>
                  {isSelected && (
                    <CheckCircle className="w-4 h-4 text-blue-500 ml-2" />
                  )}
                </div>
              );
            })}
          </div>
          
          {/* File Selection Button for CSV Files */}
          <div className="mt-1 mb-2 flex-shrink-0">
            <button
              onClick={() => handleFileClick(file)}
              className={`w-full px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedFiles.includes(file.name)
                  ? 'bg-green-100 text-green-700 border border-green-300 hover:bg-green-200'
                  : 'bg-blue-100 text-blue-700 border border-blue-300 hover:bg-blue-200'
              }`}
              title={selectedFiles.includes(file.name) ? 'File selected - click to deselect' : 'Click to select entire file'}
            >
              {selectedFiles.includes(file.name) ? '✓ File Selected' : 'Select File'}
            </button>
          </div>
        </div>
      );
    }
  };

  // ... existing functions ...

  return (
    <ErrorBoundary>
      <div className={`${isEmbedded ? 'h-full-' : 'h-screen'} bg-gray-50 flex flex-col overflow-hidden`} onKeyDown={handleKeyDown}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {!isEmbedded && (
            <button
                onClick={() => navigate('/dashboard')}
              className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors mr-3"
                title="Back to Dashboard"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            )}
            <div className="p-2 bg-blue-100 rounded-lg">
              <Play className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Playground</h1>
              <p className="text-sm text-gray-600">Build and execute data workflows</p>
              <div className="flex items-center space-x-2 mt-1">
                <div className={`w-2 h-2 rounded-full ${
                  isFunctionOpen 
                    ? 'bg-blue-500' 
                    : backendConnected 
                      ? 'bg-green-500' 
                      : 'bg-red-500'
                } animate-pulse`}></div>
                <span className={`text-xs font-medium ${
                  isFunctionOpen 
                    ? 'text-blue-600' 
                    : backendConnected 
                      ? 'text-green-600' 
                      : 'text-red-600'
                }`}>
                  {isFunctionOpen 
                    ? `Function Mode: ${activeFunction} (click columns to add parameters)` 
                    : backendConnected 
                      ? 'Ready for workflow building' 
                      : 'Backend disconnected - workflow building limited'
                  }
                </span>
              </div>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            <button 
              onClick={loadWorkflow}
              className="px-4 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded-lg transition-colors flex items-center space-x-2 hover:shadow-sm"
              title="Load a saved workflow from file"
            >
              <Upload className="w-4 h-4" />
              <span>Load Workflow</span>
            </button>
            <button 
              onClick={async () => {
                try {
                  await checkHealth();
                  alert('Backend connection successful!');
                } catch (error) {
                  alert(`Backend connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
                }
              }}
              className="px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg transition-colors flex items-center space-x-2 hover:shadow-sm"
              title="Test backend connection and data processing"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Test Backend</span>
            </button>
            <button 
              onClick={saveWorkflow}
              disabled={workflowSteps.length === 0}
              className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                workflowSteps.length === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700 hover:shadow-sm'
              }`}
              title={workflowSteps.length === 0 ? 'No workflow steps to save' : 'Save workflow as JSON template'}
            >
              <Save className="w-4 h-4" />
              <span>Save Workflow</span>
            </button>
                               {/* Enhanced Execute Button with Progress */}
                   <div className="flex items-center space-x-2">
            <button 
                       onClick={executeWorkflowWithDialog}
              disabled={workflowSteps.length === 0 || isExecuting}
              className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                workflowSteps.length === 0 || isExecuting
                  ? 'bg-gray-400 text-gray-300 cursor-not-allowed'
                           : 'bg-green-600 hover:bg-green-700 text-white hover:shadow-lg'
              }`}
              title={
                workflowSteps.length === 0 
                  ? 'No workflow steps to execute' 
                  : isExecuting 
                    ? 'Workflow is executing...' 
                             : 'Save template and execute workflow with file processing'
              }
            >
              {isExecuting ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              <span>{isExecuting ? 'Executing...' : 'Execute'}</span>
            </button>
              
              {/* Progress Bar */}
              {isExecuting && (
                <div className="flex items-center space-x-2">
                  <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 transition-all duration-300 rounded-full"
                      style={{ width: `${executionProgress}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-600 font-medium">
                    {Math.round(executionProgress)}%
                    </span>
              </div>
              )}
              
              {/* Cancel Button */}
              {canCancelExecution && (
                    <button 
                  onClick={cancelExecution}
                  className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors flex items-center space-x-2"
                  title="Cancel workflow execution"
                    >
                  <X className="w-4 h-4" />
                  <span>Cancel</span>
                    </button>
                      )}
                    </div>
                              </div>
                              </div>
                                </div>

      {/* Execution Results Display */}
      {executionResults && (
        <div className="bg-green-50 border-b border-green-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div>
                <h3 className="text-sm font-semibold text-green-800">Workflow Execution Completed</h3>
                <p className="text-xs text-green-600">
                  Processed {executionResults?.rowCount || 0} rows • {executionResults?.columns?.length || 0} columns • 
                  {executionResults?.executionTime?.toFixed(2) || '0.00'}ms • {executionResults?.memoryUsage?.toFixed(2) || '0.00'}MB
                </p>
                            </div>
            </div>
            <div className="flex items-center space-x-2">
                              <button
                onClick={() => exportExecutionResults(executionResults)}
                className="px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-sm transition-colors flex items-center space-x-2"
                title="Export results to CSV"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              <button
                onClick={() => setExecutionResults(null)}
                className="text-green-600 hover:text-green-800 p-1"
                title="Dismiss results"
              >
                <X className="w-4 h-4" />
                              </button>
                    </div>
                  </div>
                </div>
              )}
              
      {/* Main Content */}
      <div className="flex-1 p-4 overflow-hidden">
        <div className="grid grid-cols-12 gap-6 top-section-container" style={{ height: `${topSectionHeight}px` }}>
          {/* Left Panel - Data Sources (reused component) */}
          <div className="col-span-3 h-full">
            <DataSources
              importedFiles={importedFiles as unknown as Array<{ name: string; type: string; size: number; columns: string[]; path: string; lastModified: Date; sheets?: { [sheetName: string]: string[] }; headerConfig?: { row: number; merged: boolean; customHeaders?: string[]; autoDetected: boolean }; currentSheet?: string; }>}
              onBrowseFiles={handleBrowseFiles}
              onDragDropImport={handleFileImport}
              onDeleteFile={handleDeleteFile}
              height={topSectionHeight}
              showDeleteButton={true}
              showHeaderConfig={true}
            />
          </div>

          {/* Center Panel - Workflow Builder */}
          <Card className="col-span-6 h-full max-w-none workflow-builder-container">
            <CardContent className="p-3 h-full flex flex-col overflow-hidden workflow-builder-content">
              <div className="flex items-center justify-between mb-2 flex-shrink-0">
                <h3 className="font-semibold flex items-center">
                  <Play className="w-4 h-4 mr-2" />
                  Workflow Builder
                </h3>
                
                                {/* Workflow Builder Toolbar */}
                <div className="flex items-center space-x-2 max-w-full overflow-hidden workflow-builder-toolbar">
                  {/* Undo/Redo */}
                  <button
                    onClick={undoWorkflowStep}
                    disabled={workflowSteps.length === 0}
                    className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                    title="Undo previous step"
                  >
                    <Undo2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={redoWorkflowStep}
                    disabled={workflowSteps.length === 0}
                    className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                    title="Redo previous step"
                  >
                    <Redo2 className="w-4 h-4" />
                  </button>
                  
                  {/* New Dropdown */}
                  <div className="relative dropdown-container">
                    <button
                      onClick={() => setShowNewDropdown(!showNewDropdown)}
                      className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors font-medium flex items-center space-x-2"
                      title="Create new column, file, or workflow"
                    >
                      <Plus className="w-4 h-4" />
                      <span>New</span>
                    </button>
                    {showNewDropdown && (
                      <div className="absolute left-0 bottom-full mb-1 bg-white border border-gray-200 rounded-md shadow-lg z-10 min-w-[120px] max-w-[200px]">
                        <button
                          onClick={() => promptForNewColumn()}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 transition-colors flex items-center space-x-2"
                        >
                          <File className="w-3 h-3" />
                          <span>Column</span>
                        </button>
                        <button
                          onClick={() => promptForNewFile()}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 transition-colors flex items-center space-x-2"
                        >
                          <Grid3X3 className="w-3 h-3" />
                          <span>File</span>
                        </button>
                        <button
                          onClick={() => addNewWorkflow()}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 transition-colors flex items-center space-x-2"
                        >
                          <Play className="w-3 h-3" />
                          <span>Workflow</span>
                        </button>
                      </div>
                    )}

                    {/* New Column Input */}
                    {showNewColumnInput && (
                      <div className="absolute left-0 bottom-full mb-1 bg-white border border-gray-200 rounded-md shadow-lg z-10 p-2 min-w-[200px] max-w-[250px]">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-xs text-gray-600">
                            {isFunctionOpen && activeFunction ? `Add as parameter for ${activeFunction}` : 'New Column'} &lt;
                          </span>
                          <input
                            type="text"
                            value={newColumnInput}
                            onChange={(e) => setNewColumnInput(e.target.value)}
                            placeholder={isFunctionOpen && activeFunction ? "Enter column name for function" : "Enter column name"}
                            className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                addNewColumnWithName(newColumnInput);
                              }
                            }}
                            autoFocus
                          />
                          <span className="text-xs text-gray-600">&gt;</span>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => addNewColumnWithName()}
                            className="flex-1 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                          >
                            Add
                          </button>
                          <button
                            onClick={() => setShowNewColumnInput(false)}
                            className="flex-1 px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}

                    {/* New File Input */}
                    {showNewFileInput && (
                      <div className="absolute left-0 bottom-full mb-1 bg-white border border-gray-200 rounded-md shadow-lg z-10 p-2 min-w-[200px] max-w-[250px]">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-xs text-gray-600">
                            {isFunctionOpen && activeFunction ? `Add as parameter for ${activeFunction}` : 'New File'} &lt;
                          </span>
                          <input
                            type="text"
                            value={newFileInput}
                            onChange={(e) => setNewFileInput(e.target.value)}
                            placeholder={isFunctionOpen && activeFunction ? "Enter file name for function" : "Enter file name"}
                            className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                addNewFileWithName();
                              }
                            }}
                            autoFocus
                          />
                          <span className="text-xs text-gray-600">&gt;</span>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => addNewFileWithName()}
                            className="flex-1 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                          >
                            Add
                          </button>
                          <button
                            onClick={() => setShowNewFileInput(false)}
                            className="flex-1 px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Custom Input */}
                  <div className="relative dropdown-container">
                    <button
                      onClick={() => setShowCustomInput(!showCustomInput)}
                      className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors font-medium"
                      title="Add custom value"
                    >
                      Custom
                    </button>
                    {showCustomInput && (
                      <div className="absolute left-0 bottom-full mb-1 bg-white border border-gray-200 rounded-md shadow-lg z-10 p-2 min-w-[200px] max-w-[250px]">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-xs text-gray-600">
                            {isFunctionOpen && activeFunction ? `Add as parameter for ${activeFunction}` : 'Custom'} &lt;
                          </span>
                          <input
                            type="text"
                            value={customInput}
                            onChange={(e) => setCustomInput(e.target.value)}
                            placeholder={isFunctionOpen && activeFunction ? "Enter custom value for function" : "Enter custom value"}
                            className="flex-1 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                addCustomToWorkflow();
                              }
                            }}
                            autoFocus
                          />
                          <span className="text-xs text-gray-600">&gt;</span>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={addCustomToWorkflow}
                            className="flex-1 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                          >
                            Add
                          </button>
                          <button
                            onClick={() => setShowCustomInput(false)}
                            className="flex-1 px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>


                  
                  {/* Save & Select */}
                  <button
                    onClick={saveAndSelectWorkflow}
                    disabled={workflowSteps.length === 0}
                    className="px-3 py-2 text-sm text-green-600 hover:text-green-800 hover:bg-green-100 rounded transition-colors font-medium"
                    title="Save and select workflow output"
                  >
                    Save & Select
                  </button>
                  
                  {/* Clear Button */}
                  <button
                    onClick={clearWorkflow}
                    className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors"
                    title="Clear all workflow steps"
                  >
                    Clear
                  </button>
                  
                  {/* Mode Toggle */}
                  <button
                    onClick={toggleWorkflowMode}
                    className={`px-3 py-2 rounded transition-colors flex items-center space-x-2 ${
                      workflowMode === 'column'
                        ? 'text-blue-600 bg-blue-100 hover:bg-blue-200'
                        : 'text-purple-600 bg-purple-100 hover:bg-purple-200'
                    }`}
                    title={`Current mode: ${workflowMode} (click to toggle)`}
                  >
                    {workflowMode === 'column' ? <File className="w-4 h-4" /> : <Grid3X3 className="w-4 h-4" />}
                    <span className="text-sm font-medium">
                      {workflowMode === 'column' ? 'Column' : 'Sheet'}
                    </span>
                  </button>
                  

                </div>
              </div>
              
              {/* Scrollable workflow content */}
              <div 
                className="flex-1 overflow-y-auto workflow-builder-scrollbar max-w-full"
                style={{ minHeight: '200px', maxHeight: 'calc(100vh - 400px)' }}
                onScroll={(e) => {
                  const target = e.target as HTMLDivElement;
                  setWorkflowScrollTop(target.scrollTop);
                }}
              >
                {workflowSteps.length === 0 ? (
                  <div className="text-center border-2 border-dashed border-gray-300 rounded-lg h-full flex flex-col justify-center">
                    <Play className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <h3 className="text-lg font-semibold mb-2">Ready to Build Workflow</h3>
                    <div className="text-sm text-gray-500 space-y-2">
                      <p>• Click on columns in the Data Preview to add them</p>
                      <p>• Click on functions in the Formula Engine to apply them</p>
                      <p>• Build your data processing pipeline step by step</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 max-w-full">
                    {workflowSteps.map((step, index) => (
                      <div 
                        key={step.id} 
                        draggable={true}
                        onDragStart={(e) => {
                          e.dataTransfer.setData('text/plain', step.id);
                          e.currentTarget.classList.add('opacity-50', 'scale-95');
                        }}
                        onDragEnd={(e) => {
                          e.currentTarget.classList.remove('opacity-50', 'scale-95');
                        }}
                        onDragOver={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.add('border-blue-400', 'bg-blue-50');
                        }}
                        onDragLeave={(e) => {
                          e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
                        }}
                        onDrop={(e) => {
                          e.preventDefault();
                          e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
                          const draggedStepId = e.dataTransfer.getData('text/plain');
                          if (draggedStepId !== step.id) {
                            reorderWorkflowSteps(draggedStepId, step.id);
                          }
                        }}
                        className={`border-2 rounded-xl p-4 bg-gradient-to-r cursor-move ${
                          step.type === 'column' ? 'from-blue-50 to-blue-100 border-blue-200' :
                          step.type === 'function' ? 'from-green-50 to-green-100 border-green-200' :
                          step.type === 'break' ? 'from-red-50 to-red-100 border-red-200' :
                          step.type === 'custom' ? 'from-purple-50 to-purple-100 border-purple-200' :
                          step.type === 'sheet' ? 'from-orange-50 to-orange-100 border-orange-200' :
                          'from-gray-50 to-gray-100 border-gray-200'
                        } shadow-sm hover:shadow-md transition-all duration-200`}
                      >
                        
                        {/* Step Header with Enhanced Visuals */}
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-4">
                            {/* Drag Handle */}
                            <div className="flex items-center justify-center w-6 h-6 text-gray-400 hover:text-gray-600 cursor-move">
                              <div className="flex flex-col space-y-0.5">
                                <div className="w-1 h-1 bg-current rounded-full"></div>
                                <div className="w-1 h-1 bg-current rounded-full"></div>
                                <div className="w-1 h-1 bg-current rounded-full"></div>
                              </div>
                            </div>
                            
                            {/* Step Number with Badge */}
                            <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white ${
                              step.type === 'column' ? 'bg-blue-500' :
                              step.type === 'function' ? 'bg-green-500' :
                              step.type === 'break' ? 'bg-red-500' :
                              step.type === 'custom' ? 'bg-purple-500' :
                              step.type === 'sheet' ? 'bg-orange-500' :
                              'bg-gray-500'
                            }`}>
                              {index + 1}
                            </div>
                            
                            {/* Step Type Icon with Enhanced Styling */}
                            <div className={`p-2 rounded-lg ${
                              step.type === 'column' ? 'bg-blue-100 text-blue-600' :
                              step.type === 'function' ? 'bg-green-100 text-green-600' :
                              step.type === 'break' ? 'bg-red-100 text-red-600' :
                              step.type === 'custom' ? 'bg-purple-100 text-purple-600' :
                              step.type === 'sheet' ? 'bg-orange-100 text-orange-600' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {step.type === 'column' ? (
                                <File className="w-5 h-5" />
                              ) : step.type === 'function' ? (
                                <Code className="w-5 h-5" />
                              ) : step.type === 'break' ? (
                                <Link className="w-5 h-5" />
                              ) : step.type === 'custom' ? (
                                <Type className="w-5 h-5" />
                              ) : step.type === 'sheet' ? (
                                <Grid3X3 className="w-5 h-5" />
                              ) : (
                                <File className="w-5 h-5" />
                              )}
                            </div>
                            
                            {/* Step Content with Better Typography */}
                            <div className="min-w-0 flex-1 overflow-hidden">
                              {step.type === 'column' ? (
                                <div className="text-sm">
                                  <span className="font-semibold text-gray-800">
                                    {step.columnReference?.displayName || step.source}
                                  </span>
                                  {step.sheet && <span className="text-gray-600 mx-2">→</span>}
                                  {step.sheet && <span className="text-blue-600 font-medium">{step.sheet}</span>}
                                  <span className="text-gray-600 mx-2">→</span>
                                  <span className="text-gray-700 font-medium">{step.target}</span>
                                </div>
                              ) : step.type === 'function' ? (
                                <div className="text-sm">
                                  <span className="font-semibold text-gray-800">{step.source}</span>
                                  {step.parameters && step.parameters.length > 0 ? (
                                    <span className="text-green-600 font-medium"> ({step.parameters.join(', ')})</span>
                                  ) : (
                                    <span className="text-green-600 font-medium"> ()</span>
                                  )}
                                </div>
                                                             ) : step.type === 'break' ? (
                                <div className="text-sm text-red-700 font-semibold">
                                   {step.source === 'WORKFLOW_BREAK' ? '── New Workflow ──' : '── Workflow Break ──'}
                                 </div>
                              ) : step.type === 'custom' ? (
                                <div className="text-sm text-purple-700 font-semibold">
                                  {step.source}
                                </div>
                              ) : step.type === 'sheet' ? (
                                <div className="text-sm">
                                  <span className="font-semibold text-gray-800">{step.source}</span>
                                  <span className="text-gray-600 mx-2">→</span>
                                  <span className="text-orange-600 font-medium">{step.target}</span>
                                </div>
                              ) : (
                                <div className="text-sm text-gray-600">
                                  {step.source}
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Status and Actions */}
                          <div className="flex items-center space-x-3">
                            {/* Enhanced Status Indicator */}
                          <div className="flex items-center space-x-2">
                              <div className={`w-3 h-3 rounded-full ${
                                step.status === 'completed' ? 'bg-green-500 animate-pulse' :
                                step.status === 'processing' ? 'bg-blue-500 animate-spin' :
                              step.status === 'failed' ? 'bg-red-500' :
                              'bg-gray-400'
                            }`} />
                              <span className={`text-xs font-medium ${
                                step.status === 'completed' ? 'text-green-600' :
                                step.status === 'processing' ? 'text-blue-600' :
                                step.status === 'failed' ? 'text-red-600' :
                                'text-gray-500'
                              }`}>
                                {step.status}
                              </span>
                            </div>
                            
                            {/* Action Buttons */}
                            <div className="flex items-center space-x-1">
                              {/* Edit Button */}
                              <button
                                onClick={() => editWorkflowStep(step.id)}
                                className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
                                title="Edit this step"
                              >
                                <Edit3 className="w-4 h-4" />
                              </button>
                              
                              {/* Delete Button */}
                            <button
                              onClick={() => removeWorkflowStep(step.id)}
                                className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                                title="Delete this step"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                            </div>
                          </div>
                        </div>
                        
                        {/* Enhanced Function Parameter Collection */}
                         {step.type === 'function' && isFunctionOpen && step.id === workflowSteps[workflowSteps.length - 1]?.id && (
                          <div className="mt-3 p-3 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200 max-w-full overflow-hidden">
                            <div className="flex items-center space-x-2 mb-3">
                              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                              <span className="text-sm font-medium text-blue-700">
                                Function Parameter Collection Active
                              </span>
                            </div>
                            <div className="text-xs text-blue-700 mb-3">
                              💡 <strong>Tip:</strong> Click columns in the Data Preview to add parameters, then press <kbd className="px-2 py-1 bg-blue-200 border border-blue-300 rounded text-xs font-mono">Enter</kbd> to complete
                            </div>
                            <div className="text-xs text-blue-600 mb-3 p-2 bg-white rounded border border-blue-200">
                              <span className="font-medium">Current Function:</span> <strong>{step.source}</strong>
                              <br />
                              <span className="font-medium">Parameters:</span> <span className="font-mono">[{functionParameters.join(', ')}]</span>
                            </div>
                            {functionParameters.length > 0 && (
                              <div className="flex items-center space-x-2">
                              <button
                                onClick={completeFunction}
                                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg transition-colors flex items-center space-x-2"
                              >
                                  <CheckCircle className="w-4 h-4" />
                                  <span>Complete Function</span>
                              </button>
                                <button
                                  onClick={() => setFunctionParameters([])}
                                  className="px-3 py-1.5 bg-gray-500 hover:bg-gray-600 text-white text-xs font-medium rounded-lg transition-colors"
                                >
                                  Reset
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                        
                        {/* Step Description Tooltip */}
                        <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
                          <span>
                            {step.type === 'column' && 'Data column selection step'}
                            {step.type === 'function' && 'Function application step'}
                            {step.type === 'break' && 'Workflow separation step'}
                            {step.type === 'custom' && 'Custom value or operation step'}
                            {step.type === 'sheet' && 'Sheet or file operation step'}
                          </span>
                          <span className="text-blue-500 font-medium">💡 Drag to reorder</span>
                        </div>
                      </div>
                    ))}
                    
                    {/* Enhanced Visual Flow Indicators */}
                    {workflowSteps.length > 1 && (
                      <div className="flex flex-col items-center space-y-2 py-4">
                        <div className="flex items-center space-x-2 text-gray-400">
                          <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                          <span className="text-sm font-medium">Data Flow</span>
                          <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                        </div>
                        <div className="flex items-center space-x-1">
                          {workflowSteps.map((_, index) => (
                            <div key={index} className="flex flex-col items-center">
                              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                              {index < workflowSteps.length - 1 && (
                                <div className="w-0.5 h-6 bg-gradient-to-b from-blue-400 to-transparent"></div>
                              )}
                            </div>
                          ))}
                        </div>
                        <div className="text-xs text-gray-500 text-center">
                          Data flows sequentially through each step, with each step building upon the previous one
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Right Panel - Enhanced Formula Engine */}
          <Card className="col-span-3 h-full formula-engine-container">
            <CardContent className="p-3 h-full flex flex-col formula-engine-content">
              {/* Formula Engine Header with Search and Controls */}
              <div className="flex items-center justify-between mb-3 flex-shrink-0">
                <h3 className="font-semibold flex items-center">
                  <Code className="w-4 h-4 mr-2" />
                  Formula Engine
                </h3>
                
                {/* View Mode Toggle with Search and Sort Icons */}
                <div className="flex items-center space-x-2">
                  {/* Search Icon */}
                  <button
                    onClick={() => setShowSearchBar(!showSearchBar)}
                    className={`p-2 rounded-md transition-colors ${
                      showSearchBar
                        ? 'bg-blue-100 text-blue-700 border border-blue-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    title="Toggle Search"
                  >
                    <Search className="w-4 h-4" />
                  </button>
                  
                  {/* Sort Icon */}
                  <div className="relative">
                    <button
                      onClick={() => setShowSortDropdown(!showSortDropdown)}
                      className={`p-2 rounded-md transition-colors ${
                        showSortDropdown
                          ? 'bg-blue-100 text-blue-700 border border-blue-300'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                      title="Sort Formulas"
                    >
                      <ArrowUpDown className="w-4 h-4" />
                    </button>
                    
                    {/* Sort Dropdown */}
                    {showSortDropdown && (
                      <div className="sort-dropdown-container absolute right-0 top-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg z-10 min-w-[150px]">
                        <div className="py-1">
                          <button
                            onClick={() => {
                              setFormulaSortBy('name');
                              setShowSortDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 ${
                              formulaSortBy === 'name' ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                            }`}
                          >
                            Name (A-Z)
                          </button>
                          <button
                            onClick={() => {
                              setFormulaSortBy('category');
                              setShowSortDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 ${
                              formulaSortBy === 'category' ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                            }`}
                          >
                            Category (A-Z)
                          </button>
                          <button
                            onClick={() => {
                              setFormulaSortBy('usage');
                              setShowSortDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-100 ${
                              formulaSortBy === 'usage' ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                            }`}
                          >
                            Usage Count
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* View Mode Buttons */}
                  <button
                    onClick={() => setFormulaViewMode('categories')}
                    className={`p-2 rounded-md transition-colors ${
                      formulaViewMode === 'categories'
                        ? 'bg-blue-100 text-blue-700 border border-blue-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    title="Category View"
                  >
                    <Grid3X3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setFormulaViewMode('normal')}
                    className={`p-2 rounded-md transition-colors ${
                      formulaViewMode === 'normal'
                        ? 'bg-blue-100 text-blue-700 border border-blue-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    title="List View"
                  >
                    <List className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setFormulaViewMode('favorites')}
                    className={`p-2 rounded-md transition-colors ${
                      formulaViewMode === 'favorites'
                        ? 'bg-blue-100 text-blue-700 border border-blue-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                    title="Favorites View"
                  >
                    <Star className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Search Bar - Hidden by default, shown when search icon is clicked */}
              {showSearchBar && (
                <div className="relative mb-3 flex-shrink-0">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search formulas by name, description, or category..."
                    value={formulaSearchTerm}
                    onChange={(e) => setFormulaSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              )}

              {/* Formula content - Covers entire container */}
                              <div className="flex-1 overflow-y-auto">
                                {formulaViewMode === 'categories' ? (
                  /* Category View */
                  <div className="space-y-2 h-full">
                    {Object.entries(getFormulasByCategory()).map(([category, formulas]) => (
                      <div key={category} className="border border-gray-200 rounded-lg">
                        <button
                          onClick={() => toggleCategoryExpansion(category)}
                          className="category-header w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors rounded-t-lg"
                        >
                          <span className="font-medium text-gray-800">{category}</span>
                          <span className="text-sm text-gray-500">({formulas.length} formulas)</span>
                          {expandedCategories[category] ? (
                            <ChevronDown className="w-4 h-4 text-gray-500" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-gray-500" />
                          )}
                        </button>
                        
                        {expandedCategories[category] && (
                          <div className="p-2 space-y-1 bg-white rounded-b-lg">
                            {formulas.map((formula) => (
                              <div
                                key={formula.name}
                                onClick={() => handleFunctionClick(formula.name)}
                                className={`formula-item p-2 rounded-md cursor-pointer transition-all border hover:shadow-sm ${
                                  activeFunction === formula.name && isFunctionOpen
                                    ? 'bg-blue-100 border-blue-300 text-blue-700' 
                                    : 'bg-gray-50 hover:bg-gray-100 border-transparent hover:border-gray-200 text-gray-700'
                                }`}
                              >
                                <div className="flex items-center justify-between mb-2">
                                  <div className="text-sm">{getEnhancedFunctionDisplay(formula)}</div>
                                  <div className="flex items-center space-x-2">
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        toggleFavorite(formula.name);
                                      }}
                                      className="p-1 rounded transition-colors text-gray-400 hover:text-yellow-500"
                                      title="Add to favorites"
                                    >
                                      <Star className="w-3 h-3" />
                                    </button>
                                  </div>
                                </div>
                                <p className="text-xs text-gray-600 mb-2">{formula.description}</p>
                                <code className="text-xs text-gray-700 bg-gray-100 px-2 py-1 rounded block">
                                  {formula.syntax}
                                </code>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : formulaViewMode === 'normal' ? (
                  /* Normal View */
                  <div className="space-y-1 h-full">
                    {getFilteredFormulas().map((formula) => (
                      <div
                        key={formula.name}
                        onClick={() => handleFunctionClick(formula.name)}
                        className={`formula-item p-2 rounded-md cursor-pointer transition-all border hover:shadow-sm ${
                          activeFunction === formula.name && isFunctionOpen
                            ? 'bg-blue-100 border-blue-300 text-blue-700' 
                            : 'bg-white hover:bg-gray-50 border-gray-200 hover:border-gray-300 text-gray-800'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                            <div className="text-sm">{getEnhancedFunctionDisplay(formula)}</div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFavorite(formula.name);
                              }}
                              className="p-1 rounded transition-colors text-gray-400 hover:text-yellow-500"
                              title="Add to favorites"
                            >
                              <Star className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                        

                      </div>
                    ))}
                  </div>
                ) : formulaViewMode === 'favorites' ? (
                  /* Favorites View */
                  <div className="space-y-1 h-full">
                    {favoriteFormulas.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Star className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                        <p className="text-sm">No favorite formulas yet</p>
                        <p className="text-xs">Click the star icon on any formula to add it to favorites</p>
                      </div>
                    ) : (
                      getFilteredFormulas()
                        .filter(formula => favoriteFormulas.includes(formula.name))
                        .map((formula) => (
                      <div
                        key={formula.name}
                        onClick={() => handleFunctionClick(formula.name)}
                                                        className={`formula-item p-2 rounded-md cursor-pointer transition-all border hover:shadow-sm ${
                          activeFunction === formula.name && isFunctionOpen
                            ? 'bg-blue-100 border-blue-300 text-blue-700' 
                                : 'bg-white hover:bg-gray-50 border-gray-200 hover:border-gray-300 text-gray-800'
                        }`}
                      >
                            <div className="flex items-center justify-between">
                              <div className="text-sm">{getEnhancedFunctionDisplay(formula)}</div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleFavorite(formula.name);
                              }}
                                  className="p-1 rounded transition-colors text-yellow-500 hover:text-yellow-600"
                                  title="Remove from favorites"
                                >
                                  <Star className="w-3 h-3 fill-current" />
                            </button>
                          </div>
                        </div>
                            <p className="text-xs text-gray-600 mt-1">{formula.description}</p>
                            <code className="text-xs text-gray-700 bg-gray-100 px-2 py-1 rounded block mt-1">
                          {formula.syntax}
                        </code>
                      </div>
                        ))
                )}
                  </div>
                ) : null}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Clear separation line */}
        <div className="w-full h-px bg-gray-300 my-1"></div>

        {/* Data Preview Section */}
        <div className="data-preview-section mt-1" style={{ height: `${bottomSectionHeight}px` }}>
          <Card className="h-full">
                                        <CardContent className="p-2 h-full">
                     {/* Clickable Header - Switches between Data Preview and Live Preview */}
                     <div 
                       onClick={() => setPreviewMode(previewMode === 'structure' ? 'live' : 'structure')}
                                               className={`cursor-pointer transition-all duration-200 rounded-lg p-2 mb-2 ${
                         previewMode === 'structure' 
                           ? 'bg-blue-50 border border-blue-200 hover:bg-blue-100' 
                           : 'bg-green-50 border border-green-200 hover:bg-green-100'
                       }`}
                     >
                       <div className="flex items-center justify-between">
                         {/* Left: Header with Icon and Title */}
                         <div className="flex items-center space-x-3">
                           <div className={`p-2 rounded-lg ${
                             previewMode === 'structure' 
                               ? 'bg-blue-100 text-blue-600' 
                               : 'bg-green-100 text-green-600'
                           }`}>
                             {previewMode === 'structure' ? (
                               <Eye className="w-5 h-5" />
                             ) : (
                               <Play className="w-5 h-5" />
                             )}
                           </div>
                           <div>
                                                          <h3 className={`font-semibold ${
                               previewMode === 'structure' ? 'text-blue-800' : 'text-green-800'
                             }`}>
                               {previewMode === 'structure' 
                                 ? (isFunctionOpen 
                                     ? `Data Preview - Select Columns for ${activeFunction}` 
                                     : 'Data Preview - Clickable Columns & Files'
                                   )
                                 : 'Live Preview - Workflow Results'
                               }
                </h3>
                             <p className={`text-sm ${
                               previewMode === 'structure' ? 'text-blue-600' : 'text-green-600'
                             }`}>
                               {previewMode === 'structure' 
                                 ? (isFunctionOpen 
                                     ? `Click columns to add as parameters for ${activeFunction} function`
                                     : 'Click columns to add to workflow, or click "Select File" to add entire files'
                                   )
                                 : 'Real-time preview of workflow execution results'
                               }
                             </p>
                           </div>
                         </div>

                         {/* Right: Controls based on mode */}
                <div className="flex items-center space-x-3">
                           {previewMode === 'structure' ? (
                             // Data Preview Controls
                             <>
                               <span className="text-sm text-blue-600">
                                 Click columns to add to workflow
                  </span>
                               {/* Text Wrap Toggle */}
                               <button
                                 onClick={(e) => {
                                   e.stopPropagation();
                                   setTextWrapEnabled(!textWrapEnabled);
                                 }}
                                 className={`px-3 py-1 rounded text-sm transition-colors flex items-center space-x-2 ${
                                   textWrapEnabled
                                     ? 'bg-blue-100 text-blue-700 border border-blue-300'
                                     : 'bg-white text-blue-600 hover:bg-blue-50 border border-blue-200'
                                 }`}
                                 title={textWrapEnabled ? 'Disable text wrapping (save space)' : 'Enable text wrapping (show full names)'}
                               >
                                 <FileText className="w-3 h-3" />
                                 <span>{textWrapEnabled ? 'Compact' : 'Expand'}</span>
                               </button>
                  {(selectedColumns.length > 0 || selectedFiles.length > 0) && (
                    <button 
                                   onClick={(e) => {
                                     e.stopPropagation();
                        setSelectedColumns([]);
                        setSelectedFiles([]);
                      }}
                      className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-sm transition-colors"
                    >
                      Clear All
                    </button>
                  )}
                             </>
                           ) : (
                             // Live Preview Controls
                             <>
                               {/* Status Indicator */}
                               <div className="flex items-center space-x-2">
                                 <div className={`w-2 h-2 rounded-full ${
                                   isPreviewLoading ? 'bg-green-500 animate-pulse' : 'bg-green-500'
                                 }`} />
                                 <span className="text-sm font-medium text-green-700">
                                   {isPreviewLoading ? 'Generating Preview...' : 'Preview Ready'}
                                 </span>
                </div>

                               {/* Sample Size Dropdown */}
                               <div className="relative">
                                 <select
                                   value={sampleSize}
                                   onChange={(e) => setSampleSize(Number(e.target.value) as 10 | 50 | 100)}
                                   onClick={(e) => e.stopPropagation()}
                                   className="px-3 py-1 text-sm border border-green-200 rounded-md bg-white text-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                 >
                                   <option value={10}>10 rows</option>
                                   <option value={50}>50 rows</option>
                                   <option value={100}>100 rows</option>
                                 </select>
                                 {selectedColumnsPreview && (
                                   <div className="absolute -bottom-6 left-0 text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-200 whitespace-nowrap">
                                     Live Preview: {selectedColumnsPreview.columns.length} columns
                                   </div>
                                 )}
                               </div>

                               {/* Step Results Toggle Button */}
                               <button
                                 onClick={(e) => {
                                   e.stopPropagation();
                                   setPreviewResultMode(previewResultMode === 'step' ? 'final' : 'step');
                                 }}
                                 className={`px-3 py-1.5 rounded text-sm transition-colors border ${
                                   previewResultMode === 'step'
                                     ? 'bg-green-100 hover:bg-green-200 text-green-700 border-green-300'
                                     : 'bg-purple-100 hover:bg-purple-200 text-purple-700 border-purple-300'
                                 }`}
                                 title="Toggle between Step Results and Final Result"
                               >
                                 {previewResultMode === 'step' ? 'Step Results' : 'Final Result'}
                               </button>

                               {/* Step Navigation - Only show when in Step Results mode */}
                               {previewResultMode === 'step' && workflowSteps.length > 0 && (
                                 <div className="flex items-center space-x-2">
                                   <button
                                     onClick={(e) => {
                                       e.stopPropagation();
                                       goToPreviousStep();
                                     }}
                                     disabled={currentStepIndex === 0}
                                     className="px-3 py-1.5 rounded text-sm transition-colors border bg-blue-100 hover:bg-blue-200 text-blue-700 border-blue-300 disabled:opacity-50 disabled:cursor-not-allowed"
                                     title="Go to previous step"
                                   >
                                     ← Previous
                                   </button>
                                   
                                   <span className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded">
                                     Step {currentStepIndex + 1} of {workflowSteps.length}
                                   </span>
                                   
                                   <button
                                     onClick={(e) => {
                                       e.stopPropagation();
                                       goToNextStep();
                                     }}
                                     disabled={currentStepIndex === workflowSteps.length - 1}
                                     className="px-3 py-1.5 rounded text-sm transition-colors border bg-blue-100 hover:bg-blue-200 text-blue-700 border-blue-300 disabled:opacity-50 disabled:cursor-not-allowed"
                                     title="Go to next step"
                                   >
                                     Next →
                                   </button>
                                 </div>
                               )}

                               {/* Refresh Button */}
                               <button
                                 onClick={(e) => {
                                   e.stopPropagation();
                                   generateWorkflowPreview();
                                 }}
                                 disabled={isPreviewLoading || workflowSteps.length === 0}
                                 className="p-2 text-green-600 hover:text-green-800 hover:bg-green-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                 title="Refresh preview"
                               >
                                 <RefreshCw className={`w-4 h-4 ${isPreviewLoading ? 'animate-spin' : ''}`} />
                               </button>
                             </>
                           )}
                         </div>
                       </div>
                     </div>

                     {/* Preview Content */}
                     {previewMode === 'structure' ? (
                                 // File Structure Tab
                                   <div className="h-full flex flex-col min-h-0">
              
              {/* Columns Display - Only show when files are imported */}
              {importedFiles.length > 0 ? (
                  <div className="relative w-full flex-1 min-h-0">
                    <div className="absolute inset-0 overflow-x-auto overflow-y-auto data-preview-scrollbar border-2 border-gray-200 rounded-lg bg-gray-50">
                      <div className="flex space-x-4 p-3 h-full" style={{ width: 'max-content' }}>
                      {importedFiles.map((file) => renderFileColumns(file))}
                    </div>
                  </div>
                </div>
              ) : (
                  <div className="text-center text-gray-500 text-sm flex-1 flex items-center justify-center min-h-0">
                    <div className="flex flex-col items-center justify-center">
                      <Eye className="w-8 h-8 mb-2 text-gray-300" />
                      <p className="text-sm font-medium">Import files to see data preview</p>
                      <p className="text-xs text-gray-400 mt-1">Use the import button in Data Sources panel</p>
                  </div>
                  </div>
                )}
                </div>
              ) : (
                // Live Preview Tab
                <div className="flex-1">
                  <LivePreview
                    workflowSteps={workflowSteps}
                    importedFiles={importedFiles}
                    sampleSize={sampleSize}
                    isExecuting={isExecuting}
                    previewResultMode={previewResultMode}
                    onPreviewResultModeChange={setPreviewResultMode}
                    currentStepIndex={currentStepIndex}
                    selectedColumnsPreview={selectedColumnsPreview}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Execution Status */}
        {/* Removed execution status section as workflow builder is removed */}
      </div>
      
      {/* Header Configuration Modal */}
      {showHeaderConfig && selectedFileForHeader && (
        <div className="fixed inset-0 z-50 flex items-center justify-center modal-overlay">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 modal-content">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                Header Configuration
                {selectedFileForHeader.currentSheet && (
                  <span className="text-sm font-normal text-gray-600 ml-2">
                    - {selectedFileForHeader.currentSheet}
                  </span>
                )}
              </h3>
              <button
                onClick={() => {
                  setShowHeaderConfig(false);
                  setSelectedFileForHeader(null);
                }}
                className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-gray-100 rounded-md"
                title="Close configuration"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4 space-y-4">
              {/* Header Row Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Header Row:</label>
                <select 
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={headerRow}
                  onChange={(e) => setHeaderRow(parseInt(e.target.value))}
                >
                  <option value={1}>Row 1</option>
                  <option value={2}>Row 2</option>
                  <option value={3}>Row 3</option>
                  <option value={4}>Row 4</option>
                  <option value={5}>Row 5</option>
                </select>
              </div>
              
              {/* Merged Headers Toggle */}
              <div>
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={isMergedHeaders}
                    onChange={(e) => setIsMergedHeaders(e.target.checked)}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700">Merged Headers</span>
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  Enable if headers span multiple columns
                </p>
              </div>
              
              {/* Custom Headers Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Custom Headers (comma-separated):</label>
                <input
                  type="text"
                  placeholder="col1, col2, col3..."
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={customHeaders.join(', ')}
                  onChange={(e) => setCustomHeaders(e.target.value.split(',').map(h => h.trim()).filter(h => h))}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Leave empty to use auto-detected headers
                </p>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 p-4 border-t border-gray-200">
              <button
                onClick={() => {
                  setShowHeaderConfig(false);
                  setSelectedFileForHeader(null);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => updateHeaderConfig(selectedFileForHeader)}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
              >
                Apply Configuration
              </button>
            </div>
          </div>
        </div>
      )}

                   {/* Save Workflow Dialog */}
             <SaveWorkflowDialog
               isOpen={showSaveDialog}
               onClose={() => setShowSaveDialog(false)}
               onSave={handleSaveWorkflowTemplate}
               workflowSteps={workflowSteps}
               importedFiles={importedFiles}
               currentWorkflowName={workflowName}
             />

             {/* Execute Workflow Dialog */}
             <ExecuteWorkflowDialog
               isOpen={showExecuteDialog}
               onClose={() => setShowExecuteDialog(false)}
               onExecute={handleExecuteWorkflow}
               workflowSteps={workflowSteps}
               importedFiles={importedFiles}
               currentWorkflowName={workflowName}
             />

             {/* Hidden file input for file browsing */}
             <input
               ref={fileInputRef}
               type="file"
               multiple
               accept=".csv,.xlsx,.xls,.txt"
               onChange={(e) => {
                 const files = e.target.files;
                 if (files && files.length > 0) {
                   handleFileImport(files);
                 }
               }}
               onClick={(e) => {
                 // Prevent the click event from bubbling up
                 e.stopPropagation();
               }}
               className="hidden"
             />
      </div>
    </ErrorBoundary>
  );
};

export default Playground;

// Add custom CSS for the enhanced formula engine and workflow builder
const formulaEngineStyles = `

  
  .workflow-builder-scrollbar::-webkit-scrollbar {
    width: 8px;
  }
  
  .workflow-builder-scrollbar::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
  }
  
  .workflow-builder-scrollbar::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
  }
  
  .workflow-builder-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  .workflow-builder-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 #f1f5f9;
  }

  /* Strict width constraints for workflow builder */
  .workflow-builder-container {
    max-width: 50vw !important;
    width: 100% !important;
    overflow: hidden !important;
  }

  .workflow-builder-content {
    max-width: 100% !important;
    overflow-x: hidden !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
  }

  .workflow-builder-toolbar {
    max-width: 100% !important;
    overflow-x: hidden !important;
    flex-wrap: wrap !important;
  }

  /* Data Source drop area styling */
  .data-source-drop-area {
    min-height: 200px;
    border-radius: 8px;
    transition: all 0.2s ease-in-out;
  }

  .data-source-drop-area:hover {
    border-color: #60a5fa;
    background-color: #eff6ff;
  }

  /* Formula Engine container styling */
  .formula-engine-container {
    height: 100% !important;
    overflow: hidden !important;
  }

  .formula-engine-content {
    height: 100% !important;
    overflow: hidden !important;
  }

  /* Hide scrollbar for Formula Engine while maintaining scroll functionality */
  .formula-engine-content .overflow-y-auto::-webkit-scrollbar {
    display: none;
  }
  
  .formula-engine-content .overflow-y-auto {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }


  
  .formula-item {
    transition: all 0.2s ease-in-out;
    min-height: 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .formula-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  /* Formula tooltip styling */
  .formula-tooltip {
    animation: fadeIn 0.2s ease-in-out;
    pointer-events: none;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  /* Favorite star styling */
  .formula-item .star-favorite {
    color: #f59e0b;
    transition: all 0.2s ease-in-out;
    animation: starPop 0.3s ease-out;
  }

  .formula-item .star-favorite:hover {
    color: #d97706;
    transform: scale(1.1);
  }

  .formula-item .star-normal {
    color: #9ca3af;
    transition: all 0.2s ease-in-out;
  }

  .formula-item .star-normal:hover {
    color: #f59e0b;
    transform: scale(1.1);
  }

  @keyframes starPop {
    0% {
      transform: scale(0.8);
      opacity: 0.7;
    }
    50% {
      transform: scale(1.2);
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }
  
  .category-header {
    transition: background-color 0.2s ease-in-out;
  }
  
  .category-header:hover {
    background-color: #f8fafc;
  }
`;

// Inject styles into the document
if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style');
  styleElement.textContent = formulaEngineStyles;
  document.head.appendChild(styleElement);
} 