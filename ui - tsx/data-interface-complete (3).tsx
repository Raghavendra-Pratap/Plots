import React, { useState } from 'react';
import { 
  Layout, Home, Database, GitBranch, BarChart2, Download, 
  Settings, Plus, Upload, FileText, ChevronRight, File,
  Trash2, AlertCircle
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

// Custom Tooltip Component
const IconWithTooltip = ({ icon: Icon, label, active, onClick }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative" onMouseEnter={() => setShowTooltip(true)} onMouseLeave={() => setShowTooltip(false)}>
      <div
        onClick={onClick}
        className={`p-3 rounded-lg cursor-pointer transition-colors relative ${
          active ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
        }`}
      >
        <Icon className="w-6 h-6" />
      </div>
      
      {showTooltip && (
        <div className="absolute left-14 top-1/2 -translate-y-1/2 bg-gray-800 text-white px-3 py-2 rounded-md text-sm whitespace-nowrap z-50">
          <div className="absolute left-0 top-1/2 -translate-x-1 -translate-y-1/2 border-4 border-transparent border-r-gray-800" />
          {label}
        </div>
      )}
    </div>
  );
};

const DataSourceItem = ({ file, onDelete }) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  return (
    <div className="group relative p-2 bg-gray-50 rounded-md text-sm hover:bg-gray-100">
      <div className="flex items-center justify-between">
        <span className="truncate">{file.name}</span>
        <button
          onClick={() => setShowDeleteConfirm(true)}
          className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-red-50 rounded-md"
        >
          <Trash2 className="w-4 h-4 text-red-500" />
        </button>
      </div>
      {showDeleteConfirm && (
        <div className="absolute right-0 top-0 mt-8 w-64 p-3 bg-white rounded-lg shadow-lg border z-10">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">Delete File?</h4>
              <p className="text-xs text-gray-500 mt-1">
                Are you sure you want to delete "{file.name}"?
              </p>
              <div className="flex justify-end space-x-2 mt-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 rounded"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    onDelete(file);
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

const FileColumnDisplay = ({ files }) => (
  <div className="bg-white border-t">
    <div className="max-w-full overflow-x-auto">
      <div className="flex p-4 space-x-8">
        {files.map((file, index) => (
          <div key={index} className="min-w-[200px]">
            <div className="flex items-center space-x-2 pb-3 border-b border-gray-200">
              <File className="w-4 h-4 text-gray-500" />
              <h3 className="font-medium text-gray-800">{file.name}</h3>
              <span className="text-xs text-gray-500">({file.columns.length} columns)</span>
            </div>
            <div className="mt-3 space-y-2">
              {file.columns.map((column, colIndex) => (
                <div 
                  key={colIndex}
                  className="flex items-center p-2 rounded-md hover:bg-gray-50 cursor-pointer text-sm"
                >
                  <div className="w-2 h-2 rounded-full bg-blue-500 mr-2" />
                  <span>{column}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const MergedInterface = () => {
  const [activeTab, setActiveTab] = useState('workspace');
  const [activeStep, setActiveStep] = useState('import');
  const [importedFiles, setImportedFiles] = useState([
    {
      name: 'sales_data.csv',
      columns: ['Date', 'Product ID', 'Customer Name', 'Quantity', 'Price', 'Total']
    },
    {
      name: 'customer_info.xlsx',
      columns: ['Customer ID', 'Name', 'Email', 'Address', 'Phone', 'Joined Date']
    }
  ]);

  const sidebarItems = [
    { icon: Home, id: 'dashboard', label: 'Dashboard' },
    { icon: Database, id: 'workspace', label: 'Workspace' },
    { icon: GitBranch, id: 'projects', label: 'Projects' },
    { icon: BarChart2, id: 'analytics', label: 'Analytics' },
    { icon: Settings, id: 'settings', label: 'Settings' }
  ];

  const steps = [
    { id: 'import', icon: Upload, label: 'Import' },
    { id: 'clean', icon: Database, label: 'Clean' },
    { id: 'transform', icon: GitBranch, label: 'Transform' },
    { id: 'analyze', icon: BarChart2, label: 'Analyze' },
    { id: 'export', icon: Download, label: 'Export' }
  ];

  const handleDeleteFile = (fileToDelete) => {
    setImportedFiles(importedFiles.filter(file => file.name !== fileToDelete.name));
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar Navigation with Tooltips */}
      <div className="w-16 bg-gray-900 flex flex-col items-center py-6 space-y-8">
        <div className="text-white relative group">
          <Layout className="w-6 h-6" />
        </div>
        
        {sidebarItems.map((item) => (
          <IconWithTooltip
            key={item.id}
            icon={item.icon}
            label={item.label}
            active={activeTab === item.id}
            onClick={() => setActiveTab(item.id)}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white h-16 px-6 flex items-center justify-between border-b">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold">Data Processing Dashboard</h1>
            <div className="flex items-center text-sm text-gray-500">
              <span>Projects</span>
              <ChevronRight className="w-4 h-4 mx-1" />
              <span>Sales Analysis</span>
            </div>
          </div>
          <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </button>
        </div>

        <div className="flex h-[calc(100vh-64px)]">
          {activeTab === 'workspace' ? (
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
              <div className="flex-1 p-6 overflow-auto">
                <div className="grid grid-cols-12 gap-6">
                  {/* Left Panel - Data Sources */}
                  <Card className="col-span-3 h-[calc(100vh-240px)] overflow-y-auto">
                    <CardContent className="p-4">
                      <h3 className="font-semibold mb-4 flex items-center">
                        <FileText className="w-4 h-4 mr-2" />
                        Data Sources
                      </h3>
                      <div className="space-y-2">
                        {importedFiles.map((file) => (
                          <DataSourceItem
                            key={file.name}
                            file={file}
                            onDelete={handleDeleteFile}
                          />
                        ))}
                        {importedFiles.length === 0 && (
                          <div className="text-center text-gray-500 text-sm p-4">
                            No files imported
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Center Panel - Main Workspace */}
                  <Card className="col-span-6 h-[calc(100vh-240px)] overflow-y-auto">
                    <CardContent className="p-4">
                      {activeStep === 'import' && (
                        <div className="text-center p-12 border-2 border-dashed rounded-lg">
                          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                          <h3 className="text-lg font-semibold mb-2">Drop Files Here</h3>
                          <p className="text-sm text-gray-500">Support for CSV, Excel files</p>
                        </div>
                      )}
                      {activeStep === 'clean' && (
                        <div className="space-y-4">
                          <h3 className="font-semibold mb-4">Data Cleaning Tools</h3>
                          <div className="grid grid-cols-2 gap-4">
                            {['Remove Duplicates', 'Fix Missing Values', 'Standardize Format', 'Filter Data'].map((tool) => (
                              <div key={tool} className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                                {tool}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {activeStep === 'transform' && (
                        <div className="space-y-4">
                          <h3 className="font-semibold mb-4">Transformation Options</h3>
                          <div className="grid grid-cols-2 gap-4">
                            {['Join Datasets', 'Aggregate Data', 'Split Columns', 'Format Values'].map((tool) => (
                              <div key={tool} className="p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                                {tool}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Right Panel - Properties */}
                  <Card className="col-span-3 h-[calc(100vh-240px)] overflow-y-auto">
                    <CardContent className="p-4">
                      <h3 className="font-semibold mb-4 flex items-center">
                        <Settings className="w-4 h-4 mr-2" />
                        Properties
                      </h3>
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <label className="text-sm font-medium">Data Type</label>
                          <select className="w-full p-2 border rounded-md bg-white">
                            <option>String</option>
                            <option>Number</option>
                            <option>Date</option>
                          </select>
                        </div>
                        <div className="space-y-2">
                          <label className="text-sm font-medium">Format</label>
                          <input type="text" className="w-full p-2 border rounded-md" placeholder="Format pattern" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Bottom Status Bar */}
              <div className="bg-white border-t px-6 py-3 flex justify-between items-center">
                <span className="text-sm text-gray-600">
                  {importedFiles.length} file{importedFiles.length !== 1 ? 's' : ''} selected
                </span>
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-600">Last saved: 2 mins ago</span>
                  <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                    Save Changes
                  </button>
                </div>
              </div>

              {importedFiles.length > 0 && <FileColumnDisplay files={importedFiles} />}
            </div>
          ) : (
            // Dashboard View
            <div className="flex-1 p-6 overflow-auto">
              <div className="grid grid-cols-3 gap-6 mb-6">
                {/* Quick Stats */}
                {[
                  { label: 'Active Projects', value: '12' },
                  { label: 'Processed Files', value: '1,234' },
                  { label: 'Data Volume', value: '2.4 TB' }
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
                      {[
                        { name: 'Sales Analysis Q4', date: '2 hours ago', status: 'active' },
                        { name: 'Customer Data Clean', date: '5 hours ago', status: 'completed' },
                        { name: 'Product Inventory', date: '1 day ago', status: 'active' }
                      ].map((project) => (
                        <div key={project.name} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                          <div>
                            <h3 className="font-medium">{project.name}</h3>
                            <p className="text-sm text-gray-500">{project.date}</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-sm ${
                            project.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                          }`}>
                            {project.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Activity */}
                <Card>
                  <CardContent className="p-6">
                    <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
                    <div className="space-y-4">
                      {[
                        'Data import completed: sales_data.csv',
                        'Workflow "Clean Customer Data" updated',
                        'New analysis report generated',
                        'Export completed: Q4_analysis.xlsx'
                      ].map((activity, index) => (
                        <div key={index} className="flex items-center text-sm">
                          <div className="w-2 h-2 bg-blue-600 rounded-full mr-3" />
                          {activity}
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
                        { icon: BarChart2, label: 'Analytics' },
                        { icon: Download, label: 'Export' }
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
          )}
        </div>
      </div>
    </div>
  );
};

export default MergedInterface;
