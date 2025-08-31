import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Layout, Home, Play, GitBranch,
  Plus, ChevronRight, Folder, Bell, ArrowLeft, Settings as SettingsIcon
} from 'lucide-react';

import Projects from './Projects';
import Dashboard from './Dashboard';
import Workflows from './Workflows';
import Workspace from './Workspace';
import Settings from './Settings';
import Notifications from './Notifications';
import CreateProjectDialog from './CreateProjectDialog';
import { databaseManager, DatabaseProject } from '../utils/database';
// import { useBackend } from '../contexts/BackendContext'; // Not used, removed to prevent blocking
import BackendStatusIndicator from './BackendStatusIndicator';
import ErrorBoundary from './ErrorBoundary';


// Types
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

interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  created: Date;
  lastModified: Date;
  project: string;
  // Additional fields from WorkflowTemplate
  version?: string;
  filePatterns?: any[];
  columnSettings?: any;
}

interface WorkflowStep {
  id: string;
  operation: string;
  parameters: Record<string, any>;
  order: number;
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

interface IconWithTooltipProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  active: boolean;
  onClick: () => void;
}

// Custom Tooltip Component
const IconWithTooltip: React.FC<IconWithTooltipProps> = ({ icon: Icon, label, active, onClick }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const handleClick = () => {
    console.log('IconWithTooltip clicked:', label);
    onClick();
  };

  return (
    <div className="relative" onMouseEnter={() => setShowTooltip(true)} onMouseLeave={() => setShowTooltip(false)}>
      <div
        onClick={handleClick}
        className={`w-10 h-10 rounded-lg flex items-center justify-center cursor-pointer transition-all duration-200 ${
          active 
            ? 'bg-blue-600 text-white shadow-lg' 
            : 'text-gray-400 hover:bg-gray-800 hover:text-white'
        }`}
      >
        <Icon className="w-5 h-5" />
      </div>
      
      {showTooltip && (
        <div className="absolute left-16 top-1/2 transform -translate-y-1/2 bg-gray-900 text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap z-30">
          {label}
          <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-0 h-0 border-l-0 border-r-8 border-t-4 border-b-4 border-transparent border-r-gray-900"></div>
        </div>
      )}
    </div>
  );
};

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [workspaceActiveStep, setWorkspaceActiveStep] = useState('import');
  const [workspaceSelectedOperation, setWorkspaceSelectedOperation] = useState(null);
  const [importedFiles, setImportedFiles] = useState<FileData[]>([]);
  const [lastSaved, setLastSaved] = useState<Date>(new Date());

  // State for projects and workflows
  const [projects, setProjects] = useState<Project[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [showCreateProjectDialog, setShowCreateProjectDialog] = useState(false);

  // Load data from database on component mount
  useEffect(() => {
    loadDataFromDatabase();
    
    // Listen for workflow template save events
    const handleWorkflowTemplateSaved = () => {
      console.log('Workflow template saved, refreshing data...');
      loadDataFromDatabase();
    };
    
    window.addEventListener('workflowTemplateSaved', handleWorkflowTemplateSaved);
    
    // Cleanup event listener
    return () => {
      window.removeEventListener('workflowTemplateSaved', handleWorkflowTemplateSaved);
    };
  }, []);

  // Load projects and workflows from database
  const loadDataFromDatabase = async () => {
    try {
      // Load projects
      const databaseProjects = await databaseManager.getProjects();
      console.log('Raw projects from database:', databaseProjects);
      
      const projectList: Project[] = databaseProjects.map((dbProject) => ({
        id: dbProject.id,
        name: dbProject.name,
        description: dbProject.description,
        workflows: dbProject.workflows?.map(w => ({
          id: w.id,
          name: w.name,
          description: w.description,
          steps: w.steps || [],
          status: 'ready' as const,
          lastExecuted: w.lastExecuted
        })) || [],
        inputFiles: dbProject.inputFiles || [],
        outputFiles: dbProject.outputFiles || [],
        created: dbProject.created,
        lastModified: dbProject.lastModified,
        status: dbProject.status,
        storagePath: dbProject.storagePath
      }));
      
      // Sort projects by last modified date (most recent first)
      const sortedProjects = projectList.sort((a, b) => {
        const dateA = new Date(a.lastModified || a.created);
        const dateB = new Date(b.lastModified || b.created);
        return dateB.getTime() - dateA.getTime();
      });
      
      console.log('Processed and sorted projects:', sortedProjects);
      setProjects(sortedProjects);

      // Load workflows
      const databaseWorkflows = await databaseManager.getWorkflows();
      const workflowList: Workflow[] = databaseWorkflows.map((dbWorkflow) => ({
        id: dbWorkflow.id,
        name: dbWorkflow.name,
        description: dbWorkflow.description,
        steps: dbWorkflow.steps || dbWorkflow.workflowSteps || [],
        created: dbWorkflow.created || dbWorkflow.createdAt,
        lastModified: dbWorkflow.lastModified || dbWorkflow.updatedAt,
        project: dbWorkflow.project,
        version: dbWorkflow.version,
        filePatterns: dbWorkflow.filePatterns,
        columnSettings: dbWorkflow.columnSettings
      }));
      
      // Sort workflows by last modified date (most recent first)
      const sortedWorkflows = workflowList.sort((a, b) => {
        const dateA = new Date(a.lastModified || a.created);
        const dateB = new Date(b.lastModified || b.created);
        return dateB.getTime() - dateA.getTime();
      });
      
      setWorkflows(sortedWorkflows);

      console.log('Data loaded from database:', { projects: projectList, workflows: workflowList });
    } catch (error) {
      console.error('Error loading data from database:', error);
    }
  };

  const sidebarItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, active: activeTab === 'dashboard' },
    { id: 'workspace', label: 'Workspace', icon: Layout, active: activeTab === 'workspace' },
    { id: 'workflows', label: 'Workflows', icon: GitBranch, active: activeTab === 'workflows' },
    { id: 'projects', label: 'Projects', icon: Folder, active: activeTab === 'projects' },
    { id: 'notifications', label: 'Notifications', icon: Bell, active: activeTab === 'notifications' },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, active: activeTab === 'settings' },
  ];

  const getTotalDataVolume = () => {
    return importedFiles.reduce((total, file) => total + file.size, 0);
  };

  const formatDataVolume = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Project handlers
  const handleEditProject = (project: Project) => {
    console.log('Editing project:', project.name);
    // TODO: Open project editor
  };

  const handleDeleteProject = async (project: Project) => {
    try {
      await databaseManager.deleteProject(project.name);
      
      // Refresh data from database
      await loadDataFromDatabase();
      
      console.log('Project deleted from database:', project.name);
    } catch (error) {
      console.error('Error deleting project:', error);
    }
  };

  const handleImportWorkflow = (projectId: string) => {
    console.log('Importing workflow to project:', projectId);
    // TODO: Implement workflow import logic
  };

  const handleImportFiles = (projectId: string) => {
    console.log('Importing files to project:', projectId);
    // TODO: Implement file import logic
  };

  const handleExecuteWorkflow = (workflowId: string) => {
    console.log('Executing workflow:', workflowId);
    // TODO: Implement workflow execution logic
  };

  const handleMoveWorkflow = (workflowId: string, targetProjectId: string) => {
    console.log('Moving workflow:', workflowId, 'to project:', targetProjectId);
    // TODO: Implement workflow move logic
  };

  const handleExportProject = (projectId: string) => {
    console.log('Exporting project:', projectId);
    // TODO: Implement project export logic
  };

  const handleCreateProject = () => {
    setShowCreateProjectDialog(true);
  };

  const handleCreateProjectSubmit = async (projectName: string, description: string) => {
    try {
      const newProject: DatabaseProject = {
        id: `project_${Date.now()}`,
        name: projectName,
        description: description || 'Project description',
        created: new Date(),
        lastModified: new Date(),
        status: 'idle',
        storagePath: `/projects/${projectName.toLowerCase().replace(/\s+/g, '_')}`,
        workflows: [],
        inputFiles: [],
        outputFiles: []
      };
      
      console.log('Creating new project:', newProject);
      await databaseManager.createProject(newProject);
      console.log('Project created successfully in database');
      
      // Refresh data from database
      console.log('Refreshing data from database...');
      await loadDataFromDatabase();
      console.log('Data refresh completed');
      
      console.log('New project created in database:', newProject);
    } catch (error) {
      console.error('Error creating project:', error);
      throw error; // Re-throw to let dialog handle the error
    }
  };

  // Workflow handlers
  const handleRunWorkflow = (workflow: Workflow) => {
    console.log('Running workflow:', workflow.name);
    // TODO: Implement workflow execution
  };

  const handleEditWorkflow = (workflow: Workflow) => {
    console.log('Editing workflow:', workflow.name);
    // TODO: Open workflow editor
  };

  const handleDeleteWorkflow = async (workflow: Workflow) => {
    try {
      await databaseManager.deleteWorkflow(workflow.id);
      
      // Refresh data from database
      await loadDataFromDatabase();
      
      console.log('Workflow deleted from database:', workflow.id);
    } catch (error) {
      console.error('Error deleting workflow:', error);
    }
  };

  const handleWorkspaceDataOperation = (operation: any) => {
    setWorkspaceSelectedOperation(operation);
    console.log('Workspace operation selected:', operation);
  };

  const handleWorkspaceBrowseFiles = () => {
    console.log('Browse files clicked');
  };

  const handleWorkspaceDragDropImport = (files: FileList) => {
    const filesArray = Array.from(files);
    const newFiles: FileData[] = filesArray.map((file) => {
      const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
      return {
        name: file.name,
        type: isExcel ? 'excel' : (file.type || 'csv'),
        size: file.size,
        columns: [],
        path: '',
        lastModified: new Date(file.lastModified),
        headerConfig: { row: 1, merged: false, autoDetected: true }
      } as FileData;
    });
    setImportedFiles((prev) => [...prev, ...newFiles]);
  };

  const handleWorkspaceDeleteFile = (fileName: string) => {
    setImportedFiles((prev) => prev.filter((f) => f.name !== fileName));
  };

  const handleSidebarClick = (tabId: string) => {
    console.log('Sidebar clicked:', tabId);
    setActiveTab(tabId);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar Navigation with Tooltips */}
      <div className="w-16 bg-gray-900 flex flex-col items-center py-6 space-y-8 relative z-20" style={{ pointerEvents: 'auto' }}>
        <div className="text-white relative group">
          <Layout className="w-6 h-6" />
        </div>
        
        {sidebarItems.map((item) => {
          console.log('Rendering sidebar item:', item.id, item.label);
          return (
            <IconWithTooltip
              key={item.id}
              icon={item.icon}
              label={item.label}
              active={activeTab === item.id}
              onClick={() => handleSidebarClick(item.id)}
            />
          );
        })}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white h-16 px-6 flex items-center justify-between border-b">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold">Data Studio</h1>
            {/* Backend Status Indicator */}
            <BackendStatusIndicator />
            {/* Dynamic breadcrumb navigation */}
            {selectedProject && (
              <div className="flex items-center text-sm text-gray-500">
                <span 
                  className="cursor-pointer hover:text-gray-700"
                  onClick={() => setSelectedProject(null)}
                >
                  Projects
                </span>
                <ChevronRight className="w-4 h-4 mx-1" />
                <span>{selectedProject.name}</span>
              </div>
            )}
          </div>
          <div className="flex items-center space-x-3">
            <button 
              onClick={() => navigate('/playground')}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Play className="w-4 h-4 mr-2" />
              Playground
            </button>
            <button 
              onClick={() => navigate('/playground')}
              className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Workflow
            </button>
            <button 
              onClick={() => setShowCreateProjectDialog(true)}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </button>
          </div>
        </div>

        <div className="flex h-[calc(100vh-64px)]">
          <ErrorBoundary>
            {activeTab === 'dashboard' && (
              <Dashboard
                projects={projects}
                workflows={workflows}
                importedFiles={importedFiles}
                getTotalDataVolume={getTotalDataVolume}
                formatDataVolume={formatDataVolume}
              />
            )}

          {activeTab === 'projects' && (
            <Projects
              projects={projects}
              selectedProject={selectedProject}
              onSelectProject={setSelectedProject}
              onEditProject={handleEditProject}
              onDeleteProject={handleDeleteProject}
              onImportWorkflow={handleImportWorkflow}
              onImportFiles={handleImportFiles}
              onExecuteWorkflow={handleExecuteWorkflow}
              onMoveWorkflow={handleMoveWorkflow}
              onExportProject={handleExportProject}
              onCreateProject={handleCreateProject}
            />
          )}

          {activeTab === 'workflows' && (
            <Workflows
              workflows={workflows}
              selectedProject={selectedProject}
              onRunWorkflow={handleRunWorkflow}
              onEditWorkflow={handleEditWorkflow}
              onDeleteWorkflow={handleDeleteWorkflow}
            />
          )}

          {activeTab === 'workspace' && (
            <Workspace
              activeStep={workspaceActiveStep}
              setActiveStep={setWorkspaceActiveStep}
              importedFiles={importedFiles}
              selectedOperation={workspaceSelectedOperation}
              handleDataOperation={handleWorkspaceDataOperation}
              handleBrowseFiles={handleWorkspaceBrowseFiles}
              handleDragDropImport={handleWorkspaceDragDropImport}
              handleDeleteFile={handleWorkspaceDeleteFile}
              dataSourceHeight={600}
              previewHeight={400}
              dataPreviewHeight={300}
              selectedColumns={[]}
              selectedFiles={[]}
              handleColumnClick={() => {}}
              handleFileClick={() => {}}
              collapsedSheets={{}}
              toggleSheetCollapse={() => {}}
              renderFileColumns={() => null}
              lastSaved={lastSaved}
              formatTimeAgo={(date: Date) => {
                const now = new Date();
                const diffMs = now.getTime() - date.getTime();
                const diffMins = Math.floor(diffMs / 60000);
                if (diffMins < 1) return 'Just now';
                if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
                const diffHours = Math.floor(diffMins / 60);
                if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
                const diffDays = Math.floor(diffHours / 24);
                return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
              }}
              handleSaveChanges={() => {
                setLastSaved(new Date());
                console.log('Saving changes...');
              }}
              ArrowLeft={ArrowLeft}
              onNavigateToPlayground={() => navigate('/playground')}
            />
          )}

          {activeTab === 'settings' && (
            <Settings />
          )}



          {activeTab === 'notifications' && (
            <Notifications />
          )}

          {activeTab === 'analytics' && (
            <div className="flex-1 p-6 overflow-auto">
              <div className="text-center text-gray-500">
                <h2 className="text-2xl font-bold mb-4">Analytics</h2>
                <p>This section is under development.</p>
              </div>
            </div>
          )}
          </ErrorBoundary>
        </div>
      </div>

      {/* Create Project Dialog */}
      <CreateProjectDialog
        isOpen={showCreateProjectDialog}
        onClose={() => setShowCreateProjectDialog(false)}
        onCreateProject={handleCreateProjectSubmit}
      />
    </div>
  );
};

export default AppLayout; 