import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import DataSources from './DataSources';
import LivePreview from './LivePreview';
import { 
  Upload, Database, GitBranch, BarChart2, Download, 
  Settings, Filter, Edit3, Eye, AlertCircle, Play
} from 'lucide-react';

interface FileData {
  name: string;
  type: string;
  size: number;
  columns: string[];
  path: string;
  lastModified: Date;
  sheets?: { [sheetName: string]: string[] };
  headerConfig?: {
    row: number;
    merged: boolean;
    customHeaders?: string[];
    autoDetected: boolean;
  };
  currentSheet?: string;
}

interface DataOperation {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  parameters: Record<string, any>;
}

interface WorkspaceProps {
  activeStep: string;
  setActiveStep: (step: string) => void;
  importedFiles: FileData[];
  selectedOperation: DataOperation | null;
  handleDataOperation: (operation: DataOperation) => void;
  handleBrowseFiles: () => void;
  handleDragDropImport: (files: FileList) => void;
  handleDeleteFile?: (fileName: string) => void;
  dataSourceHeight: number;
  previewHeight: number;
  dataPreviewHeight: number;
  selectedColumns: string[];
  selectedFiles: string[];
  handleColumnClick: (columnPath: string) => void;
  handleFileClick: (fileName: string) => void;
  collapsedSheets: { [key: string]: boolean };
  toggleSheetCollapse: (fileKey: string) => void;
  renderFileColumns: (file: FileData) => React.ReactNode;
  lastSaved: Date;
  formatTimeAgo: (date: Date) => string;
  handleSaveChanges: () => void;
  ArrowLeft: React.ComponentType<{ className?: string }>;
  onNavigateToPlayground?: () => void;
}

const Workspace: React.FC<WorkspaceProps> = ({
  activeStep,
  setActiveStep,
  importedFiles,
  selectedOperation,
  handleDataOperation,
  handleBrowseFiles,
  handleDragDropImport,
  handleDeleteFile,
  dataSourceHeight,
  previewHeight,
  dataPreviewHeight,
  selectedColumns,
  selectedFiles,
  handleColumnClick,
  handleFileClick,
  collapsedSheets,
  toggleSheetCollapse,
  renderFileColumns,
  lastSaved,
  formatTimeAgo,
  handleSaveChanges,
  ArrowLeft,
  onNavigateToPlayground
}) => {
  // Dynamic height calculation for 50/50 split
  const [windowHeight, setWindowHeight] = React.useState(window.innerHeight);
  
  // Preview mode state (icon-based toggle instead of tabs)
  const [previewMode, setPreviewMode] = useState<'structure' | 'live'>('structure');
  
  // Live Preview state
  const [sampleSize, setSampleSize] = useState<10 | 50 | 100>(50);
  
  React.useEffect(() => {
    const handleResize = () => setWindowHeight(window.innerHeight);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Calculate heights dynamically - 50% for top section, 50% for data preview
  const topSectionHeight = Math.floor((windowHeight - 200) * 0.5); // 50% for top section
  const bottomSectionHeight = Math.floor((windowHeight - 200) * 0.5); // 50% for data preview
  const steps = [
    { id: 'import', icon: Upload, label: 'Import' },
    { id: 'clean', icon: Database, label: 'Clean' },
    { id: 'transform', icon: GitBranch, label: 'Transform' },
    { id: 'analyze', icon: BarChart2, label: 'Analyze' },
    { id: 'export', icon: Download, label: 'Export' }
  ];

  // Data cleaning tools
  const cleaningTools: DataOperation[] = [
    { id: 'remove_duplicates', name: 'Remove Duplicates', description: 'Remove duplicate rows based on selected columns', icon: Filter, parameters: {} },
    { id: 'fix_missing', name: 'Fix Missing Values', description: 'Fill or remove missing values in columns', icon: Database, parameters: {} },
    { id: 'standardize', name: 'Standardize Format', description: 'Standardize data formats and values', icon: Edit3, parameters: {} },
    { id: 'filter_data', name: 'Filter Data', description: 'Filter rows based on conditions', icon: Filter, parameters: {} }
  ];

  // Transformation tools
  const transformationTools: DataOperation[] = [
    { id: 'join_datasets', name: 'Join Datasets', description: 'Combine multiple datasets', icon: GitBranch, parameters: {} },
    { id: 'aggregate_data', name: 'Aggregate Data', description: 'Group and summarize data', icon: BarChart2, parameters: {} },
    { id: 'split_columns', name: 'Split Columns', description: 'Split columns into multiple parts', icon: GitBranch, parameters: {} },
    { id: 'format_values', name: 'Format Values', description: 'Format and transform column values', icon: Edit3, parameters: {} }
  ];

  // Analysis tools
  const analysisTools: DataOperation[] = [
    { id: 'basic_stats', name: 'Basic Statistics', description: 'Calculate mean, median, standard deviation', icon: BarChart2, parameters: {} },
    { id: 'data_quality', name: 'Data Quality Report', description: 'Generate data quality assessment', icon: Eye, parameters: {} },
    { id: 'correlation', name: 'Correlation Analysis', description: 'Find correlations between columns', icon: BarChart2, parameters: {} },
    { id: 'outlier_detection', name: 'Outlier Detection', description: 'Identify and handle outliers', icon: AlertCircle, parameters: {} }
  ];

  // Export options
  const exportOptions: DataOperation[] = [
    { id: 'export_csv', name: 'Export to CSV', description: 'Save data as CSV file', icon: Download, parameters: {} },
    { id: 'export_excel', name: 'Export to Excel', description: 'Save data as Excel file', icon: Download, parameters: {} },
    { id: 'export_json', name: 'Export to JSON', description: 'Save data as JSON file', icon: Download, parameters: {} },
    { id: 'save_workflow', name: 'Save as Workflow', description: 'Save current operations as reusable workflow', icon: Download, parameters: {} }
  ];

  return (
    <div className="flex-1 flex flex-col">
      {/* Workflow Steps */}
      <div className="bg-white border-b">
        <div className="flex justify-between px-6 py-3">
          {steps.map((step) => (
            <div
              key={step.id}
              onClick={() => setActiveStep(step.id)}
              className={`flex flex-col items-center p-3 cursor-pointer rounded-lg transition-colors
                ${activeStep === step.id ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50'}`}
            >
              <step.icon className="w-5 h-5 mb-1" />
              <span className="text-sm">{step.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Workspace Content */}
      <div className="flex-1 p-6 overflow-hidden">
        <div className="grid grid-cols-12 gap-6 top-section-container" style={{ height: `${topSectionHeight -10 }px` }}>
          {activeStep === 'import' && (
            <>
              {/* Left Panel - Data Sources */}
              <div className="col-span-3 h-full">
                <DataSources
                  importedFiles={importedFiles}
                  onBrowseFiles={handleBrowseFiles}
                  onDragDropImport={handleDragDropImport}
                  onDeleteFile={handleDeleteFile}
                  height={topSectionHeight - 10}
                  showDeleteButton={true}
                  showHeaderConfig={true}
                />
              </div>

              {/* Center Panel - Import Tools */}
              <Card className="col-span-6 h-full">
                <CardContent className="p-4 h-full flex flex-col">
                  <h3 className="font-semibold mb-4 flex-shrink-0">Import Options</h3>
                  <div className="flex-1 overflow-y-auto pr-2">
                    <div className="grid grid-cols-2 gap-4">
                      <div 
                        onClick={() => handleBrowseFiles()}
                        className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 border border-transparent hover:border-blue-200"
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <Upload className="w-5 h-5 text-blue-600" />
                          <h4 className="text-sm font-medium text-gray-900">Browse Files</h4>
                        </div>
                        <p className="text-sm text-gray-600">Select files from your computer</p>
                      </div>
                      <div 
                        className="p-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors"
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
                          if (e.dataTransfer.files.length > 0) {
                            handleDragDropImport(e.dataTransfer.files);
                          }
                        }}
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <Upload className="w-5 h-5 text-blue-600" />
                          <h4 className="text-sm font-medium text-gray-900">Drag & Drop</h4>
                        </div>
                        <p className="text-sm text-gray-600">Drop files here to import</p>
                      </div>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Upload className="w-5 h-5 text-blue-600" />
                          <h4 className="text-sm font-medium text-gray-900">From URL</h4>
                        </div>
                        <p className="text-sm text-gray-600">Import from web URL</p>
                      </div>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Database className="w-5 h-5 text-blue-600" />
                          <h4 className="text-sm font-medium text-gray-900">Database</h4>
                        </div>
                        <p className="text-sm text-gray-600">Connect to database</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Right Panel - Import Properties */}
              <Card className="col-span-3 h-full">
                <CardContent className="p-4 h-full flex flex-col">
                  <h3 className="font-semibold mb-4 flex items-center flex-shrink-0">
                    <Settings className="w-4 h-4 mr-2" />
                    Import Properties
                  </h3>
                  <div className="flex-1 overflow-y-auto pr-2">
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium">File Encoding</label>
                        <select className="w-full p-2 border rounded-md bg-white mt-1">
                          <option>Auto-detect</option>
                          <option>UTF-8</option>
                          <option>ISO-8859-1</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Delimiter</label>
                        <select className="w-full p-2 border rounded-md bg-white mt-1">
                          <option>Auto-detect</option>
                          <option>Comma (,)</option>
                          <option>Semicolon (;)</option>
                          <option>Tab</option>
                        </select>
                      </div>
                      <div>
                        <label className="text-sm font-medium">First Row as Headers</label>
                        <input type="checkbox" defaultChecked className="ml-2" />
                      </div>
                    </div>
                  </div>
                  <div className="flex-shrink-0 pt-3">
                    <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      Import Files
                    </button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}

        {activeStep === 'clean' && (
          <>
            {/* Left Panel - Data Sources */}
            <div className="col-span-3 h-full">
              <DataSources
                importedFiles={importedFiles}
                onBrowseFiles={handleBrowseFiles}
                onDragDropImport={handleDragDropImport}
                onDeleteFile={handleDeleteFile}
                height={topSectionHeight - 10}
                showDeleteButton={true}
                showHeaderConfig={true}
              />
            </div>

            {/* Center Panel - Cleaning Tools */}
            <Card className="col-span-6 h-full">
              <CardContent className="p-4 h-full flex flex-col">
                <h3 className="font-semibold mb-4 flex-shrink-0">Data Cleaning Tools</h3>
                <div className="flex-1 overflow-y-auto pr-2">
                  <div className="grid grid-cols-2 gap-4">
                    {cleaningTools.map((tool) => (
                      <div 
                        key={tool.id}
                        onClick={() => handleDataOperation(tool)}
                        className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 border border-transparent hover:border-blue-200"
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <tool.icon className="w-5 h-5 text-blue-600" />
                          <h4 className="text-sm font-medium text-gray-900">{tool.name}</h4>
                        </div>
                        <p className="text-sm text-gray-600">{tool.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Right Panel - Cleaning Properties */}
            <Card className="col-span-3 h-full">
              <CardContent className="p-4 h-full flex flex-col">
                <h3 className="font-semibold mb-4 flex items-center flex-shrink-0">
                  <Settings className="w-4 h-4 mr-2" />
                  Cleaning Properties
                </h3>
                <div className="flex-1 overflow-y-auto pr-2">
                  {selectedOperation ? (
                    <div className="space-y-4">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900">{selectedOperation.name}</h4>
                        <p className="text-sm text-blue-700 mt-1">{selectedOperation.description}</p>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Target Columns</label>
                        <select className="w-full p-2 border rounded-md bg-white">
                          <option>All columns</option>
                          {importedFiles.flatMap(f => f.columns).map(col => (
                            <option key={col}>{col}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 text-sm p-4">
                      Select a cleaning tool to configure properties
                    </div>
                  )}
                </div>
                {selectedOperation && (
                  <div className="flex-shrink-0 pt-3">
                    <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      Apply Cleaning
                    </button>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}

        {activeStep === 'transform' && (
          <>
            {/* Left Panel - Available Datasets */}
            <div className="col-span-3 h-full">
              <DataSources
                importedFiles={importedFiles}
                onBrowseFiles={handleBrowseFiles}
                onDragDropImport={handleDragDropImport}
                onDeleteFile={handleDeleteFile}
                height={topSectionHeight - 10}
                showDeleteButton={true}
                showHeaderConfig={true}
              />
            </div>

            {/* Center Panel - Transformation Tools */}
            <Card className="col-span-6 h-full">
              <CardContent className="p-4 h-full flex flex-col">
                <h3 className="font-semibold mb-4 flex-shrink-0">Transformation Options</h3>
                <div className="flex-1 overflow-y-auto pr-2">
                  <div className="grid grid-cols-2 gap-4">
                    {transformationTools.map((tool) => (
                      <div 
                        key={tool.id}
                        onClick={() => handleDataOperation(tool)}
                        className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 border border-transparent hover:border-blue-200"
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <tool.icon className="w-5 h-5 text-blue-600" />
                          <h4 className="font-medium text-gray-900">{tool.name}</h4>
                        </div>
                        <p className="text-sm text-gray-600">{tool.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Right Panel - Transformation Properties */}
            <Card className="col-span-3 h-full">
              <CardContent className="p-4 h-full flex flex-col">
                <h3 className="font-semibold mb-4 flex items-center flex-shrink-0">
                  <Settings className="w-4 h-4 mr-2" />
                  Transformation Properties
                </h3>
                <div className="flex-1 overflow-y-auto pr-2">
                  {selectedOperation ? (
                    <div className="space-y-4">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900">{selectedOperation.name}</h4>
                        <p className="text-sm text-blue-700 mt-1">{selectedOperation.description}</p>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Join Type</label>
                        <select className="w-full p-2 border rounded-md bg-white">
                          <option>Inner Join</option>
                          <option>Left Join</option>
                          <option>Right Join</option>
                          <option>Outer Join</option>
                        </select>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 text-sm p-4">
                      Select a transformation to configure properties
                    </div>
                  )}
                </div>
                {selectedOperation && (
                  <div className="flex-shrink-0 pt-3">
                    <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      Apply Transformation
                    </button>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}

        {activeStep === 'analyze' && (
          <>
            {/* Left Panel - Data Overview */}
            <Card className="col-span-3 h-full">
              <CardContent className="p-4 h-full">
                <h3 className="font-semibold mb-4 flex items-center">
                  <BarChart2 className="w-4 h-4 mr-2" />
                  Data Overview
                </h3>
                <div className="space-y-3">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {importedFiles.reduce((total, f) => total + f.columns.length, 0)}
                    </div>
                    <div className="text-sm text-blue-600">Total Columns</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {importedFiles.length}
                    </div>
                    <div className="text-sm text-green-600">Datasets</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Center Panel - Analysis Tools */}
            <Card className="col-span-6 h-full">
              <CardContent className="p-4 h-full flex flex-col">
                <h3 className="font-semibold mb-4 flex-shrink-0">Analysis Tools</h3>
                <div className="flex-1 overflow-y-auto pr-2">
                  <div className="grid grid-cols-2 gap-4">
                    {analysisTools.map((tool) => (
                      <div 
                        key={tool.id}
                        onClick={() => handleDataOperation(tool)}
                        className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 border border-transparent hover:border-blue-200"
                      >
                        <div className="flex items-center space-x-2 mb-2">
                          <tool.icon className="w-5 h-5 text-blue-600" />
                          <h4 className="font-medium text-gray-900">{tool.name}</h4>
                        </div>
                        <p className="text-sm text-gray-600">{tool.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Right Panel - Analysis Properties */}
            <Card className="col-span-3 h-full">
              <CardContent className="p-4 h-full">
                <h3 className="font-semibold mb-4 flex items-center">
                  <Settings className="w-4 h-4 mr-2" />
                  Analysis Properties
                </h3>
                {selectedOperation ? (
                  <div className="space-y-4">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900">{selectedOperation.name}</h4>
                      <p className="text-sm text-blue-700 mt-1">{selectedOperation.description}</p>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Target Columns</label>
                      <select className="w-full p-2 border rounded-md bg-white">
                        <option>All numeric columns</option>
                        {importedFiles.flatMap(f => f.columns).map(col => (
                          <option key={col}>{col}</option>
                        ))}
                      </select>
                    </div>
                    <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      Run Analysis
                    </button>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 text-sm p-4">
                    Select an analysis tool to configure properties
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}

        {activeStep === 'export' && (
          <>
            {/* Left Panel - Export Summary */}
            <Card className="col-span-3 h-full">
              <CardContent className="p-4 h-full">
                <h3 className="font-semibold mb-4 flex items-center">
                  <Download className="w-4 h-4 mr-2" />
                  Export Summary
                </h3>
                <div className="space-y-3">
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {importedFiles.length}
                    </div>
                    <div className="text-sm text-green-600">Processed Files</div>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {importedFiles.reduce((total, f) => total + f.size, 0) / 1024} KB
                    </div>
                    <div className="text-sm text-blue-600">Total Data</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Center Panel - Export Options */}
            <Card className="col-span-6 h-full">
              <CardContent className="p-4 h-full">
                <h3 className="font-semibold mb-4">Export Options</h3>
                <div className="grid grid-cols-2 gap-4">
                  {exportOptions.map((tool) => (
                    <div 
                      key={tool.id}
                      onClick={() => handleDataOperation(tool)}
                      className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 border border-transparent hover:border-blue-200"
                    >
                      <div className="flex items-center space-x-2 mb-2">
                        <tool.icon className="w-5 h-5 text-blue-600" />
                        <h4 className="font-medium text-gray-900">{tool.name}</h4>
                      </div>
                      <p className="text-sm text-gray-600">{tool.description}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Right Panel - Export Properties */}
            <Card className="col-span-3 h-full">
              <CardContent className="p-4 h-full flex flex-col">
                <h3 className="font-semibold mb-4 flex items-center flex-shrink-0">
                  <Settings className="w-4 h-4 mr-2" />
                  Export Properties
                </h3>
                <div className="flex-1 overflow-y-auto pr-2">
                  {selectedOperation ? (
                    <div className="space-y-4">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900">{selectedOperation.name}</h4>
                        <p className="text-sm text-blue-700 mt-1">{selectedOperation.description}</p>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">File Name</label>
                        <input 
                          type="text" 
                          className="w-full p-2 border rounded-md" 
                          placeholder="exported_data" 
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Include Headers</label>
                        <input type="checkbox" defaultChecked className="ml-2" />
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 text-sm p-4">
                      Select an export option to configure properties
                    </div>
                  )}
                </div>
                {selectedOperation && (
                  <div className="flex-shrink-0 pt-3">
                    <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                      Export Data
                    </button>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}
        </div>
      </div>

      {/* Clear separation line */}
      <div className="w-full h-px bg-gray-300 my-2"></div>

      {/* Data Preview Section - Dynamic Height (50% of screen) */}
      <div className="mt-2 data-preview-section" style={{ height: `${bottomSectionHeight}px` }}>
        <Card className="h-full">
          <CardContent className="p-3 h-full">
            {/* Preview Header with Mode Toggle */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-4">
                <h3 className="font-semibold flex items-center">
                  <Eye className="w-4 h-4 mr-2" />
                  Data Preview
                </h3>
                
                {/* Preview Mode Toggle */}
                <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setPreviewMode('structure')}
                    className={`p-2 rounded-md transition-colors ${
                      previewMode === 'structure' 
                        ? 'bg-white text-blue-600 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                    title="File Structure View"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setPreviewMode('live')}
                    className={`p-2 rounded-md transition-colors ${
                      previewMode === 'live' 
                        ? 'bg-white text-green-600 shadow-sm' 
                        : 'text-gray-600 hover:text-gray-800'
                    }`}
                    title="Live Preview"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                </div>
                
                {/* Sample Size Selector for Live Preview */}
                {previewMode === 'live' && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">Sample:</span>
                    <select
                      value={sampleSize}
                      onChange={(e) => setSampleSize(Number(e.target.value) as 10 | 50 | 100)}
                      className="text-sm border rounded px-2 py-1 bg-white"
                    >
                      <option value={10}>10 rows</option>
                      <option value={50}>50 rows</option>
                      <option value={100}>100 rows</option>
                    </select>
                  </div>
                )}
              </div>
              
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  {importedFiles.length} file{importedFiles.length !== 1 ? 's' : ''} selected
                </span>
                <span className="text-sm text-gray-600">Last saved: {formatTimeAgo(lastSaved)}</span>
                {(selectedColumns.length > 0 || selectedFiles.length > 0) && (
                  <button 
                    onClick={() => {
                      // Clear selections logic would go here
                    }}
                    className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-sm transition-colors"
                  >
                    Clear All
                  </button>
                )}
                <button 
                  onClick={onNavigateToPlayground || handleSaveChanges}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
                  title="Save changes and go to Playground"
                >
                  <span>Save & Go to Playground</span>
                  <ArrowLeft className="w-4 h-4 rotate-180" />
                </button>
              </div>
            </div>
            
            {/* Preview Content */}
            {previewMode === 'structure' ? (
              // File Structure Tab
              <div className="h-full flex flex-col">
                {/* Columns Display - Only show when files are imported */}
                {importedFiles.length > 0 ? (
                  <div className="relative w-full" style={{ height: 'calc(100% - 2.5rem)' }}>
                    <div className="absolute inset-0 overflow-x-auto overflow-y-hidden data-preview-scrollbar border-2 border-gray-200 rounded-lg bg-gray-50">
                      <div className="flex space-x-4 p-3" style={{ width: 'max-content', minHeight: '100%', height: '100%' }}>
                        {importedFiles.map((file) => renderFileColumns(file))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-gray-500 text-sm" style={{ height: 'calc(100% - 5.5rem)' }}>
                    <div className="flex flex-col items-center justify-center h-full">
                      <Eye className="w-10 h-10 mb-2 text-gray-300" />
                      <p className="text-base font-medium">Import files to see data preview</p>
                      <p className="text-xs text-gray-400 mt-1">Use the import button in Data Sources panel</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              // Live Preview Tab
              <div className="h-full">
                <LivePreview
                  workflowSteps={[]} // Empty for now since Workspace doesn't have workflow steps
                  importedFiles={importedFiles}
                  sampleSize={sampleSize}
                  isExecuting={false}
                  previewResultMode={'final'}
                  onPreviewResultModeChange={() => {}} // No-op for now
                  currentStepIndex={0}
                />
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Workspace;
