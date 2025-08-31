// Simple BackendStatusService for now
export interface BackendStatus {
  status: 'checking' | 'starting' | 'running' | 'stopped' | 'error' | 'timeout';
  message?: string;
  timestamp: Date;
}

class BackendStatusService {
  private listeners: Set<(status: BackendStatus) => void> = new Set();
  private currentStatus: BackendStatus = {
    status: 'checking',
    timestamp: new Date()
  };

  constructor() {
    console.log('🚀 BackendStatusService: Initializing...');
    this.startHealthChecks();
  }

  private startHealthChecks() {
    console.log('Starting health checks...');
    setInterval(async () => {
      await this.performHealthCheck();
    }, 3000);
  }

  private async performHealthCheck() {
    try {
      const response = await fetch('http://localhost:5002/health');
      if (response.ok) {
        this.updateStatus('running');
      } else {
        this.updateStatus('error', 'Backend unhealthy');
      }
    } catch (error) {
      this.updateStatus('error', 'Backend connection failed');
    }
  }

  private updateStatus(status: BackendStatus['status'], message?: string) {
    const newStatus: BackendStatus = {
      status,
      message,
      timestamp: new Date()
    };

    if (this.currentStatus.status !== status || this.currentStatus.message !== message) {
      this.currentStatus = newStatus;
      this.listeners.forEach((listener) => {
        try {
          listener(newStatus);
        } catch (error) {
          console.error('Error in listener:', error);
        }
      });
    }
  }

  public getCurrentStatus(): BackendStatus {
    return { ...this.currentStatus };
  }

  public subscribe(listener: (status: BackendStatus) => void): () => void {
    this.listeners.add(listener);
    listener(this.currentStatus);
    
    return () => {
      this.listeners.delete(listener);
    };
  }

  public async restartBackend(): Promise<void> {
    this.updateStatus('starting');
    window.location.reload();
  }

  public async checkBackendHealth(): Promise<any> {
    try {
      const response = await fetch('http://localhost:5002/health');
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      throw new Error(`Health check failed: ${error}`);
    }
  }

  public destroy() {
    this.listeners.clear();
  }
}

export const backendStatusService = new BackendStatusService();
export default backendStatusService;
