import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface BackendStatus {
  connected: boolean;
  port: number;
  processRunning: boolean;
  lastHeartbeat?: string;
}

interface BackendContextType {
  status: BackendStatus | null;
  updateStatus: (status: BackendStatus) => void;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  setError: (error: string | null) => void;
  restartBackend: () => Promise<void>;
}

const BackendContext = createContext<BackendContextType | undefined>(undefined);

export const useBackend = () => {
  const context = useContext(BackendContext);
  if (context === undefined) {
    throw new Error('useBackend must be used within a BackendProvider');
  }
  return context;
};

interface BackendProviderProps {
  children: ReactNode;
}

export const BackendStatusProvider: React.FC<BackendProviderProps> = ({ children }) => {
  // NON-BLOCKING: Start with a default connected state so UI loads immediately
  const [status, setStatus] = useState<BackendStatus>({
    connected: true, // Assume connected initially
    port: 5002,
    processRunning: true
  });
  const [isLoading, setIsLoading] = useState(false); // Start as not loading
  const [error, setError] = useState<string | null>(null);

  const updateStatus = (newStatus: BackendStatus) => {
    setStatus(newStatus);
    setIsLoading(false);
    if (newStatus.connected) {
      setError(null);
    }
  };

  const isConnected = status?.connected || false;

  const restartBackend = async () => {
    if (window.electronAPI) {
      try {
        setIsLoading(true);
        setError(null);
        await window.electronAPI.restartBackend();
      } catch (err) {
        setError(`Failed to restart backend: ${err instanceof Error ? err.message : 'Unknown error'}`);
        setIsLoading(false);
      }
    }
  };

    useEffect(() => {
    const setupElectronAPI = () => {
      console.log('BackendContext: Setting up Electron API listeners...');
      
      if (window.electronAPI && typeof window.electronAPI.onBackendStatus === 'function') {
        window.electronAPI.onBackendStatus((event: any, data: any) => {
          console.log('BackendContext: Backend status update received:', data);
          updateStatus({
            connected: data.connected,
            port: data.port || 5002,
            processRunning: data.processRunning
          });
        });

        if (typeof window.electronAPI.onBackendHeartbeat === 'function') {
          window.electronAPI.onBackendHeartbeat((event: any, data: any) => {
            setStatus(prev => ({
              ...prev,
              lastHeartbeat: data.timestamp
            }));
          });
        }

        if (typeof window.electronAPI.onShowError === 'function') {
          window.electronAPI.onShowError((event: any, data: any) => {
            setError(data.message);
            setIsLoading(false);
          });
        }
        
        console.log('✅ BackendContext: Electron API listeners set up successfully');
      } else {
        console.log('⚠️ BackendContext: electronAPI not available, using browser mode');
        // Browser mode - simulate connected status
        setTimeout(() => {
          updateStatus({
            connected: true,
            port: 5002,
            processRunning: true
          });
        }, 1000);
      }
    };

    // Check if we're in Electron and wait for electronAPI to be ready
    if (window.location.href.includes('file://')) {
      console.log('BackendContext: In Electron environment, checking electronAPI...');
      console.log('BackendContext: electronAPI object:', window.electronAPI);
      console.log('BackendContext: electronAPIReady flag:', window.electronAPIReady);
      console.log('BackendContext: electronAPIFullyReady flag:', window.electronAPIFullyReady);
      
      // Function to check if electronAPI is fully ready
      const checkElectronAPIReady = () => {
        if (window.electronAPI && 
            (window.electronAPIReady || window.electronAPIFullyReady) &&
            typeof window.electronAPI.onBackendStatus === 'function') {
          console.log('BackendContext: electronAPI fully ready, setting up...');
          setupElectronAPI();
          return true;
        }
        return false;
      };
      
      // Try immediate check
      if (checkElectronAPIReady()) {
        return;
      }
      
      // Wait for the event or check the flag
      const handleElectronAPIReady = () => {
        console.log('BackendContext: electronAPI ready event received, checking...');
        if (checkElectronAPIReady()) {
          window.removeEventListener('electronAPIReady', handleElectronAPIReady);
        }
      };
      
      window.addEventListener('electronAPIReady', handleElectronAPIReady);
      
      // NON-BLOCKING: Set a short timeout and then proceed anyway
      setTimeout(() => {
        console.log('BackendContext: Short timeout reached, proceeding with available electronAPI...');
        
        if (window.electronAPI) {
          console.log('BackendContext: Setting up with available electronAPI...');
          setupElectronAPI();
        } else {
          console.log('BackendContext: No electronAPI available, using browser mode');
          setupElectronAPI();
        }
      }, 1000); // Only wait 1 second instead of 5
    } else {
      // Browser mode
      console.log('BackendContext: In browser environment, using browser mode');
      setupElectronAPI();
    }
  }, []);

  const value: BackendContextType = {
    status,
    updateStatus,
    isConnected,
    isLoading,
    error,
    setError,
    restartBackend
  };

  return (
    <BackendContext.Provider value={value}>
      {children}
    </BackendContext.Provider>
  );
};
