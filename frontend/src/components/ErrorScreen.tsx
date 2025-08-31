import React from 'react';
import { AlertTriangle, RefreshCw, Home, Settings } from 'lucide-react';

interface ErrorScreenProps {
  error: string;
  onRetry: () => void;
}

const ErrorScreen: React.FC<ErrorScreenProps> = ({ error, onRetry }) => {
  return (
    <div className="error-screen">
      <div className="text-center space-y-6 max-w-2xl mx-auto">
        {/* Error Icon */}
        <div className="flex justify-center">
          <AlertTriangle className="w-24 h-24 text-red-300" />
        </div>
        
        {/* Title */}
        <h1 className="text-4xl font-bold text-white">
          Something went wrong
        </h1>
        
        {/* Error Message */}
        <div className="bg-red-900/30 p-6 rounded-lg border border-red-500/30">
          <p className="text-lg text-red-100 font-mono break-words">
            {error}
          </p>
        </div>
        
        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={onRetry}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Try Again</span>
          </button>
          
          <button
            onClick={() => window.location.reload()}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
          >
            <Home className="w-5 h-5" />
            <span>Reload App</span>
          </button>
        </div>
        
        {/* Troubleshooting Tips */}
        <div className="mt-8 text-left bg-white/10 p-6 rounded-lg backdrop-blur-sm">
          <h3 className="text-lg font-semibold text-white mb-4">Troubleshooting Tips</h3>
          <ul className="space-y-2 text-sm text-blue-100">
            <li className="flex items-start space-x-2">
              <span className="text-blue-300">•</span>
              <span>Check if the backend process is running</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-blue-300">•</span>
              <span>Verify no other applications are using port 5002</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-blue-300">•</span>
              <span>Ensure you have the required permissions</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-blue-300">•</span>
              <span>Check the console for detailed error messages</span>
            </li>
          </ul>
        </div>
        
        {/* Technical Details */}
        <details className="text-left">
          <summary className="cursor-pointer text-blue-200 hover:text-blue-100">
            <Settings className="inline w-4 h-4 mr-2" />
            Technical Details
          </summary>
          <div className="mt-2 p-4 bg-black/20 rounded text-xs text-gray-300 font-mono">
            <div>Platform: {navigator.platform}</div>
            <div>User Agent: {navigator.userAgent}</div>
            <div>Timestamp: {new Date().toISOString()}</div>
            <div>Error: {error}</div>
          </div>
        </details>
        
        {/* Footer */}
        <div className="mt-8 text-sm text-red-200">
          If the problem persists, please check the console logs or restart the application.
        </div>
      </div>
    </div>
  );
};

export default ErrorScreen;
