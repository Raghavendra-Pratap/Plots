import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { 
  Play, 
  X, 
  FileText, 
  FileSearch,
  Settings, 
  Info,
  AlertCircle,
  FolderPlus
} from 'lucide-react';
import { databaseManager, DatabaseProject, DatabaseWorkflow } from '../utils/database';

export interface ExecuteWorkflowTemplate {
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
  saveInputFiles: boolean; // Required for execute flow
}

export interface FilePattern {
  id: string;
  originalName: string;
  customName: string;
  isCommon: boolean;
  description: string;
  isActive: boolean;
  examples: string[];
}
    
interface ExecuteWorkflowDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onExecute: (template: ExecuteWorkflowTemplate) => void;
  workflowSteps: any[];
  importedFiles: any[];
  currentWorkflowName?: string;
}

const ExecuteWorkflowDialog: React.FC<ExecuteWorkflowDialogProps> = ({
  isOpen,
  onClose,
  onExecute,
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
  
  // Input file saving (key feature for execute flow)
  const [saveInputFiles, setSaveInputFiles] = useState(false);
  
  // Column settings (simplified for execute flow)
  const [trackAllColumns, setTrackAllColumns] = useState(false);
  const [fixedColumnSequence, setFixedColumnSequence] = useState(false);
  const [caseInsensitiveColumns, setCaseInsensitiveColumns] = useState(true);
  
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

  // Validate form
  const validateForm = () => {
    const newErrors: string[] = [];
    if (!workflowName.trim()) {
      newErrors.push('Workflow Name is required');
    }
    if (!project.trim()) {
      newErrors.push('Project is required');
    }
    
    setErrors(newErrors);
    return newErrors.length === 0;
  };

  // Handle execute workflow
  const handleExecute = async () => {
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
      
      const template: ExecuteWorkflowTemplate = {
        id: `template_${Date.now()}`,
        name: workflowName,
        description,
        project,
        version,
        compatibility: {
          minVersion: '1.0.0',
          maxVersion: '2.0.0'
        },
        filePatterns: [], // Simplified for execute flow
        workflowSteps,
        createdAt: new Date(),
        updatedAt: new Date(),
        isTemporary: false,
        columnSettings: {
          trackAllColumns,
          fixedSequence: fixedColumnSequence,
          caseInsensitive: caseInsensitiveColumns
        },
        saveInputFiles
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
        steps: template.workflowSteps,
        created: template.createdAt,
        lastModified: template.updatedAt
      };
      
      await databaseManager.createWorkflow(databaseWorkflow);
      
      // Call the execute callback
      await onExecute(template);
      onClose();
    } catch (error) {
      console.error('Error executing workflow:', error);
      setErrors(['Failed to execute workflow']);
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
          <div className="bg-green-600 text-white px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Play className="w-6 h-6" />
              <div>
                <h2 className="text-xl font-semibold">Execute Workflow</h2>
                <p className="text-green-100 text-sm">Save template and execute workflow with file processing</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-green-100 hover:text-white p-1"
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
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
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
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
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
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="Describe what this workflow does..."
                />
              </div>
            </div>

            {/* Input File Management - Key Feature for Execute Flow */}
            <div className="mb-6 border-t border-gray-200 pt-6">
              <div className="flex items-center space-x-2 text-gray-700 mb-4">
                <FileSearch className="w-5 h-5" />
                <span className="font-medium">Input File Management</span>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="saveInputFiles"
                    checked={saveInputFiles}
                    onChange={(e) => setSaveInputFiles(e.target.checked)}
                    className="w-4 h-4 text-green-600"
                  />
                  <label htmlFor="saveInputFiles" className="text-sm text-gray-700">
                    Save input files to project folder (with timestamped names)
                  </label>
                </div>
                
                {saveInputFiles && (
                  <div className="ml-6 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-700">
                      <strong>Note:</strong> Input files will be saved to the project's "Input Files" folder 
                      with timestamps to prevent conflicts. This helps maintain a complete record of 
                      all files used in workflow execution.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Column Settings */}
            <div className="mb-6">
              <div className="flex items-center space-x-2 text-gray-700 mb-4">
                <Settings className="w-5 h-5" />
                <span className="font-medium">Column Settings</span>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="trackAllColumns"
                    checked={trackAllColumns}
                    onChange={(e) => setTrackAllColumns(e.target.checked)}
                    className="w-4 h-4 text-green-600"
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
                    className="w-4 h-4 text-green-600"
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
                    className="w-4 h-4 text-green-600"
                  />
                  <label htmlFor="caseInsensitiveColumns" className="text-sm text-gray-700">
                    Column names should not be case sensitive in the workflow
                  </label>
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

            {/* Execution Summary */}
            <div className="mb-6 p-4 border rounded-lg bg-green-50 border-green-200">
              <div className="flex items-center space-x-2 mb-2">
                <Info className="w-5 h-5 text-green-600" />
                <h4 className="font-medium text-green-800">Execution Summary</h4>
              </div>
              <div className="text-sm space-y-1 text-green-700">
                <p>• <strong>Workflow Steps:</strong> {workflowSteps.length} steps</p>
                <p>• <strong>Files:</strong> {importedFiles.length} imported files</p>
                <p>• <strong>Column Tracking:</strong> {trackAllColumns ? 'All columns' : 'Workflow columns only'}</p>
                <p>• <strong>Sequence:</strong> {fixedColumnSequence ? 'Fixed order' : 'Flexible order'}</p>
                <p>• <strong>Case Sensitivity:</strong> {caseInsensitiveColumns ? 'Case insensitive' : 'Case sensitive'}</p>
                <p>• <strong>Input Files:</strong> {saveInputFiles ? 'Will be saved with timestamps' : 'Not saved'}</p>
              </div>
            </div>
            
            {/* Bottom padding for consistency */}
            <div className="h-4"></div>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Template will be saved and workflow will be executed with file processing
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleExecute}
                disabled={isSaving}
                className="px-4 py-2 text-white rounded-md transition-colors flex items-center space-x-2 disabled:opacity-50 bg-green-600 hover:bg-green-700"
              >
                {isSaving ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                <span>{isSaving ? 'Processing...' : 'Save and Execute'}</span>
              </button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ExecuteWorkflowDialog;
