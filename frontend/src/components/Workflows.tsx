import React, { useState, useEffect } from 'react';
import { Play, Edit3, Trash2, AlertCircle, Folder, Users, GitBranch } from 'lucide-react';

interface WorkflowStep {
  id: string;
  operation: string;
  parameters: Record<string, any>;
  order: number;
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

interface WorkflowItemProps {
  workflow: Workflow;
  onEdit: (workflow: Workflow) => void;
  onRun: (workflow: Workflow) => void;
  onDelete: (workflow: Workflow) => void;
}

const WorkflowItem: React.FC<WorkflowItemProps> = ({ workflow, onEdit, onRun, onDelete }) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = React.useState(false);

  return (
    <div className="p-3 bg-white border rounded-lg hover:shadow-md transition-shadow relative">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{workflow.name}</h4>
          <p className="text-sm text-gray-500">{workflow.description}</p>
          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
            <span>{workflow.steps.length} steps</span>
            <span className="flex items-center">
              <Folder className="w-3 h-3 mr-1" />
              {workflow.project}
            </span>
            <span>Modified: {workflow.lastModified.toLocaleDateString()}</span>
            {workflow.version && <span>v{workflow.version}</span>}
          </div>
          {workflow.filePatterns && workflow.filePatterns.length > 0 && (
            <div className="mt-2 text-xs text-blue-600">
              <span className="font-medium">File Patterns:</span> {workflow.filePatterns.length} patterns
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onRun(workflow)}
            className="p-2 text-green-600 hover:bg-green-50 rounded-md"
            title="Run Workflow"
          >
            <Play className="w-4 h-4" />
          </button>
          <button
            onClick={() => onEdit(workflow)}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-md"
            title="Edit Workflow"
          >
            <Edit3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="p-2 text-red-600 hover:bg-red-50 rounded-md"
            title="Delete Workflow"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
      {showDeleteConfirm && (
        <div className="absolute right-0 top-0 mt-8 w-64 p-3 bg-white rounded-lg shadow-lg border z-10">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">Delete Workflow?</h4>
              <p className="text-xs text-gray-500 mt-1">
                Are you sure you want to delete "{workflow.name}"?
              </p>
              <div className="flex justify-end space-x-2 mt-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-2 py-2 text-xs text-gray-600 hover:bg-gray-100 rounded"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    onDelete(workflow);
                    setShowDeleteConfirm(false);
                  }}
                  className="px-2 py-2 text-xs text-white bg-red-500 hover:bg-red-600 rounded"
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

interface WorkflowsProps {
  workflows: Workflow[];
  selectedProject: any;
  onRunWorkflow: (workflow: Workflow) => void;
  onEditWorkflow: (workflow: Workflow) => void;
  onDeleteWorkflow: (workflow: Workflow) => void;
}

// Project Card Component for Project View
const ProjectCard: React.FC<{
  projectName: string;
  workflows: Workflow[];
  onSelectProject: (projectName: string) => void;
  onRunWorkflow: (workflow: Workflow) => void;
  onEditWorkflow: (workflow: Workflow) => void;
  onDeleteWorkflow: (workflow: Workflow) => void;
}> = ({ projectName, workflows, onSelectProject, onRunWorkflow, onEditWorkflow, onDeleteWorkflow }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div 
        className="p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Folder className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">{projectName}</h3>
              <p className="text-sm text-gray-500">{workflows.length} workflow{workflows.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSelectProject(projectName);
              }}
              className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
            >
              View All
            </button>
            <div className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>
      </div>
      
      {isExpanded && (
        <div className="border-t border-gray-100 px-4 pb-4">
          <div className="space-y-2 mt-3">
            {workflows.slice(0, 3).map((workflow) => (
              <div key={workflow.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{workflow.name}</p>
                  <p className="text-xs text-gray-500">{workflow.steps.length} steps</p>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => onRunWorkflow(workflow)}
                    className="p-1 text-green-600 hover:bg-green-100 rounded"
                    title="Run Workflow"
                  >
                    <Play className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => onEditWorkflow(workflow)}
                    className="p-1 text-blue-600 hover:bg-blue-100 rounded"
                    title="Edit Workflow"
                  >
                    <Edit3 className="w-3 h-3" />
                  </button>
                  <button
                    onClick={() => onDeleteWorkflow(workflow)}
                    className="p-1 text-red-600 hover:bg-red-100 rounded"
                    title="Delete Workflow"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
            {workflows.length > 3 && (
              <div className="text-center pt-2">
                <button
                  onClick={() => onSelectProject(projectName)}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  View {workflows.length - 3} more workflows...
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const Workflows: React.FC<WorkflowsProps> = ({ 
  workflows, 
  selectedProject, 
  onRunWorkflow, 
  onEditWorkflow, 
  onDeleteWorkflow 
}) => {
  const [projectFilter, setProjectFilter] = useState<string>('all');
  const [availableProjects, setAvailableProjects] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'projects' | 'workflows'>('workflows');
  const [selectedProjectFilter, setSelectedProjectFilter] = useState<string | null>(null);

  // Load available projects
  useEffect(() => {
    const uniqueProjects = Array.from(new Set(workflows.map(w => w.project)));
    setAvailableProjects(uniqueProjects);
  }, [workflows]);

  // Filter workflows based on selected project and view mode
  const filteredWorkflows = workflows.filter(w => {
    if (selectedProject) {
      return w.project === selectedProject.name;
    }
    if (selectedProjectFilter) {
      return w.project === selectedProjectFilter;
    }
    if (projectFilter === 'all') {
      return true;
    }
    return w.project === projectFilter;
  });

  // Group workflows by project for project view
  const workflowsByProject = workflows.reduce((acc, workflow) => {
    if (!acc[workflow.project]) {
      acc[workflow.project] = [];
    }
    acc[workflow.project].push(workflow);
    return acc;
  }, {} as Record<string, Workflow[]>);

  const handleProjectSelect = (projectName: string) => {
    setSelectedProjectFilter(projectName);
    setViewMode('workflows');
  };

  const clearProjectFilter = () => {
    setSelectedProjectFilter(null);
  };

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-bold">
            Workflows {selectedProject && `- ${selectedProject.name}`}
            {selectedProjectFilter && ` - ${selectedProjectFilter}`}
          </h2>
          {selectedProjectFilter && (
            <button
              onClick={clearProjectFilter}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded-md hover:bg-gray-200"
            >
              Clear Filter
            </button>
          )}
        </div>
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => window.location.href = '/playground'}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Play className="w-4 h-4 mr-2" />
            Open Playground
          </button>
          {/* View Mode Toggle */}
          {!selectedProject && !selectedProjectFilter && (
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('projects')}
                className={`px-3 py-2 text-sm rounded-md transition-colors flex items-center space-x-2 ${
                  viewMode === 'projects'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>Projects</span>
              </button>
              <button
                onClick={() => setViewMode('workflows')}
                className={`px-3 py-2 text-sm rounded-md transition-colors flex items-center space-x-2 ${
                  viewMode === 'workflows'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <GitBranch className="w-4 h-4" />
                <span>Workflows</span>
              </button>
            </div>
          )}
          
          {/* Project Filter for Workflow View */}
          {!selectedProject && !selectedProjectFilter && viewMode === 'workflows' && (
            <select
              value={projectFilter}
              onChange={(e) => setProjectFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Projects</option>
              {availableProjects.map(project => (
                <option key={project} value={project}>{project}</option>
              ))}
            </select>
          )}
          

        </div>
      </div>
      
      {/* Content based on view mode */}
      {viewMode === 'projects' && !selectedProjectFilter ? (
        <div>
          <div className="mb-4 text-sm text-gray-600">
            {Object.keys(workflowsByProject).length} project{Object.keys(workflowsByProject).length !== 1 ? 's' : ''} with workflows
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(workflowsByProject).map(([projectName, projectWorkflows]) => (
              <ProjectCard
                key={projectName}
                projectName={projectName}
                workflows={projectWorkflows}
                onSelectProject={handleProjectSelect}
                onRunWorkflow={onRunWorkflow}
                onEditWorkflow={onEditWorkflow}
                onDeleteWorkflow={onDeleteWorkflow}
              />
            ))}
          </div>
          {Object.keys(workflowsByProject).length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Folder className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium mb-2">No projects with workflows found</h3>
              <p className="text-sm">Create your first workflow to get started</p>
            </div>
          )}
        </div>
      ) : (
        <div>
          <div className="mb-4 text-sm text-gray-600">
            {filteredWorkflows.length} workflow{filteredWorkflows.length !== 1 ? 's' : ''} found
            {projectFilter !== 'all' && ` in project "${projectFilter}"`}
            {selectedProjectFilter && ` in project "${selectedProjectFilter}"`}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredWorkflows.length === 0 ? (
              <div className="col-span-2 text-center py-12 text-gray-500">
                <GitBranch className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium mb-2">No workflows found</h3>
                <p className="text-sm">
                  {projectFilter === 'all' && !selectedProjectFilter
                    ? 'Create your first workflow to get started'
                    : `No workflows found in the selected project`
                  }
                </p>
              </div>
            ) : (
              filteredWorkflows.map((workflow) => (
                <WorkflowItem
                  key={workflow.id}
                  workflow={workflow}
                  onRun={onRunWorkflow}
                  onEdit={onEditWorkflow}
                  onDelete={onDeleteWorkflow}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Workflows;
