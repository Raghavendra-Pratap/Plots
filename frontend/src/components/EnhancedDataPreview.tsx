import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Eye, Loader2, Info, AlertCircle, CheckCircle, FileText } from 'lucide-react';

// Types for enhanced data preview
interface ColumnReference {
  displayName: string;        // "12474.csv ▸ Store" (UI display)
  columnName: string;         // "Store" (actual column name)
  fileName: string;           // "12474.csv" (file identifier)
  sheetName?: string;         // "Sheet1" (for Excel files)
  fullPath: string;           // "12474.csv ▸ Store" or "12474.csv ▸ Sheet1 ▸ Store"
  dataType?: 'numeric' | 'text' | 'date' | 'categorical' | 'boolean';
}

interface PlaygroundFile {
  name: string;
  type: string;
  size: number;
  columns: string[];
  sheets?: { [sheetName: string]: string[] };
  headerConfig?: {
    row: number;
    merged: boolean;
    customHeaders?: string[];
    autoDetected: boolean;
  };
  currentSheet?: string;
  data?: any[];
}

interface EnhancedDataPreviewProps {
  importedFiles: PlaygroundFile[];
  selectedColumns: string[];
  onColumnClick: (columnPath: string, file: PlaygroundFile) => void;
  currentFunctionStep?: {
    id: string;
    source: string;
    parameters?: string[];
  } | null;
  onParameterAdd?: (columnPath: string) => void;
}

const EnhancedDataPreview: React.FC<EnhancedDataPreviewProps> = ({
  importedFiles,
  selectedColumns,
  onColumnClick,
  currentFunctionStep,
  onParameterAdd
}) => {
  const [hoveredColumn, setHoveredColumn] = useState<string | null>(null);
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set());

  // Smart column type detection
  const detectColumnType = (column: string, data: any[]): 'numeric' | 'text' | 'date' | 'categorical' | 'boolean' => {
    if (!data || data.length === 0) return 'text';
    
    const sampleValues = data.slice(0, 100).map(row => row[column]).filter(val => val !== null && val !== undefined);
    if (sampleValues.length === 0) return 'text';
    
    // Check if numeric
    const numericCount = sampleValues.filter(val => !isNaN(Number(val)) && val !== '').length;
    if (numericCount / sampleValues.length > 0.8) return 'numeric';
    
    // Check if boolean
    const booleanValues = ['true', 'false', 'yes', 'no', '1', '0'];
    const booleanCount = sampleValues.filter(val => 
      booleanValues.includes(String(val).toLowerCase())
    ).length;
    if (booleanCount / sampleValues.length > 0.8) return 'boolean';
    
    // Check if date
    const dateCount = sampleValues.filter(val => {
      const date = new Date(val);
      return !isNaN(date.getTime()) && date.getFullYear() > 1900;
    }).length;
    if (dateCount / sampleValues.length > 0.7) return 'date';
    
    // Check if categorical (limited unique values)
    const uniqueValues = new Set(sampleValues.map(String)).size;
    if (uniqueValues / sampleValues.length < 0.3) return 'categorical';
    
    return 'text';
  };

  // Get column clickability status
  const getColumnClickability = (columnPath: string, file: PlaygroundFile) => {
    if (!currentFunctionStep) return 'disabled';
    
    const currentParams = currentFunctionStep.parameters?.length || 0;
    const maxParams = getMaxParametersForFunction(currentFunctionStep.source);
    
    if (currentParams >= maxParams) return 'maxed';
    if (currentFunctionStep.parameters?.includes(columnPath)) return 'already_selected';
    return 'clickable';
  };

  // Get maximum parameters for function
  const getMaxParametersForFunction = (functionName: string): number => {
    const maxParams = {
      'TEXT_JOIN': 10,
      'SUMIFS': 20,
      'PIVOT': 5,
      'VLOOKUP': 10,
      'IF': 5,
      'UPPER': 1,
      'LOWER': 1,
      'CONCATENATE': 10
    };
    
    return maxParams[functionName as keyof typeof maxParams] || 5;
  };

  // Get column tooltip content
  const getColumnTooltip = (columnPath: string, clickability: string, currentFunctionStep: any) => {
    const fileName = columnPath.split(' ▸ ')[0];
    const columnName = columnPath.split(' ▸ ').pop() || '';
    
    let tooltipContent = [
      `<strong>${columnName}</strong>`,
      `File: ${fileName}`,
      `Type: ${getColumnTypeDisplay(columnPath)}`
    ];
    
    if (clickability === 'clickable') {
      tooltipContent.push('Click to add as parameter');
    } else if (clickability === 'maxed') {
      tooltipContent.push('Maximum parameters reached');
    } else if (clickability === 'already_selected') {
      tooltipContent.push('Already selected');
    } else if (clickability === 'disabled') {
      tooltipContent.push('Select a function first');
    }
    
    return tooltipContent.join('\n');
  };

  // Get column type display
  const getColumnTypeDisplay = (columnPath: string): string => {
    const file = importedFiles.find(f => columnPath.includes(f.name));
    if (!file || !file.data) return 'Unknown';
    
    const columnName = columnPath.split(' ▸ ').pop() || '';
    const dataType = detectColumnType(columnName, file.data);
    
    const typeDisplay = {
      'numeric': 'Number',
      'text': 'Text',
      'date': 'Date',
      'categorical': 'Category',
      'boolean': 'Boolean'
    };
    
    return typeDisplay[dataType] || 'Unknown';
  };

  // Handle column click
  const handleColumnClick = (columnPath: string, file: PlaygroundFile) => {
    const clickability = getColumnClickability(columnPath, file);
    
    if (clickability === 'clickable') {
      if (currentFunctionStep && onParameterAdd) {
        onParameterAdd(columnPath);
      } else {
        onColumnClick(columnPath, file);
      }
    }
  };

  // Toggle file expansion
  const toggleFileExpansion = (fileName: string) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(fileName)) {
      newExpanded.delete(fileName);
    } else {
      newExpanded.add(fileName);
    }
    setExpandedFiles(newExpanded);
  };

  // Get column icon based on type
  const getColumnIcon = (columnPath: string) => {
    const file = importedFiles.find(f => columnPath.includes(f.name));
    if (!file || !file.data) return '📄';
    
    const columnName = columnPath.split(' ▸ ').pop() || '';
    const dataType = detectColumnType(columnName, file.data);
    
    const typeIcons = {
      'numeric': '🔢',
      'text': '📝',
      'date': '📅',
      'categorical': '🏷️',
      'boolean': '✅'
    };
    
    return typeIcons[dataType] || '📄';
  };

  // Get column status indicator
  const getColumnStatusIndicator = (columnPath: string) => {
    const clickability = getColumnClickability(columnPath, importedFiles.find(f => columnPath.includes(f.name))!);
    
    if (clickability === 'clickable') {
      return <span className="click-indicator">👆</span>;
    } else if (clickability === 'maxed') {
      return <span className="maxed-indicator">⛔</span>;
    } else if (clickability === 'already_selected') {
      return <span className="selected-indicator">✓</span>;
    } else {
      return <span className="disabled-indicator">🔒</span>;
    }
  };

  if (importedFiles.length === 0) {
    return (
      <Card className="h-full">
        <CardContent className="p-4 h-full flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center">
              <Eye className="w-4 h-4 mr-2" />
              Data Preview
            </h3>
          </div>
          
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No files imported yet</p>
              <p className="text-sm">Import files to see column previews</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardContent className="p-4 h-full flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold flex items-center">
            <Eye className="w-4 h-4 mr-2" />
            Data Preview
          </h3>
          
          {/* Selection Mode Indicator */}
          <div className="selection-mode">
            {currentFunctionStep ? (
              <div className="mode-active">
                <span className="mode-icon">🎯</span>
                <span className="mode-text">
                  Click columns to add to {currentFunctionStep.source}
                </span>
                <span className="param-count">
                  ({currentFunctionStep.parameters?.length || 0}/{getMaxParametersForFunction(currentFunctionStep.source)})
                </span>
              </div>
            ) : (
              <div className="mode-inactive">
                <span className="mode-icon">👆</span>
                <span className="mode-text">Select a function to start adding parameters</span>
              </div>
            )}
          </div>
        </div>
        
        {/* Files and Columns */}
        <div className="flex-1 overflow-y-auto space-y-4">
          {importedFiles.map((file) => {
            const isExpanded = expandedFiles.has(file.name);
            const hasMultipleSheets = file.sheets && Object.keys(file.sheets).length > 1;
            
            return (
              <div key={file.name} className="file-section">
                {/* File Header */}
                <div className="file-header">
                  <button
                    onClick={() => toggleFileExpansion(file.name)}
                    className="file-toggle"
                  >
                    <span className={`toggle-icon ${isExpanded ? 'expanded' : ''}`}>
                      {isExpanded ? '▼' : '▶'}
                    </span>
                    <span className="file-name">{file.name}</span>
                    <span className="file-info">
                      ({file.columns.length} columns)
                    </span>
                  </button>
                </div>
                
                {/* File Content */}
                {isExpanded && (
                  <div className="file-content">
                    {hasMultipleSheets ? (
                      // Multiple sheets (Excel)
                      Object.entries(file.sheets || {}).map(([sheetName, columns]) => (
                        <div key={sheetName} className="sheet-section">
                          <div className="sheet-header">
                            <span className="sheet-icon">📊</span>
                            <span className="sheet-name">{sheetName}</span>
                            <span className="sheet-info">({columns.length} columns)</span>
                          </div>
                          
                          <div className="columns-grid">
                            {columns.map((column, colIndex) => {
                              const columnPath = `${file.name} ▸ ${sheetName} ▸ ${column}`;
                              const clickability = getColumnClickability(columnPath, file);
                              const isHovered = hoveredColumn === columnPath;
                              
                              return (
                                <div 
                                  key={colIndex}
                                  className={`column-item ${clickability} ${isHovered ? 'hovered' : ''}`}
                                  onClick={() => handleColumnClick(columnPath, file)}
                                  onMouseEnter={() => setHoveredColumn(columnPath)}
                                  onMouseLeave={() => setHoveredColumn(null)}
                                  title={getColumnTooltip(columnPath, clickability, currentFunctionStep)}
                                >
                                  <div className="column-content">
                                    <span className="column-icon">
                                      {getColumnIcon(columnPath)}
                                    </span>
                                    <span className="column-name">{column}</span>
                                    <span className="column-type">
                                      {getColumnTypeDisplay(columnPath)}
                                    </span>
                                    
                                    {/* Visual Indicators */}
                                    {clickability === 'clickable' && (
                                      <div className="click-indicators">
                                        {getColumnStatusIndicator(columnPath)}
                                        {isHovered && (
                                          <div className="hover-effect">
                                            <span className="pulse-ring"></span>
                                          </div>
                                        )}
                                      </div>
                                    )}
                                    
                                    {clickability === 'maxed' && (
                                      <span className="maxed-indicator">⛔</span>
                                    )}
                                    
                                    {clickability === 'already_selected' && (
                                      <span className="selected-indicator">✓</span>
                                    )}
                                    
                                    {clickability === 'disabled' && (
                                      <span className="disabled-indicator">🔒</span>
                                    )}
                                  </div>
                                  
                                  {/* Hover Tooltip */}
                                  {isHovered && (
                                    <div className="column-tooltip">
                                      <div className="tooltip-content">
                                        <strong>{column}</strong>
                                        <span>File: {file.name}</span>
                                        <span>Sheet: {sheetName}</span>
                                        <span>Type: {getColumnTypeDisplay(columnPath)}</span>
                                        {clickability === 'clickable' && (
                                          <span className="action-hint">Click to add as parameter</span>
                                        )}
                                        {clickability === 'maxed' && (
                                          <span className="warning">Maximum parameters reached</span>
                                        )}
                                        {clickability === 'already_selected' && (
                                          <span className="info">Already selected</span>
                                        )}
                                        {clickability === 'disabled' && (
                                          <span className="info">Select a function first</span>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))
                    ) : (
                      // Single file (CSV or single sheet Excel)
                      <div className="columns-grid">
                        {file.columns.map((column, colIndex) => {
                          const columnPath = `${file.name} ▸ ${column}`;
                          const clickability = getColumnClickability(columnPath, file);
                          const isHovered = hoveredColumn === columnPath;
                          
                          return (
                            <div 
                              key={colIndex}
                              className={`column-item ${clickability} ${isHovered ? 'hovered' : ''}`}
                              onClick={() => handleColumnClick(columnPath, file)}
                              onMouseEnter={() => setHoveredColumn(columnPath)}
                              onMouseLeave={() => setHoveredColumn(null)}
                              title={getColumnTooltip(columnPath, clickability, currentFunctionStep)}
                            >
                              <div className="column-content">
                                <span className="column-icon">
                                  {getColumnIcon(columnPath)}
                                </span>
                                <span className="column-name">{column}</span>
                                <span className="column-type">
                                  {getColumnTypeDisplay(columnPath)}
                                </span>
                                
                                {/* Visual Indicators */}
                                {clickability === 'clickable' && (
                                  <div className="click-indicators">
                                    {getColumnStatusIndicator(columnPath)}
                                    {isHovered && (
                                      <div className="hover-effect">
                                        <span className="pulse-ring"></span>
                                      </div>
                                    )}
                                  </div>
                                )}
                                
                                {clickability === 'maxed' && (
                                  <span className="maxed-indicator">⛔</span>
                                )}
                                
                                {clickability === 'already_selected' && (
                                  <span className="selected-indicator">✓</span>
                                )}
                                
                                {clickability === 'disabled' && (
                                  <span className="disabled-indicator">🔒</span>
                                )}
                              </div>
                              
                              {/* Hover Tooltip */}
                              {isHovered && (
                                <div className="column-tooltip">
                                  <div className="tooltip-content">
                                    <strong>{column}</strong>
                                    <span>File: {file.name}</span>
                                    <span>Type: {getColumnTypeDisplay(columnPath)}</span>
                                    {clickability === 'clickable' && (
                                      <span className="action-hint">Click to add as parameter</span>
                                    )}
                                    {clickability === 'maxed' && (
                                      <span className="warning">Maximum parameters reached</span>
                                    )}
                                    {clickability === 'already_selected' && (
                                      <span className="info">Already selected</span>
                                    )}
                                    {clickability === 'disabled' && (
                                      <span className="info">Select a function first</span>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedDataPreview;
