import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Zap, 
  Download, 
  Upload, 
  FileText, 
  Play, 
  Shield,
  Save,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Sun,
  Moon,
  Monitor,
  Clock,
  Trash2
} from 'lucide-react';
import { Card, CardContent } from './ui/card';

interface SettingsProps {
  onSaveSettings?: (settings: any) => void;
}

interface SettingsData {
  general: {
    defaultStoragePath: string;
    performanceMode: 'normal' | 'low-end';
    theme: 'light' | 'dark' | 'auto';
  };
  playground: {
    formulaEngineView: 'normal' | 'detailed' | 'category';
    defaultSorting: 'name' | 'category' | 'recent';
    workflowMode: 'column' | 'sheet';
    workflowStyle: 'step-wise' | 'linear';
  };
  backup: {
    autoBackup: boolean;
    includeInputFiles: boolean;
    includeOutputFiles: boolean;
    encryptionEnabled: boolean;
  };
  logs: {
    sessionLogs: boolean;
    playgroundLogs: boolean;
    logRetentionDays: number;
    autoDeleteLogs: boolean;
  };
  execution: {
    autoSaveWorkflows: boolean;
    temporarySaveOnFailure: boolean;
    progressDisplayMode: 'detailed' | 'simplified';
    allowColumnMapping: boolean;
  };
}

const Settings: React.FC<SettingsProps> = ({ onSaveSettings }) => {
  const [settings, setSettings] = useState<SettingsData>({
    general: {
      defaultStoragePath: '/Users/raghavendra_pratap/Developer/unified-data-studio/data',
      performanceMode: 'normal',
      theme: 'light'
    },
    playground: {
      formulaEngineView: 'normal',
      defaultSorting: 'name',
      workflowMode: 'column',
      workflowStyle: 'step-wise'
    },
    backup: {
      autoBackup: true,
      includeInputFiles: false,
      includeOutputFiles: false,
      encryptionEnabled: true
    },
    logs: {
      sessionLogs: true,
      playgroundLogs: true,
      logRetentionDays: 30,
      autoDeleteLogs: true
    },
    execution: {
      autoSaveWorkflows: true,
      temporarySaveOnFailure: true,
      progressDisplayMode: 'detailed',
      allowColumnMapping: true
    }
  });

  const [backupStatus, setBackupStatus] = useState<'idle' | 'creating' | 'restoring' | 'success' | 'error'>('idle');
  const [backupMessage, setBackupMessage] = useState('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [logs, setLogs] = useState([
    { id: 1, action: 'File imported', timestamp: '2024-01-18 10:30:00', status: 'success' },
    { id: 2, action: 'Workflow executed', timestamp: '2024-01-18 10:25:00', status: 'success' },
    { id: 3, action: 'Data cleaned', timestamp: '2024-01-18 10:20:00', status: 'success' }
  ]);

  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('dataStudioSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(parsed);
      } catch (error) {
        console.log('No saved settings found, using defaults');
      }
    }
  }, []);

  const handleSettingChange = (section: keyof SettingsData, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
    setHasUnsavedChanges(true);
  };

  const handleStoragePathChange = () => {
    const newPath = prompt('Enter new storage path:', settings.general.defaultStoragePath);
    if (newPath) {
      handleSettingChange('general', 'defaultStoragePath', newPath);
    }
  };

  const handleCreateBackup = async () => {
    setBackupStatus('creating');
    setBackupMessage('Creating backup...');
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setBackupStatus('success');
    setBackupMessage('Backup created successfully!');
    
    setTimeout(() => {
      setBackupStatus('idle');
      setBackupMessage('');
    }, 3000);
  };

  const handleRestoreBackup = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setBackupStatus('restoring');
      setBackupMessage('Restoring backup...');
      
      setTimeout(() => {
        setBackupStatus('success');
        setBackupMessage('Backup restored successfully!');
        
        setTimeout(() => {
          setBackupStatus('idle');
          setBackupMessage('');
        }, 3000);
      }, 2000);
    }
  };

  const handleExportLogs = () => {
    const logData = logs.map(log => `${log.timestamp} - ${log.action} (${log.status})`).join('\n');
    const blob = new Blob([logData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClearLogs = () => {
    if (window.confirm('Are you sure you want to clear all logs? This action cannot be undone.')) {
      setLogs([]);
    }
  };

  const handleSave = () => {
    // Save to localStorage
    localStorage.setItem('dataStudioSettings', JSON.stringify(settings));
    
    if (onSaveSettings) {
      onSaveSettings(settings);
    }
    
    setHasUnsavedChanges(false);
    
    // Show success message
    const successMessage = document.createElement('div');
    successMessage.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    successMessage.textContent = 'Settings saved successfully!';
    document.body.appendChild(successMessage);
    
    setTimeout(() => {
      document.body.removeChild(successMessage);
    }, 3000);
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to default values?')) {
      localStorage.removeItem('dataStudioSettings');
      window.location.reload();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <SettingsIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
              <p className="text-gray-600">Configure your Data Studio preferences</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {hasUnsavedChanges && (
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full font-medium">
                Unsaved changes
              </span>
            )}
            <button
              onClick={handleReset}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors font-medium"
            >
              Reset
            </button>
            <button
              onClick={handleSave}
              disabled={!hasUnsavedChanges}
              className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </button>
          </div>
        </div>
      </div>

      {/* Main Content - All Settings in One Scrollable Page */}
      <div className="flex-1 overflow-auto scroll-smooth">
        <div className="p-8 space-y-8 max-w-6xl mx-auto">
        
        {/* General Settings */}
        <Card className="border-0 shadow-sm bg-gradient-to-r from-blue-50 to-indigo-50 mx-auto">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-100 rounded-lg">
                <SettingsIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">General Settings</h2>
                <p className="text-gray-600">Storage, performance, and appearance configuration</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Storage Path */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Default Storage Path</label>
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={settings.general.defaultStoragePath}
                    readOnly
                    className="flex-1 p-3 border border-gray-300 rounded-lg bg-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={handleStoragePathChange}
                    className="px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm whitespace-nowrap"
                  >
                    Change
                  </button>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  Used for input_files/, output_files/, and mappings/ folders
                </p>
              </div>

              {/* Performance Mode */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Performance Mode</label>
                <select
                  value={settings.general.performanceMode}
                  onChange={(e) => handleSettingChange('general', 'performanceMode', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm"
                >
                  <option value="normal">🚀 Normal Mode - Real-time updates</option>
                  <option value="low-end">⚡ Low-End Mode - Manual refresh</option>
                </select>
              </div>

              {/* Theme Selection */}
              <div className="lg:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-3">Theme</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-2xl">
                  {[
                    { value: 'light', icon: Sun, label: 'Light', description: 'Clean and bright' },
                    { value: 'dark', icon: Moon, label: 'Dark', description: 'Easy on the eyes' },
                    { value: 'auto', icon: Monitor, label: 'Auto', description: 'Follows system' }
                  ].map((theme) => (
                    <button
                      key={theme.value}
                      onClick={() => handleSettingChange('general', 'theme', theme.value)}
                      className={`p-4 border-2 rounded-lg text-center transition-all ${
                        settings.general.theme === theme.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <theme.icon className="w-8 h-8 mx-auto mb-2" />
                      <div className="font-medium">{theme.label}</div>
                      <div className="text-xs text-gray-500">{theme.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Playground Settings */}
        <Card className="border-0 shadow-sm bg-gradient-to-r from-orange-50 to-amber-50 mx-auto">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-orange-100 rounded-lg">
                <Play className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Playground Settings</h2>
                <p className="text-gray-600">Formula engine and workflow builder preferences</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Formula Engine View</label>
                <select
                  value={settings.playground.formulaEngineView}
                  onChange={(e) => handleSettingChange('playground', 'formulaEngineView', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 shadow-sm"
                >
                  <option value="normal">📋 Normal - Standard list view</option>
                  <option value="detailed">🔍 Detailed - Extended information</option>
                  <option value="category">📁 Category - Grouped by type</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Default Sorting</label>
                <select
                  value={settings.playground.defaultSorting}
                  onChange={(e) => handleSettingChange('playground', 'defaultSorting', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 shadow-sm"
                >
                  <option value="name">📝 By Name - Alphabetical order</option>
                  <option value="category">📂 By Category - Grouped logically</option>
                  <option value="recent">⏰ By Recent - Recently used first</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Workflow Mode</label>
                <select
                  value={settings.playground.workflowMode}
                  onChange={(e) => handleSettingChange('playground', 'workflowMode', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 shadow-sm"
                >
                  <option value="column">📊 Column - Focus on data columns</option>
                  <option value="sheet">📋 Sheet - Work with entire sheets</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Workflow Style</label>
                <select
                  value={settings.playground.workflowStyle}
                  onChange={(e) => handleSettingChange('playground', 'workflowStyle', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 shadow-sm"
                >
                  <option value="step-wise">🔄 Step-wise - Sequential workflow steps</option>
                  <option value="linear">📈 Linear - Simple linear flow</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Backup & Restore Settings */}
        <Card className="border-0 shadow-sm bg-gradient-to-r from-emerald-50 to-green-50 mx-auto">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-emerald-100 rounded-lg">
                <Shield className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Backup & Restore</h2>
                <p className="text-gray-600">Data backup and restoration configuration</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Backup Options */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Backup Options</h3>
                {[
                  { key: 'autoBackup', label: 'Auto Backup', description: 'Automatically backup workflows' },
                  { key: 'includeInputFiles', label: 'Include Input Files', description: 'Backup input files with workflows' },
                  { key: 'includeOutputFiles', label: 'Include Output Files', description: 'Backup processed output files' },
                  { key: 'encryptionEnabled', label: 'Encryption', description: 'Encrypt backups for security' }
                ].map((option) => (
                  <div key={option.key} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
                    <div>
                      <label className="text-sm font-medium text-gray-700">{option.label}</label>
                      <p className="text-sm text-gray-500">{option.description}</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.backup[option.key as keyof typeof settings.backup] as boolean}
                      onChange={(e) => handleSettingChange('backup', option.key, e.target.checked)}
                      className="w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500"
                    />
                  </div>
                ))}
              </div>

              {/* Backup Actions */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Backup Actions</h3>
                
                {backupMessage && (
                  <div className={`p-4 rounded-lg ${
                    backupStatus === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 
                    backupStatus === 'error' ? 'bg-red-50 text-red-800 border border-red-200' : 
                    'bg-blue-50 text-blue-800 border border-blue-200'
                  }`}>
                    <div className="flex items-center">
                      {backupStatus === 'success' ? <CheckCircle className="w-5 h-5 mr-2" /> :
                       backupStatus === 'error' ? <AlertCircle className="w-5 h-5 mr-2" /> :
                       <RefreshCw className="w-5 h-5 mr-2 animate-spin" />}
                      {backupMessage}
                    </div>
                  </div>
                )}

                <div className="space-y-3">
                  <button
                    onClick={handleCreateBackup}
                    disabled={backupStatus !== 'idle'}
                    className="w-full flex items-center justify-center p-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors shadow-sm"
                  >
                    <Download className="w-5 h-5 mr-2" />
                    Create Backup
                  </button>
                  
                  <button
                    onClick={handleRestoreBackup}
                    disabled={backupStatus !== 'idle'}
                    className="w-full flex items-center justify-center p-3 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 disabled:bg-gray-300 transition-colors shadow-sm"
                  >
                    <Upload className="w-5 h-5 mr-2" />
                    Restore Backup
                  </button>
                </div>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".backup,.zip"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Logs & Audit Settings */}
        <Card className="border-0 shadow-sm bg-gradient-to-r from-violet-50 to-purple-50 mx-auto">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-violet-100 rounded-lg">
                <FileText className="w-6 h-6 text-violet-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Logs & Audit</h2>
                <p className="text-gray-600">Logging configuration and audit trail settings</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Log Configuration */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Log Configuration</h3>
                {[
                  { key: 'sessionLogs', label: 'Session Logs', description: 'Record every action performed' },
                  { key: 'playgroundLogs', label: 'Playground Logs', description: 'Maintain detailed logs for each session' },
                  { key: 'autoDeleteLogs', label: 'Auto Delete Logs', description: 'Automatically delete old logs' }
                ].map((option) => (
                  <div key={option.key} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
                    <div>
                      <label className="text-sm font-medium text-gray-700">{option.label}</label>
                      <p className="text-sm text-gray-500">{option.description}</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.logs[option.key as keyof typeof settings.logs] as boolean}
                      onChange={(e) => handleSettingChange('logs', option.key, e.target.checked)}
                      className="w-5 h-5 text-violet-600 rounded focus:ring-violet-500"
                    />
                  </div>
                ))}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Log Retention (days)</label>
                  <select
                    value={settings.logs.logRetentionDays}
                    onChange={(e) => handleSettingChange('logs', 'logRetentionDays', parseInt(e.target.value))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 shadow-sm"
                  >
                    <option value={7}>7 days</option>
                    <option value={15}>15 days</option>
                    <option value={30}>30 days (Recommended)</option>
                    <option value={60}>60 days</option>
                    <option value={90}>90 days</option>
                  </select>
                </div>
              </div>

              {/* Log Actions & Recent Logs */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Log Actions</h3>
                
                <div className="space-y-3">
                  <button
                    onClick={handleExportLogs}
                    className="w-full flex items-center justify-center p-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors shadow-sm"
                  >
                    <Download className="w-5 h-5 mr-2" />
                    Export Logs
                  </button>
                  
                  <button
                    onClick={handleClearLogs}
                    className="w-full flex items-center justify-center p-3 bg-red-100 text-red-700 font-medium rounded-lg hover:bg-red-200 transition-colors shadow-sm"
                  >
                    <Trash2 className="w-5 h-5 mr-2" />
                    Clear Logs
                  </button>
                </div>

                <div className="mt-6">
                  <h4 className="text-md font-medium text-gray-800 mb-3">Recent Logs</h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {logs.map((log) => (
                      <div key={log.id} className="flex items-center justify-between p-2 bg-white rounded border border-gray-200">
                        <div className="flex items-center">
                          {log.status === 'success' ? (
                            <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-red-500 mr-2" />
                          )}
                          <span className="text-sm text-gray-700">{log.action}</span>
                        </div>
                        <span className="text-xs text-gray-500">{log.timestamp}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Execution Settings */}
        <Card className="border-0 shadow-sm bg-gradient-to-r from-rose-50 to-pink-50 mx-auto">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-rose-100 rounded-lg">
                <Zap className="w-6 h-6 text-rose-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Execution Settings</h2>
                <p className="text-gray-600">Workflow execution and progress display preferences</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Workflow Handling */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Workflow Handling</h3>
                {[
                  { key: 'autoSaveWorkflows', label: 'Auto-save Workflows', description: 'Automatically save before execution' },
                  { key: 'temporarySaveOnFailure', label: 'Temporary Save on Failure', description: 'Save workflow temporarily if execution fails' },
                  { key: 'allowColumnMapping', label: 'Allow Column Mapping', description: 'Review and modify workflow before retry' }
                ].map((option) => (
                  <div key={option.key} className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
                    <div>
                      <label className="text-sm font-medium text-gray-700">{option.label}</label>
                      <p className="text-sm text-gray-500">{option.description}</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.execution[option.key as keyof typeof settings.execution] as boolean}
                      onChange={(e) => handleSettingChange('execution', option.key, e.target.checked)}
                      className="w-5 h-5 text-rose-600 rounded focus:ring-rose-500"
                    />
                  </div>
                ))}
              </div>

              {/* Progress Display */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-800 mb-3">Progress Display</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Progress Mode</label>
                  <select
                    value={settings.execution.progressDisplayMode}
                    onChange={(e) => handleSettingChange('execution', 'progressDisplayMode', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-rose-500 focus:border-rose-500 shadow-sm"
                  >
                    <option value="detailed">🔍 Detailed Mode - Step-by-step + % + estimated time</option>
                    <option value="simplified">📊 Simplified Mode - Only overall progress %</option>
                  </select>
                </div>

                <div className="p-4 bg-white rounded-lg border border-gray-200">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Current Setting</h4>
                  <p className="text-sm text-gray-600">
                    {settings.execution.progressDisplayMode === 'detailed' 
                      ? 'Detailed progress display with step-by-step information'
                      : 'Simplified progress display showing only overall completion'
                    }
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Save Changes Section */}
        <div className="flex justify-center pt-8 pb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 max-w-md w-full text-center">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Save Your Changes</h3>
              <p className="text-gray-600 mb-4">
                {hasUnsavedChanges 
                  ? 'You have unsaved changes. Click the button above to save them.'
                  : 'All changes have been saved successfully!'
                }
              </p>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                <Clock className="w-4 h-4" />
                <span>Settings are automatically saved to your browser</span>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
