declare global {
  interface Window {
    electronAPI?: {
      getBackendStatus: () => Promise<string>;
      startBackend: () => Promise<string>;
      stopBackend: () => Promise<string>;
      restartBackend: () => Promise<string>;
      onBackendStatus: (callback: (event: any, status: any) => void) => void;
      onBackendReady: (callback: (event: any) => void) => void;
      onBackendError: (callback: (event: any, error: any) => void) => void;
      onBackendClosed: (callback: (event: any) => void) => void;
      onBackendHeartbeat: (callback: (event: any, data: any) => void) => void;
      onShowError: (callback: (event: any, data: any) => void) => void;
      removeAllListeners: (channel: string) => void;
      platform: string;
      isElectron: boolean;
    };
      electronAPIReady?: boolean;
  electronAPIFullyReady?: boolean;
  API_BASE_URL?: string;
  }
}

export {};
