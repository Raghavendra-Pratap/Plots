import React, { useState } from 'react';
import { 
  Plus, Folder, Edit3, Trash2, AlertCircle, ArrowLeft, 
  Upload, Download, Play, FileText, 
  Clock, Move, ExternalLink, FolderOpen
} from 'lucide-react';

interface ProjectFile {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: Date;
  status: 'pending' | 'processing' | 'completed' | 'error';
}

interface ProjectWorkflow {
  id: string;
  name: string;
  description: string;
  steps: any[];
  status: 'draft' | 'ready' | 'running' | 'completed' | 'error';
  lastExecuted?: Date;
}

interface Project {
  id: string;
  name: string;
  description: string;
  workflows: ProjectWorkflow[];
  inputFiles: ProjectFile[];
  outputFiles: ProjectFile[];
  created: Date;
  lastModified: Date;
  status: 'in_progress' | 'completed' | 'idle';
  storagePath: string;
}

interface ProjectItemProps {
  project: Project;
  onSelect: (project: Project) => void;
  onEdit: (project: Project) => void;
  onDelete: (project: Project) => void;
  onImportWorkflow: (projectId: string) => void;
  onImportFiles: (projectId: string) => void;
  onExecuteWorkflow: (workflowId: string) => void;
  onMoveWorkflow: (workflowId: string, targetProjectId: string) => void;
  onExportProject: (projectId: string) => void;
}

const ProjectItem: React.FC<ProjectItemProps> = ({ 
  project, 
  onSelect, 
  onEdit, 
  onDelete, 
  onImportWorkflow,
  onImportFiles,
  onExecuteWorkflow,
  onMoveWorkflow,
  onExportProject
}) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'workflow' | 'input' | 'output'>('workflow');

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'idle': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: Project['status']) => {
    switch (status) {
      case 'in_progress': return 'In Progress';
      case 'completed': return 'Completed';
      case 'idle': return 'Idle';
      default: return 'Unknown';
    }
  };

  const getFileCount = () => {
    return project.inputFiles.length + project.outputFiles.length;
  };

  const getRecentActivity = () => {
    const activities = [
      ...project.workflows.map(w => ({ date: w.lastExecuted, type: 'workflow' })),
      ...project.inputFiles.map(f => ({ date: f.uploadedAt, type: 'file' })),
      ...project.outputFiles.map(f => ({ date: f.uploadedAt, type: 'output' }))
    ].filter(a => a.date);
    
    if (activities.length === 0) return 'No recent activity';
    
    const latest = activities.sort((a, b) => new Date(b.date!).getTime() - new Date(a.date!).getTime())[0];
    const timeAgo = getTimeAgo(new Date(latest.date!));
    return `Last: ${timeAgo}`;
  };

  const getTimeAgo = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  };

  const tabs = [
    { id: 'workflow', label: 'Workflows', icon: FolderOpen, count: project.workflows.length },
    { id: 'input', label: 'Input Files', icon: Upload, count: project.inputFiles.length },
    { id: 'output', label: 'Output Files', icon: Download, count: project.outputFiles.length }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'workflow':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">Workflows</h4>
              <button
                onClick={(e) => { e.stopPropagation(); onImportWorkflow(project.id); }}
                className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <Plus className="w-3 h-3 mr-1 inline" />
                Import
              </button>
            </div>
            {project.workflows.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">No workflows imported yet</p>
            ) : (
              <div className="space-y-2">
                {project.workflows.slice(0, 3).map((workflow) => (
                  <div key={workflow.id} className="p-2 bg-gray-50 rounded text-sm">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{workflow.name}</div>
                        <div className="text-xs text-gray-500">{workflow.steps.length} steps</div>
                      </div>
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={(e) => { e.stopPropagation(); onExecuteWorkflow(workflow.id); }}
                          className="p-1 text-green-600 hover:bg-green-100 rounded"
                          title="Execute"
                        >
                          <Play className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); onMoveWorkflow(workflow.id, ''); }}
                          className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                          title="Move"
                        >
                          <Move className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                {project.workflows.length > 3 && (
                  <p className="text-xs text-gray-500 text-center">
                    +{project.workflows.length - 3} more workflows...
                  </p>
                )}
              </div>
            )}
          </div>
        );
      case 'input':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">Input Files</h4>
              <button
                onClick={(e) => { e.stopPropagation(); onImportFiles(project.id); }}
                className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <Upload className="w-3 h-3 mr-1 inline" />
                Import
              </button>
            </div>
            {project.inputFiles.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">No input files uploaded yet</p>
            ) : (
              <div className="space-y-2">
                {project.inputFiles.slice(0, 3).map((file) => (
                  <div key={file.id} className="p-2 bg-gray-50 rounded text-sm">
                    <div className="font-medium text-gray-900">{file.name}</div>
                    <div className="text-xs text-gray-500">
                      {file.type} • {Math.round(file.size / 1024)} KB
                    </div>
                  </div>
                ))}
                {project.inputFiles.length > 3 && (
                  <p className="text-xs text-gray-500 text-center">
                    +{project.inputFiles.length - 3} more files...
                  </p>
                )}
              </div>
            )}
          </div>
        );
      case 'output':
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">Output Files</h4>
              <button
                onClick={(e) => { e.stopPropagation(); onExportProject(project.id); }}
                className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
              >
                <Download className="w-3 h-3 mr-1 inline" />
                Export
              </button>
            </div>
            {project.outputFiles.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">No output files generated yet</p>
            ) : (
              <div className="space-y-2">
                {project.outputFiles.slice(0, 3).map((file) => (
                  <div key={file.id} className="p-2 bg-gray-50 rounded text-sm">
                    <div className="font-medium text-gray-900">{file.name}</div>
                    <div className="text-xs text-gray-500">
                      {file.type} • {Math.round(file.size / 1024)} KB
                    </div>
                  </div>
                ))}
                {project.outputFiles.length > 3 && (
                  <p className="text-xs text-gray-500 text-center">
                    +{project.outputFiles.length - 3} more files...
                  </p>
                )}
              </div>
            )}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="bg-white border rounded-lg hover:shadow-md transition-shadow relative">
      {/* Project Card Header */}
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div 
            className="flex-1 cursor-pointer" 
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <div className="flex items-center space-x-2">
              <Folder className="w-5 h-5 text-blue-500" />
              <h4 className="font-medium text-gray-900">{project.name}</h4>
              <div className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-1">{project.description}</p>
            
            {/* Project Stats */}
            <div className="flex items-center space-x-4 mt-3">
              <div className="flex items-center space-x-2 text-xs">
                <FileText className="w-3 h-3 text-gray-400" />
                <span className="text-gray-600">{getFileCount()} files</span>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <FolderOpen className="w-3 h-3 text-gray-400" />
                <span className="text-gray-600">{project.workflows.length} workflows</span>
              </div>
              <div className="flex items-center space-x-2 text-xs">
                <Clock className="w-3 h-3 text-gray-400" />
                <span className="text-gray-600">{getRecentActivity()}</span>
              </div>
            </div>
            
            {/* Status and Created Info */}
            <div className="flex items-center justify-between mt-3">
              <span className={`px-2 py-1 text-xs rounded-full font-medium ${getStatusColor(project.status)}`}>
                {getStatusText(project.status)}
              </span>
              <span className="text-xs text-gray-400">
                Created: {project.created.toLocaleDateString()}
              </span>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => { e.stopPropagation(); onEdit(project); }}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-md"
              title="Edit Project"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(true); }}
              className="p-2 text-red-600 hover:bg-red-50 rounded-md"
              title="Delete Project"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-100">
          {/* Tabs */}
          <div className="px-4 pt-3">
            <div className="flex space-x-4 border-b border-gray-200">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={(e) => { e.stopPropagation(); setActiveTab(tab.id as any); }}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                  <span className="bg-gray-100 text-gray-600 px-1 py-0.5 rounded text-xs">
                    {tab.count}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-4">
            {renderTabContent()}
          </div>
        </div>
      )}
      
      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div className="absolute right-0 top-0 mt-8 w-64 p-3 bg-white rounded-lg shadow-lg border z-10">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">Delete Project?</h4>
              <p className="text-xs text-gray-500 mt-1">
                Are you sure you want to delete "{project.name}"? This action cannot be undone.
              </p>
              <div className="flex justify-end space-x-2 mt-3">
                <button
                  onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(false); }}
                  className="px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 rounded"
                >
                  Cancel
                </button>
                <button
                  onClick={(e) => { 
                    e.stopPropagation(); 
                    onDelete(project);
                    setShowDeleteConfirm(false);
                  }}
                  className="px-2 py-1 text-xs text-white bg-red-500 hover:bg-red-600 rounded"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface ProjectDetailProps {
  project: Project;
  onBack: () => void;
  onEditProject: (project: Project) => void;
  onDeleteProject: (project: Project) => void;
  onImportWorkflow: (projectId: string) => void;
  onImportFiles: (projectId: string) => void;
  onExecuteWorkflow: (workflowId: string) => void;
  onMoveWorkflow: (workflowId: string, targetProjectId: string) => void;
  onExportProject: (projectId: string) => void;
}

const ProjectDetail: React.FC<ProjectDetailProps> = ({
  project,
  onBack,
  onEditProject,
  onDeleteProject,
  onImportWorkflow,
  onImportFiles,
  onExecuteWorkflow,
  onMoveWorkflow,
  onExportProject
}) => {
  const [activeTab, setActiveTab] = useState<'workflow' | 'input' | 'output'>('workflow');

  const tabs = [
    { id: 'workflow', label: 'Workflow', icon: Folder, count: project.workflows.length },
    { id: 'input', label: 'Input Files', icon: Upload, count: project.inputFiles.length },
    { id: 'output', label: 'Output Files', icon: Download, count: project.outputFiles.length }
  ];

  const renderWorkflowTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Workflows</h3>
        <button
          onClick={() => onImportWorkflow(project.id)}
          className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Import Workflow</span>
        </button>
      </div>
      
      {project.workflows.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Folder className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No workflows imported yet</p>
          <p className="text-sm">Import a workflow to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {project.workflows.map((workflow) => (
            <div key={workflow.id} className="p-4 bg-gray-50 rounded-lg border">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{workflow.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{workflow.description}</p>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>{workflow.steps.length} steps</span>
                    <span className={`px-2 py-1 rounded-full ${
                      workflow.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                      workflow.status === 'completed' ? 'bg-green-100 text-green-800' :
                      workflow.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {workflow.status}
                    </span>
                    {workflow.lastExecuted && (
                      <span>Last run: {workflow.lastExecuted.toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => onExecuteWorkflow(workflow.id)}
                    disabled={workflow.status === 'running'}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-md disabled:opacity-50"
                    title="Execute Workflow"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onMoveWorkflow(workflow.id, '')}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-md"
                    title="Move Workflow"
                  >
                    <Move className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderInputFilesTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Input Files</h3>
        <button
          onClick={() => onImportFiles(project.id)}
          className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <Upload className="w-4 h-4" />
          <span>Import Files</span>
        </button>
      </div>
      
      {project.inputFiles.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No input files uploaded yet</p>
          <p className="text-sm">Upload files to process with your workflows</p>
        </div>
      ) : (
        <div className="space-y-3">
          {project.inputFiles.map((file) => (
            <div key={file.id} className="p-4 bg-gray-50 rounded-lg border">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{file.name}</h4>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>{file.type}</span>
                    <span>{Math.round(file.size / 1024)} KB</span>
                    <span>Uploaded: {file.uploadedAt.toLocaleDateString()}</span>
                    <span className={`px-2 py-1 rounded-full ${
                      file.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                      file.status === 'completed' ? 'bg-green-100 text-green-800' :
                      file.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {file.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderOutputFilesTab = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Output Files</h3>
        <button
          onClick={() => onExportProject(project.id)}
          className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-2"
        >
          <Download className="w-4 h-4" />
          <span>Export Project</span>
        </button>
      </div>
      
      {project.outputFiles.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Download className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>No output files generated yet</p>
          <p className="text-sm">Execute workflows to generate output files</p>
        </div>
      ) : (
        <div className="space-y-3">
          {project.outputFiles.map((file) => (
            <div key={file.id} className="p-4 bg-gray-50 rounded-lg border">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{file.name}</h4>
                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <span>{file.type}</span>
                    <span>{Math.round(file.size / 1024)} KB</span>
                    <span>Generated: {file.uploadedAt.toLocaleDateString()}</span>
                    <span className={`px-2 py-1 rounded-full ${
                      file.status === 'completed' ? 'bg-green-100 text-green-800' :
                      file.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {file.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'workflow':
        return renderWorkflowTab();
      case 'input':
        return renderInputFilesTab();
      case 'output':
        return renderOutputFilesTab();
      default:
        return renderWorkflowTab();
    }
  };

  return (
    <div className="flex-1 p-6 overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold">{project.name}</h2>
            <p className="text-gray-600">{project.description}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => onEditProject(project)}
            className="px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-md flex items-center space-x-2"
          >
            <Edit3 className="w-4 h-4" />
            <span>Edit Project</span>
          </button>
          <button
            onClick={() => onExportProject(project.id)}
            className="px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-2"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Project Info */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="p-4 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{project.workflows.length}</div>
          <div className="text-sm text-blue-600">Workflows</div>
        </div>
        <div className="p-4 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{project.inputFiles.length}</div>
          <div className="text-sm text-green-600">Input Files</div>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{project.outputFiles.length}</div>
          <div className="text-sm text-purple-600">Output Files</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600">Storage Path</div>
          <div className="text-xs text-gray-500 mt-1 truncate">{project.storagePath}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
              <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}
    </div>
  );
};

interface ProjectsProps {
  projects: Project[];
  selectedProject: Project | null;
  onSelectProject: (project: Project) => void;
  onEditProject: (project: Project) => void;
  onDeleteProject: (project: Project) => void;
  onImportWorkflow: (projectId: string) => void;
  onImportFiles: (projectId: string) => void;
  onExecuteWorkflow: (workflowId: string) => void;
  onMoveWorkflow: (workflowId: string, targetProjectId: string) => void;
  onExportProject: (projectId: string) => void;
  onCreateProject: () => void;
}

const Projects: React.FC<ProjectsProps> = ({ 
  projects, 
  selectedProject,
  onSelectProject, 
  onEditProject, 
  onDeleteProject,
  onImportWorkflow,
  onImportFiles,
  onExecuteWorkflow,
  onMoveWorkflow,
  onExportProject,
  onCreateProject
}) => {
  if (selectedProject) {
    return (
      <ProjectDetail
        project={selectedProject}
        onBack={() => onSelectProject(null as any)}
        onEditProject={onEditProject}
        onDeleteProject={onDeleteProject}
        onImportWorkflow={onImportWorkflow}
        onImportFiles={onImportFiles}
        onExecuteWorkflow={onExecuteWorkflow}
        onMoveWorkflow={onMoveWorkflow}
        onExportProject={onExportProject}
      />
    );
  }

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Projects</h2>
        <button 
          onClick={() => window.location.href = '/playground'}
          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <Play className="w-4 h-4 mr-2" />
          Open Playground
        </button>
      </div>
      
      {projects.length === 0 ? (
        <div className="text-center py-12">
          <Folder className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-500 mb-4">Use the "+ New Project" button in the header to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectItem
              key={project.id}
              project={project}
              onSelect={onSelectProject}
              onEdit={onEditProject}
              onDelete={onDeleteProject}
              onImportWorkflow={onImportWorkflow}
              onImportFiles={onImportFiles}
              onExecuteWorkflow={onExecuteWorkflow}
              onMoveWorkflow={onMoveWorkflow}
              onExportProject={onExportProject}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Projects;
