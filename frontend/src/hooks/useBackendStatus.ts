import { useState, useEffect } from 'react';
import { backendStatusService, BackendStatus } from '../services/BackendStatusService';

/**
 * Hook to get real-time backend status
 * Automatically subscribes to status updates and unsubscribes on unmount
 */
export function useBackendStatus() {
  console.log('🔌 useBackendStatus: Hook initialized');
  
  const [status, setStatus] = useState<BackendStatus>(() => {
    const currentStatus = backendStatusService.getCurrentStatus();
    console.log('🔌 useBackendStatus: Initial status:', currentStatus);
    return currentStatus;
  });

  useEffect(() => {
    console.log('🔌 useBackendStatus: Setting up subscription...');
    
    // Subscribe to status updates
    const unsubscribe = backendStatusService.subscribe((newStatus) => {
      console.log('🔌 useBackendStatus: Received status update:', newStatus);
      setStatus(newStatus);
    });

    console.log('🔌 useBackendStatus: Subscription active');

    // Cleanup on unmount
    return () => {
      console.log('🔌 useBackendStatus: Cleaning up subscription...');
      unsubscribe();
    };
  }, []);

  const restartBackend = async () => {
    console.log('🔌 useBackendStatus: Restart backend requested');
    await backendStatusService.restartBackend();
  };

  const checkHealth = async () => {
    console.log('🔌 useBackendStatus: Manual health check requested');
    try {
      const result = await backendStatusService.checkBackendHealth();
      console.log('🔌 useBackendStatus: Health check result:', result);
      return result;
    } catch (error) {
      console.error('🔌 useBackendStatus: Health check failed:', error);
      throw error;
    }
  };

  const result = {
    status,
    restartBackend,
    checkHealth,
    isConnected: status.status === 'running',
    isChecking: status.status === 'checking',
    isStarting: status.status === 'starting',
    isError: status.status === 'error',
    isStopped: status.status === 'stopped',
    isTimeout: status.status === 'timeout'
  };

  console.log('�� useBackendStatus: Returning result:', result);

  return result;
}
