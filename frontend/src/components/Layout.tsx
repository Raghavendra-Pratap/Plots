import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Menu, 
  X, 
  Database, 
  BarChart3, 
  Workflow, 
  Settings, 
  Sun, 
  Moon, 
  Monitor,
  Zap
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useBackend } from '../contexts/BackendContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { theme, setTheme } = useTheme();
  const { status, isConnected } = useBackend();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Data Processing', href: '/data-processing', icon: Database },
    { name: 'Workflows', href: '/workflows', icon: Workflow },
    { name: 'Visualizations', href: '/visualizations', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (href: string) => location.pathname === href;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Zap className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">UDS v2</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className="mr-3 w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Backend Status */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-600 dark:text-gray-400">Backend</span>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>
            {status && (
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Port: {status.port}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <div className="sticky top-0 z-40 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Page title */}
            <div className="flex-1 min-w-0">
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                {navigation.find(item => isActive(item.href))?.name || 'Unified Data Studio v2'}
              </h1>
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-4">
              {/* Theme toggle */}
              <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => setTheme('light')}
                  className={`p-2 rounded-md transition-colors ${
                    theme === 'light' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                  }`}
                >
                  <Sun className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setTheme('system')}
                  className={`p-2 rounded-md transition-colors ${
                    theme === 'system' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                  }`}
                >
                  <Monitor className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`p-2 rounded-md transition-colors ${
                    theme === 'dark' 
                      ? 'bg-white text-gray-900 shadow-sm' 
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                  }`}
                >
                  <Moon className="w-4 h-4" />
                </button>
              </div>

              {/* Backend status indicator */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout;
