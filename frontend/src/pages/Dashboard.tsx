import React from 'react';
import { 
  Database, 
  BarChart3, 
  Workflow, 
  Zap, 
  Clock,
  Activity
} from 'lucide-react';
import { useBackend } from '../contexts/BackendContext';

const Dashboard: React.FC = () => {
  const { status, isConnected } = useBackend();

  const stats = [
    {
      name: 'Backend Status',
      value: isConnected ? 'Connected' : 'Disconnected',
      icon: Activity,
      color: isConnected ? 'text-green-600' : 'text-red-600',
      bgColor: isConnected ? 'bg-green-100' : 'bg-red-100',
    },
    {
      name: 'Port',
      value: status?.port || 'N/A',
      icon: Database,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Process',
      value: status?.processRunning ? 'Running' : 'Stopped',
      icon: Zap,
      color: status?.processRunning ? 'text-green-600' : 'text-red-600',
      bgColor: status?.processRunning ? 'bg-green-100' : 'bg-red-100',
    },
    {
      name: 'Last Heartbeat',
      value: status?.lastHeartbeat ? new Date(status.lastHeartbeat).toLocaleTimeString() : 'N/A',
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  const features = [
    {
      title: 'High-Performance Data Processing',
      description: 'Rust backend delivers 10x faster performance than Python',
      icon: Zap,
      color: 'text-yellow-600',
    },
    {
      title: 'Advanced Workflow Automation',
      description: 'Complex workflow execution with dependency management',
      icon: Workflow,
      color: 'text-blue-600',
    },
    {
      title: 'Real-time Visualizations',
      description: 'Interactive charts and dashboards for data insights',
      icon: BarChart3,
      color: 'text-green-600',
    },
    {
      title: 'Cross-Platform Support',
      description: 'Native applications for macOS, Linux, and Windows',
      icon: Database,
      color: 'text-purple-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Welcome to Unified Data Studio v2
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Next-generation data management, visualization, and workflow automation platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-3 rounded-md ${stat.bgColor} dark:bg-gray-700`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    {stat.name}
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <div key={feature.title} className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <Icon className={`w-8 h-8 ${feature.color}`} />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-gray-600 dark:text-gray-400">
                    {feature.description}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
            <Database className="w-5 h-5 mr-2" />
            Process Data
          </button>
          <button className="flex items-center justify-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
            <Workflow className="w-5 h-5 mr-2" />
            Create Workflow
          </button>
          <button className="flex items-center justify-center px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
            <BarChart3 className="w-5 h-5 mr-2" />
            View Charts
          </button>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Performance Metrics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">10x</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Faster than Python</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">70%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Less memory usage</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">&lt;100ms</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Backend startup</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
