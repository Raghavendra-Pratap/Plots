import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent } from './ui/card';
import { 
  Save, 
  X, 
  FileText, 
  FileSearch,
  Settings, 
  Info,
  AlertCircle,
  FolderPlus
} from 'lucide-react';
import { databaseManager, DatabaseProject, DatabaseWorkflow } from '../utils/database';

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  project: string;
  version: string;
  compatibility: {
    minVersion: string;
    maxVersion: string;
  };
  filePatterns: FilePattern[];
  workflowSteps: any[];
  createdAt: Date;
  updatedAt: Date;
  isTemporary: boolean;
  columnSettings: {
    trackAllColumns: boolean;
    fixedSequence: boolean;
    caseInsensitive: boolean;
  };

}

export interface FilePattern {
  id: string;
  originalName: string;
  customName: string;
  isCommon: boolean; // true = *--name--*, false = --name--
  description: string;
  isActive: boolean;
  examples: string[];
}

interface SaveWorkflowDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (template: WorkflowTemplate) => void;
  workflowSteps: any[];
  importedFiles: any[];
  currentWorkflowName?: string;
}

const SaveWorkflowDialog: React.FC<SaveWorkflowDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  workflowSteps,
  importedFiles,
  currentWorkflowName
}) => {
  // Basic workflow info
  const [workflowName, setWorkflowName] = useState(currentWorkflowName || 'Untitled Workflow');
  const [description, setDescription] = useState('');
  const [project, setProject] = useState('');
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [version, setVersion] = useState('1.0.0');
  
  // Project management
  const [existingProjects, setExistingProjects] = useState<string[]>([]);
  const [showNewProjectInput, setShowNewProjectInput] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  

  const [useCustomFileNames, setUseCustomFileNames] = useState(false);
  const [trackAllColumns, setTrackAllColumns] = useState(false);
  const [fixedColumnSequence, setFixedColumnSequence] = useState(false);
  const [caseInsensitiveColumns, setCaseInsensitiveColumns] = useState(true);

  
  // File patterns
  const [filePatterns, setFilePatterns] = useState<FilePattern[]>([]);
  
  // Form state
  const [errors, setErrors] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  // Load existing projects from database
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const projects = await databaseManager.getProjects();
        const projectNames = projects.map(p => p.name);
        setExistingProjects(projectNames);
      } catch (error) {
        console.error('Error loading projects:', error);
        setExistingProjects([]);
      }
    };
    
    if (isOpen) {
      loadProjects();
    }
  }, [isOpen]);

  // Auto-detect file patterns for each imported file
  const initializeFilePatterns = useCallback(() => {
    const patterns = importedFiles.map(file => {
      const fileName = file.name;
      const baseName = fileName.split('.')[0];
      
      // Detect common patterns
      let pattern = '';
      let description = '';
      
      if (baseName.match(/^audit_\d{4}$/)) {
        pattern = 'audit_*';
        description = 'Monthly audit files (e.g., audit_2025, audit_2026)';
      } else if (baseName.match(/^report_Q\d$/)) {
        pattern = 'report_Q*';
        description = 'Quarterly report files (e.g., report_Q1, report_Q2)';
      } else if (baseName.match(/^data_\w+$/)) {
        pattern = 'data_*';
        description = 'Data files with category suffix';
      } else {
        pattern = baseName;
        description = `Exact file name: ${baseName}`;
      }
      
      return {
        id: `pattern_${Date.now()}_${Math.random()}`,
        originalName: fileName,
        customName: pattern,
        isCommon: pattern.includes('*'),
        description,
        isActive: true,
        examples: generatePatternExamples(pattern)
      };
    });
    
    setFilePatterns(patterns);
  }, [importedFiles]);

  // Initialize patterns when dialog opens
  useEffect(() => {
    if (isOpen && importedFiles.length > 0) {
      initializeFilePatterns();
    }
  }, [isOpen, importedFiles, initializeFilePatterns]);

  // Generate examples for file patterns
  const generatePatternExamples = (pattern: string): string[] => {
    if (pattern.includes('*')) {
      if (pattern.startsWith('audit_')) {
        return ['audit_2025', 'audit_2026', 'audit_2027'];
      } else if (pattern.startsWith('report_Q')) {
        return ['report_Q1', 'report_Q2', 'report_Q3', 'report_Q4'];
      } else if (pattern.startsWith('data_')) {
        return ['data_sales', 'data_marketing', 'data_finance'];
      }
    }
    return [pattern];
  };

  // Handle project selection/creation
  const handleProjectChange = (value: string) => {
    if (value === 'create_new') {
      setShowNewProjectInput(true);
      setProject('');
    } else {
      setProject(value);
      setShowNewProjectInput(false);
      setNewProjectName('');
    }
  };

  // Create new project in database
  const createNewProject = async () => {
    if (newProjectName.trim()) {
      try {
        const newProject: DatabaseProject = {
          id: `project_${Date.now()}`,
          name: newProjectName.trim(),
          description: `Project for ${newProjectName.trim()} workflows`,
          created: new Date(),
          lastModified: new Date(),
          status: 'idle',
          storagePath: `/projects/${newProjectName.trim().toLowerCase().replace(/\s+/g, '_')}`,
          workflows: [],
          inputFiles: [],
          outputFiles: []
        };
        
        await databaseManager.createProject(newProject);
        
        // Update local state
        setExistingProjects(prev => [...prev, newProjectName.trim()]);
        setProject(newProjectName.trim());
        setShowNewProjectInput(false);
        setNewProjectName('');
        
        console.log('New project created in database:', newProject);
      } catch (error) {
        console.error('Error creating project:', error);
        setErrors(['Failed to create project. Please try again.']);
      }
    }
  };

  // Update file pattern
  const updateFilePattern = (id: string, field: keyof FilePattern, value: any) => {
    setFilePatterns(prev => prev.map(pattern => 
      pattern.id === id ? { ...pattern, [field]: value } : pattern
    ));
  };

  // Toggle file pattern common/exact
  const toggleFilePatternType = (id: string) => {
    setFilePatterns(prev => prev.map(pattern => {
      if (pattern.id === id) {
        const isCommon = !pattern.isCommon;
        let customName = pattern.customName;
        
        if (isCommon && !customName.includes('*')) {
          // Convert to common pattern
          const baseName = customName.split('_')[0];
          customName = `${baseName}_*`;
        } else if (!isCommon && customName.includes('*')) {
          // Convert to exact pattern
          customName = customName.replace('*', '2025'); // Use current year as example
        }
        
        return { ...pattern, isCommon, customName };
      }
      return pattern;
    }));
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: string[] = [];
    
    if (!workflowName.trim()) {
      newErrors.push('Workflow name is required');
    }
    
    if (!project.trim()) {
      newErrors.push('Project is required');
    }
    
    if (useCustomFileNames && filePatterns.some(p => !p.customName.trim())) {
      newErrors.push('All file patterns must have custom names');
    }
    
    setErrors(newErrors);
    return newErrors.length === 0;
  };

  // Save workflow template to database
  const handleSave = async () => {
    if (!validateForm()) return;
    
    setIsSaving(true);
    
    try {
      // Ensure project exists in database
      if (!existingProjects.includes(project)) {
        // Create the project if it doesn't exist
        const newProject: DatabaseProject = {
          id: `project_${Date.now()}`,
          name: project,
          description: `Project for ${project} workflows`,
          created: new Date(),
          lastModified: new Date(),
          status: 'idle',
          storagePath: `/projects/${project.toLowerCase().replace(/\s+/g, '_')}`,
          workflows: [],
          inputFiles: [],
          outputFiles: []
        };
        
        await databaseManager.createProject(newProject);
        setExistingProjects(prev => [...prev, project]);
        
        console.log('Project created automatically in database:', newProject);
      }
      
      const template: WorkflowTemplate = {
        id: `template_${Date.now()}`,
        name: workflowName,
        description,
        project,
        version,
        compatibility: {
          minVersion: '1.0.0',
          maxVersion: '2.0.0'
        },
        filePatterns: useCustomFileNames ? filePatterns.filter(p => p.isActive) : [],
        workflowSteps,
        createdAt: new Date(),
        updatedAt: new Date(),
        isTemporary: false,
        columnSettings: {
          trackAllColumns,
          fixedSequence: fixedColumnSequence,
          caseInsensitive: caseInsensitiveColumns
        },

      };
      
      // Save to database
      const databaseWorkflow: DatabaseWorkflow = {
        id: template.id,
        name: template.name,
        description: template.description,
        project: template.project,
        version: template.version,
        workflowSteps: template.workflowSteps,
        filePatterns: template.filePatterns,
        columnSettings: template.columnSettings,
        createdAt: template.createdAt,
        updatedAt: template.updatedAt,
        isTemporary: template.isTemporary,
        // Additional properties for compatibility
        steps: template.workflowSteps,
        created: template.createdAt,
        lastModified: template.updatedAt
      };
      
      await databaseManager.createWorkflow(databaseWorkflow);
      
      // Call the onSave callback
      await onSave(template);
      onClose();
    } catch (error) {
      console.error('Error saving workflow template:', error);
      setErrors(['Failed to save workflow template']);
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[85vh] overflow-hidden">
        <CardContent className="p-0">
          {/* Header */}
          <div className="bg-blue-600 text-white px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Save className="w-6 h-6" />
              <div>
                <h2 className="text-xl font-semibold">Save Workflow Template</h2>
                <p className="text-blue-100 text-sm">Create a reusable workflow template with smart file mapping</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-blue-100 hover:text-white p-1"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(85vh-140px)]">
            {/* Basic Information */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Basic Information
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Workflow Name *
                  </label>
                  <input
                    type="text"
                    value={workflowName}
                    onChange={(e) => setWorkflowName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter workflow name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project *
                  </label>
                  <div className="flex space-x-2">
                    <select
                      value={project}
                      onChange={(e) => handleProjectChange(e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select a project</option>
                      {existingProjects.map(proj => (
                        <option key={proj} value={proj}>{proj}</option>
                      ))}
                      <option value="create_new">+ Create New Project</option>
                    </select>
                  </div>
                  
                  {showNewProjectInput && (
                    <div className="mt-2 flex space-x-2">
                      <input
                        type="text"
                        value={newProjectName}
                        onChange={(e) => setNewProjectName(e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter new project name"
                      />
                      <button
                        onClick={createNewProject}
                        className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-1"
                      >
                        <FolderPlus className="w-4 h-4" />
                        <span>Create</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe what this workflow does..."
                />
              </div>
            </div>

            {/* Advanced Settings Section - Always Visible */}
            <div className="mb-6 border-t border-gray-200 pt-6">
              <div className="flex items-center space-x-2 text-gray-700 mb-4">
                <Settings className="w-5 h-5" />
                <span className="font-medium">Advanced Settings</span>
              </div>
              
              {/* File Naming Settings */}
                <div className="mb-6">
                  <div className="flex items-center space-x-2 mb-4">
                    <input
                      type="checkbox"
                      id="useCustomFileNames"
                      checked={useCustomFileNames}
                      onChange={(e) => setUseCustomFileNames(e.target.checked)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <label htmlFor="useCustomFileNames" className="text-sm font-medium text-gray-700">
                      Use custom file names for the workflow
                    </label>
                  </div>
                  
                  {useCustomFileNames && (
                    <div className="ml-6 border-l-2 border-gray-200 pl-4">
                      <h4 className="text-md font-medium mb-3 flex items-center">
                        <FileSearch className="w-4 h-4 mr-2" />
                        File Name Patterns
                      </h4>
                      
                      {filePatterns.map((pattern) => (
                        <div key={pattern.id} className="mb-4 p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-sm font-medium text-gray-600">
                              Current File Name: {pattern.originalName}
                            </span>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="block text-xs text-gray-600 mb-1">Custom Name</label>
                              <input
                                type="text"
                                value={pattern.customName}
                                onChange={(e) => updateFilePattern(pattern.id, 'customName', e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                                placeholder="e.g., audit_* or audit_2025"
                              />
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => toggleFilePatternType(pattern.id)}
                                className={`px-4 py-2 text-sm rounded-md transition-colors ${
                                  pattern.isCommon
                                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                                    : 'bg-gray-100 text-gray-700 border border-gray-300'
                                }`}
                              >
                                {pattern.isCommon ? 'is common' : 'is exact'}
                              </button>
                            </div>
                          </div>
                          
                          <div className="mt-2 text-xs text-gray-500">
                            <strong>Examples:</strong> {pattern.examples.join(', ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Column Settings */}
                <div className="mb-6">
                  <h4 className="text-md font-medium mb-3 flex items-center">
                    <FileText className="w-4 h-4 mr-2" />
                    Column Settings
                  </h4>
                  
                  <div className="ml-6 space-y-3">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="trackAllColumns"
                        checked={trackAllColumns}
                        onChange={(e) => setTrackAllColumns(e.target.checked)}
                        className="w-4 h-4 text-blue-600"
                      />
                      <label htmlFor="trackAllColumns" className="text-sm text-gray-700">
                        Track entire structure (all columns) vs. just workflow columns
                      </label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="fixedColumnSequence"
                        checked={fixedColumnSequence}
                        onChange={(e) => setFixedColumnSequence(e.target.checked)}
                        className="w-4 h-4 text-blue-600"
                      />
                      <label htmlFor="fixedColumnSequence" className="text-sm text-gray-700">
                        Fixed column sequence / Look for column names irrespective of sequence
                      </label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="caseInsensitiveColumns"
                        checked={caseInsensitiveColumns}
                        onChange={(e) => setCaseInsensitiveColumns(e.target.checked)}
                        className="w-4 h-4 text-blue-600"
                      />
                      <label htmlFor="caseInsensitiveColumns" className="text-sm text-gray-700">
                        Column names should not be case sensitive in the workflow
                      </label>
                    </div>
                  </div>
                </div>
            </div>

            {/* Errors */}
            {errors.length > 0 && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  <h4 className="text-red-800 font-medium">Please fix the following errors:</h4>
                </div>
                <ul className="list-disc list-inside text-red-700 text-sm space-y-1">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Summary */}
            <div className="mb-6 p-4 border rounded-lg bg-blue-50 border-blue-200">
              <div className="flex items-center space-x-2 mb-2">
                <Info className="w-5 h-5 text-blue-600" />
                <h4 className="font-medium text-blue-800">Template Summary</h4>
              </div>
              <div className="text-sm space-y-1 text-blue-700">
                <p>• <strong>Workflow Steps:</strong> {workflowSteps.length} steps</p>
                <p>• <strong>Files:</strong> {importedFiles.length} imported files</p>
                {useCustomFileNames && (
                  <p>• <strong>File Patterns:</strong> {filePatterns.filter(p => p.isActive).length} patterns</p>
                )}
                <p>• <strong>Column Tracking:</strong> {trackAllColumns ? 'All columns' : 'Workflow columns only'}</p>
                <p>• <strong>Sequence:</strong> {fixedColumnSequence ? 'Fixed order' : 'Flexible order'}</p>
                <p>• <strong>Case Sensitivity:</strong> {caseInsensitiveColumns ? 'Case insensitive' : 'Case sensitive'}</p>
              </div>
            </div>
            
            {/* Bottom padding for consistency */}
            <div className="h-4"></div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              This template will be saved locally and can be exported as JSON
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="px-4 py-2 text-white rounded-md transition-colors flex items-center space-x-2 disabled:opacity-50 bg-blue-600 hover:bg-blue-700"
              >
                {isSaving ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span>{isSaving ? 'Processing...' : 'Save Template'}</span>
              </button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SaveWorkflowDialog;
