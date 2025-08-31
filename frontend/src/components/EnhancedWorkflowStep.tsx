import React, { useState, useEffect } from 'react';
import { 
  Edit3, 
  Trash2, 
  CheckCircle, 
  AlertCircle, 
  Info,
  Lightbulb,
  X,
  Plus,
  Minus
} from 'lucide-react';

// Types for enhanced workflow steps
interface ColumnReference {
  displayName: string;        // "12474.csv ▸ Store" (UI display)
  columnName: string;         // "Store" (actual column name)
  fileName: string;           // "12474.csv" (file identifier)
  sheetName?: string;         // "Sheet1" (for Excel files)
  fullPath: string;           // "12474.csv ▸ Store" or "12474.csv ▸ Sheet1 ▸ Store"
}

interface WorkflowStep {
  id: string;
  type: 'column' | 'function' | 'break' | 'custom' | 'sheet';
  source: string;
  target?: string;
  sheet?: string;
  parameters?: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  columnReference?: ColumnReference;
}

interface EnhancedWorkflowStepProps {
  step: WorkflowStep;
  index: number;
  isActive: boolean;
  onEdit: (stepId: string) => void;
  onDelete: (stepId: string) => void;
  onReorder: (draggedId: string, targetId: string) => void;
  onParametersChange: (stepId: string, parameters: string[]) => void;
  onOutputChange: (stepId: string, output: string) => void;
}

const EnhancedWorkflowStep: React.FC<EnhancedWorkflowStepProps> = ({
  step,
  index,
  isActive,
  onEdit,
  onDelete,
  onReorder,
  onParametersChange,
  onOutputChange
}) => {
  const [selectedParams, setSelectedParams] = useState<string[]>(step.parameters || []);
  const [outputColumnName, setOutputColumnName] = useState(step.target || '');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Auto-suggest output column names
  const getOutputColumnSuggestions = (functionName: string, parameters: string[]) => {
    const suggestions = {
      'TEXT_JOIN': [
        'Combined_Text',
        'Full_Name',
        'Address_Complete',
        'Description_Combined'
      ],
      'SUMIFS': [
        'Sum_Result',
        'Total_Amount',
        'Aggregated_Value',
        'Calculated_Sum'
      ],
      'PIVOT': [
        'Pivot_Table',
        'Summary_Data',
        'Aggregated_Table',
        'Grouped_Results'
      ],
      'VLOOKUP': [
        'Lookup_Result',
        'Found_Value',
        'Reference_Data',
        'Matched_Value'
      ],
      'IF': [
        'Conditional_Result',
        'If_Output',
        'Condition_Result',
        'Logical_Output'
      ],
      'UPPER': [
        'Uppercase_Text',
        'Upper_Result',
        'Capitalized_Text'
      ],
      'LOWER': [
        'Lowercase_Text',
        'Lower_Result',
        'Small_Text'
      ],
      'CONCATENATE': [
        'Combined_Text',
        'Joined_Text',
        'Merged_Text'
      ]
    };
    
    return suggestions[functionName as keyof typeof suggestions] || ['Output_Column'];
  };

  const suggestions = getOutputColumnSuggestions(step.source, selectedParams);

  // Function-specific hints and warnings
  const getFunctionHints = (functionName: string, parameters: string[]) => {
    const hints = {
      'TEXT_JOIN': {
        description: 'Combines multiple columns into one',
        steps: [
          '1. Click the columns you want to join',
          '2. Choose a separator (space, comma, etc.)',
          '3. Set output column name'
        ],
        typicalParams: 2,
        maxParams: 10,
        example: 'First Name + Last Name = Full Name'
      },
      'SUMIFS': {
        description: 'Sums values based on conditions',
        steps: [
          '1. Click the column you want to sum',
          '2. Click the columns to filter by',
          '3. Set output column name'
        ],
        typicalParams: 3,
        maxParams: 20,
        example: 'Sum sales where Region = "North"'
      },
      'PIVOT': {
        description: 'Creates summary tables',
        steps: [
          '1. Click the column to group by (rows)',
          '2. Click the column to aggregate (values)',
          '3. Choose aggregation type'
        ],
        typicalParams: 2,
        maxParams: 5,
        example: 'Group sales by Region and Product'
      },
      'VLOOKUP': {
        description: 'Finds values in reference tables',
        steps: [
          '1. Click the column to search for',
          '2. Click the lookup table columns',
          '3. Set output column name'
        ],
        typicalParams: 3,
        maxParams: 10,
        example: 'Find product name using product ID'
      },
      'UPPER': {
        description: 'Converts text to uppercase',
        steps: [
          '1. Click the text column to convert',
          '2. Set output column name'
        ],
        typicalParams: 1,
        maxParams: 1,
        example: 'Convert "hello" to "HELLO"'
      },
      'LOWER': {
        description: 'Converts text to lowercase',
        steps: [
          '1. Click the text column to convert',
          '2. Set output column name'
        ],
        typicalParams: 1,
        maxParams: 1,
        example: 'Convert "HELLO" to "hello"'
      },
      'CONCATENATE': {
        description: 'Joins multiple text columns',
        steps: [
          '1. Click the text columns to join',
          '2. Choose separator',
          '3. Set output column name'
        ],
        typicalParams: 2,
        maxParams: 10,
        example: 'Join "First" + "Last" = "First Last"'
      }
    };
    
    return hints[functionName as keyof typeof hints];
  };

  const currentHint = getFunctionHints(step.source, selectedParams);

  // Parameter count warnings
  const getParameterWarning = (functionName: string, currentCount: number) => {
    if (!currentHint) return null;
    
    const { typicalParams, maxParams } = currentHint;
    
    if (currentCount > maxParams) {
      return {
        type: 'critical',
        message: `${currentCount} parameters exceeds maximum (${maxParams}). This may cause errors.`
      };
    }
    
    if (currentCount > typicalParams) {
      return {
        type: 'warning',
        message: `${currentCount} parameters (typically ${typicalParams}). This may be complex.`
      };
    }
    
    if (currentCount === 0) {
      return {
        type: 'info',
        message: `No parameters selected. Click columns in Data Preview to add parameters.`
      };
    }
    
    return null;
  };

  const parameterWarning = getParameterWarning(step.source, selectedParams.length);

  // Handle parameter changes
  const addParameter = (param: string) => {
    if (!selectedParams.includes(param)) {
      const newParams = [...selectedParams, param];
      setSelectedParams(newParams);
      onParametersChange(step.id, newParams);
    }
  };

  const removeParameter = (index: number) => {
    const newParams = selectedParams.filter((_, i) => i !== index);
    setSelectedParams(newParams);
    onParametersChange(step.id, newParams);
  };

  const clearParameters = () => {
    setSelectedParams([]);
    onParametersChange(step.id, []);
  };

  // Handle output column changes
  const handleOutputChange = (value: string) => {
    setOutputColumnName(value);
    onOutputChange(step.id, value);
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent) => {
    setIsDragging(true);
    e.dataTransfer.setData('text/plain', step.id);
    e.currentTarget.classList.add('opacity-50', 'scale-95');
  };

  const handleDragEnd = (e: React.DragEvent) => {
    setIsDragging(false);
    e.currentTarget.classList.remove('opacity-50', 'scale-95');
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('border-blue-400', 'bg-blue-50');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-400', 'bg-blue-50');
    const draggedStepId = e.dataTransfer.getData('text/plain');
    if (draggedStepId !== step.id) {
      onReorder(draggedStepId, step.id);
    }
  };

  // Get step status text
  const getStepStatusText = () => {
    if (step.type === 'function') {
      if (selectedParams.length === 0) return 'Ready to configure';
      if (!outputColumnName) return 'Set output column';
      if (parameterWarning?.type === 'critical') return 'Too many parameters';
      if (parameterWarning?.type === 'warning') return 'Complex configuration';
      return 'Ready to execute';
    }
    return step.status;
  };

  // Get step status color
  const getStepStatusColor = () => {
    if (step.type === 'function') {
      if (selectedParams.length === 0 || !outputColumnName) return 'text-gray-500';
      if (parameterWarning?.type === 'critical') return 'text-red-600';
      if (parameterWarning?.type === 'warning') return 'text-yellow-600';
      return 'text-green-600';
    }
    
    switch (step.status) {
      case 'completed': return 'text-green-600';
      case 'processing': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  return (
    <div 
      draggable={true}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-2 rounded-xl p-4 bg-gradient-to-r cursor-move transition-all duration-200 ${
        step.type === 'column' ? 'from-blue-50 to-blue-100 border-blue-200' :
        step.type === 'function' ? 'from-green-50 to-green-100 border-green-200' :
        step.type === 'break' ? 'from-red-50 to-red-100 border-red-200' :
        step.type === 'custom' ? 'from-purple-50 to-purple-100 border-purple-200' :
        step.type === 'sheet' ? 'from-orange-50 to-orange-100 border-orange-200' :
        'from-gray-50 to-gray-100 border-gray-200'
      } shadow-sm hover:shadow-md ${
        isDragging ? 'opacity-50 scale-95' : ''
      }`}
    >
      {/* Step Header */}
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
          
          {/* Step Number */}
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
          
          {/* Step Type Icon */}
          <div className={`p-2 rounded-lg ${
            step.type === 'column' ? 'bg-blue-100 text-blue-600' :
            step.type === 'function' ? 'bg-green-100 text-green-600' :
            step.type === 'break' ? 'bg-red-100 text-red-600' :
            step.type === 'custom' ? 'bg-purple-100 text-purple-600' :
            step.type === 'sheet' ? 'bg-orange-100 text-orange-600' :
            'bg-gray-100 text-gray-600'
          }`}>
            {step.type === 'function' ? (
              <span className="text-lg">🧮</span>
            ) : step.type === 'column' ? (
              <span className="text-lg">📁</span>
            ) : (
              <span className="text-lg">⚙️</span>
            )}
          </div>
          
          {/* Step Content */}
          <div className="min-w-0 flex-1 overflow-hidden">
            {step.type === 'function' ? (
              <div className="text-sm">
                <span className="font-semibold text-gray-800">{step.source}</span>
                <span className="text-green-600 font-medium"> ({selectedParams.join(' → ')})</span>
              </div>
            ) : step.type === 'column' ? (
              <div className="text-sm">
                <span className="font-semibold text-gray-800">
                  {step.columnReference?.displayName || step.source}
                </span>
                {step.sheet && <span className="text-gray-600 mx-2">→</span>}
                {step.sheet && <span className="text-blue-600 font-medium">{step.sheet}</span>}
                <span className="text-gray-600 mx-2">→</span>
                <span className="text-gray-700 font-medium">{step.target}</span>
              </div>
            ) : (
              <div className="text-sm text-gray-600">{step.source}</div>
            )}
          </div>
        </div>
        
        {/* Status and Actions */}
        <div className="flex items-center space-x-3">
          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              step.status === 'completed' ? 'bg-green-500 animate-pulse' :
              step.status === 'processing' ? 'bg-blue-500 animate-spin' :
              step.status === 'failed' ? 'bg-red-500' :
              'bg-gray-400'
            }`} />
            <span className={`text-xs font-medium ${getStepStatusColor()}`}>
              {getStepStatusText()}
            </span>
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center space-x-1">
            <button
              onClick={() => onEdit(step.id)}
              className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
              title="Edit this step"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            
            <button
              onClick={() => onDelete(step.id)}
              className="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
              title="Delete this step"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Enhanced Function Parameter Collection */}
      {step.type === 'function' && isActive && (
        <div className="mt-3 p-3 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200 max-w-full overflow-hidden">
          <div className="flex items-center space-x-2 mb-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-blue-700">
              Function Parameter Collection Active
            </span>
          </div>
          
          {/* Enhanced Tips Section */}
          <div className="tips-section mb-3">
            <div className="tip primary">
              <span className="icon">💡</span>
              <span className="text">
                <strong>Tip:</strong> Click columns in the Data Preview to add parameters
              </span>
            </div>
            
            {/* Function-Specific Hints */}
            {currentHint && (
              <div className="function-hints mt-2">
                <div className="hint-header">
                  <span className="icon">💡</span>
                  <span className="title">How to use {step.source}</span>
                </div>
                
                <div className="hint-content">
                  <p className="description">{currentHint.description}</p>
                  
                  <div className="steps">
                    {currentHint.steps.map((stepText, stepIndex) => (
                      <div key={stepIndex} className="step">
                        <span className="step-number">{stepIndex + 1}</span>
                        <span className="step-text">{stepText}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="example">
                    <span className="label">Example:</span>
                    <span className="text">{currentHint.example}</span>
                  </div>
                </div>
              </div>
            )}
            
            {/* Parameter Count Warning */}
            {parameterWarning && (
              <div className={`tip ${parameterWarning.type} mt-2`}>
                <span className="icon">
                  {parameterWarning.type === 'critical' ? '⚠️' : 
                   parameterWarning.type === 'warning' ? '💭' : 'ℹ️'}
                </span>
                <span className="text">
                  <strong>{parameterWarning.type === 'critical' ? 'Warning:' : 
                           parameterWarning.type === 'warning' ? 'Note:' : 'Info:'}</strong> {parameterWarning.message}
                </span>
              </div>
            )}
          </div>
          
          {/* Parameter Input Section */}
          <div className="parameter-input-section mb-3">
            <div className="input-container">
              <div className="parameter-display">
                {selectedParams.length > 0 ? (
                  <div className="parameters-list">
                    {selectedParams.map((param, paramIndex) => (
                      <div key={paramIndex} className="parameter-tag">
                        <span className="param-text">{param}</span>
                        <button 
                          className="remove-param"
                          onClick={() => removeParameter(paramIndex)}
                          title="Remove parameter"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <span className="icon">👆</span>
                    <span className="text">No parameters selected yet</span>
                  </div>
                )}
              </div>
              
              <div className="input-actions">
                <button 
                  className="clear-btn"
                  onClick={clearParameters}
                  disabled={selectedParams.length === 0}
                >
                  Clear All
                </button>
              </div>
            </div>
          </div>
          
          {/* Output Column Configuration */}
          <div className="output-configuration mb-3">
            <div className="config-header">
              <h4>Output Column</h4>
              <span className="config-status">
                {outputColumnName ? 'Configured ✓' : 'Not configured'}
              </span>
            </div>
            
            <div className="output-input-container">
              <input 
                type="text" 
                value={outputColumnName}
                onChange={(e) => handleOutputChange(e.target.value)}
                placeholder="Enter output column name..."
                className="output-input"
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
              />
              
              {/* Auto-Suggestions Dropdown */}
              {showSuggestions && (
                <div className="suggestions-dropdown">
                  {suggestions.map((suggestion, suggestionIndex) => (
                    <div 
                      key={suggestionIndex}
                      className="suggestion-item"
                      onClick={() => {
                        handleOutputChange(suggestion);
                        setShowSuggestions(false);
                      }}
                    >
                      <span className="suggestion-text">{suggestion}</span>
                      <span className="suggestion-hint">Click to use</span>
                    </div>
                  ))}
                </div>
              )}
              
              <button 
                className="suggest-btn"
                onClick={() => setShowSuggestions(!showSuggestions)}
                title="Show suggestions"
              >
                💡
              </button>
            </div>
          </div>
          
          {/* Function Info */}
          <div className="function-info">
            <div className="info-row">
              <span className="label">Current Function:</span>
              <span className="value">{step.source}</span>
            </div>
            <div className="info-row">
              <span className="label">Parameters:</span>
              <span className="value">[{selectedParams.length}]</span>
            </div>
            <div className="info-row">
              <span className="label">Output:</span>
              <span className="value">{outputColumnName || 'Not set'}</span>
            </div>
            <div className="info-row">
              <span className="label">Status:</span>
              <span className={`value status-${getStepStatusText().toLowerCase().replace(/\s+/g, '-')}`}>
                {getStepStatusText()}
              </span>
            </div>
          </div>
        </div>
      )}
      
      {/* Footer */}
      <div className="step-footer">
        <span className="step-type">{step.type === 'function' ? 'Function application step' : `${step.type} step`}</span>
        <div className="footer-actions">
          <span className="drag-hint">💡 Drag to reorder</span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedWorkflowStep;
