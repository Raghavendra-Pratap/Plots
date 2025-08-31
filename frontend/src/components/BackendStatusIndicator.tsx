import React, { useState, useEffect } from 'react';
import { backendStatusService, BackendStatus } from '../services/BackendStatusService';

const BackendStatusIndicator: React.FC = () => {
  const [status, setStatus] = useState<BackendStatus>({
    status: 'checking',
    timestamp: new Date()
  });

  useEffect(() => {
    // Subscribe to backend status updates
    const unsubscribe = backendStatusService.subscribe((newStatus) => {
      setStatus(newStatus);
    });

    // Cleanup subscription on unmount
    return unsubscribe;
  }, []);

  const getStatusColor = (status: BackendStatus['status']) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'error':
      case 'timeout':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'starting':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'checking':
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: BackendStatus['status']) => {
    switch (status) {
      case 'running':
        return 'Backend Connected';
      case 'error':
        return 'Backend Error';
      case 'timeout':
        return 'Backend Timeout';
      case 'starting':
        return 'Starting Backend';
      case 'checking':
      default:
        return 'Checking Backend...';
    }
  };

  const getStatusIcon = (status: BackendStatus['status']) => {
    switch (status) {
      case 'running':
        return '🟢';
      case 'error':
      case 'timeout':
        return '🔴';
      case 'starting':
        return '🟡';
      case 'checking':
      default:
        return '⚪';
    }
  };

  return (
    <div className={`flex items-center px-3 py-1 rounded-full border text-sm font-medium ${getStatusColor(status.status)}`}>
      <span className="mr-2">{getStatusIcon(status.status)}</span>
      <span>{getStatusText(status.status)}</span>
      {status.message && (
        <span className="ml-2 text-xs opacity-75">({status.message})</span>
      )}
    </div>
  );
};

export default BackendStatusIndicator;
