import React from 'react';
import { Card, CardContent } from './ui/card';
import { Folder, GitBranch, Upload, Play } from 'lucide-react';

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

interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  created: Date;
  lastModified: Date;
  project: string;
}

interface WorkflowStep {
  id: string;
  operation: string;
  parameters: Record<string, any>;
  order: number;
}

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

interface DashboardProps {
  projects: Project[];
  workflows: Workflow[];
  importedFiles: FileData[];
  getTotalDataVolume: () => number;
  formatDataVolume: (bytes: number) => string;
}

const Dashboard: React.FC<DashboardProps> = ({ 
  projects, 
  workflows, 
  importedFiles, 
  getTotalDataVolume, 
  formatDataVolume 
}) => {
  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="grid grid-cols-3 gap-6 mb-6">
        {/* Quick Stats */}
        {[
          { label: 'Active Projects', value: projects.length.toString() },
          { label: 'Total Workflows', value: workflows.length.toString() },
          { label: 'Data Volume', value: formatDataVolume(getTotalDataVolume()) }
        ].map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-6">
              <h3 className="text-gray-500 text-sm">{stat.label}</h3>
              <p className="text-2xl font-bold mt-2">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Recent Projects */}
        <Card className="row-span-2">
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Projects</h2>
            <div className="space-y-4">
              {projects.slice(0, 3).map((project) => (
                <div key={project.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium">{project.name}</h3>
                    <p className="text-sm text-gray-500">{project.description}</p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700">
                    {project.workflows.length} workflows
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Workflows */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-4">Recent Workflows</h2>
            <div className="space-y-4">
              {workflows.slice(0, 3).map((workflow) => (
                <div key={workflow.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h3 className="font-medium">{workflow.name}</h3>
                    <p className="text-sm text-gray-500">{workflow.project}</p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-sm bg-green-100 text-green-700">
                    {workflow.steps.length} steps
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
            <div className="grid grid-cols-2 gap-4">
              {[
                { icon: Upload, label: 'Import Data' },
                { icon: GitBranch, label: 'New Workflow' },
                { icon: Folder, label: 'New Project' },
                { icon: Play, label: 'Run Workflow' }
              ].map((action) => (
                <button
                  key={action.label}
                  className="p-4 bg-gray-50 rounded-lg flex flex-col items-center justify-center hover:bg-gray-100"
                >
                  <action.icon className="w-6 h-6 mb-2" />
                  <span className="text-sm">{action.label}</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
