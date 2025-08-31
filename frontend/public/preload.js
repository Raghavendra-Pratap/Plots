const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Backend status and control
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),
  startBackend: () => ipcRenderer.invoke('start-backend'),
  stopBackend: () => ipcRenderer.invoke('stop-backend'),
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  
  // Listen for backend events
  onBackendStatus: (callback) => ipcRenderer.on('backend-status', callback),
  onBackendReady: (callback) => ipcRenderer.on('backend-ready', callback),
  onBackendError: (callback) => ipcRenderer.on('backend-error', callback),
  onBackendClosed: (callback) => ipcRenderer.on('backend-closed', callback),
  onBackendHeartbeat: (callback) => ipcRenderer.on('backend-heartbeat', callback),
  onShowError: (callback) => ipcRenderer.on('show-error', callback),
  
  // Loading screen events
  onLoadingStatus: (callback) => ipcRenderer.on('loading-status', callback),
  
  // App events
  onNewProject: (callback) => ipcRenderer.on('new-project', callback),
  onOpenProject: (callback) => ipcRenderer.on('open-project', callback),
  onShowAbout: (callback) => ipcRenderer.on('show-about', callback),
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // Platform info
  platform: process.platform,
  isElectron: true,
  
  // Direct backend health check
  checkBackendHealth: async () => {
    try {
      const response = await fetch('http://localhost:5002/health');
      if (response.ok) {
        const data = await response.json();
        return { status: 'connected', data };
      } else {
        return { status: 'error', error: 'Backend not responding' };
      }
    } catch (error) {
      return { status: 'error', error: error.message };
    }
  }
});

// Handle window load
window.addEventListener('DOMContentLoaded', () => {
  console.log('Electron app loaded');
  
  // Update API base URL for Electron
  if (window.location.href.includes('file://')) {
    // We're running in Electron, update API calls to use localhost
    window.API_BASE_URL = 'http://localhost:5002';
    console.log('Running in Electron, API base URL:', window.API_BASE_URL);
    console.log('✅ Preload script completed successfully');
    
    // Mark electronAPI as ready immediately since it's already exposed
    console.log('✅ electronAPI exposed, marking as ready');
    window.electronAPIReady = true;
    
    // Dispatch multiple events to ensure React catches at least one
    console.log('✅ Dispatching electronAPIReady event');
    window.dispatchEvent(new CustomEvent('electronAPIReady'));
    
    // Dispatch multiple times with delays to ensure React catches it
    setTimeout(() => {
      console.log('✅ Dispatching delayed electronAPIReady event (100ms)');
      window.dispatchEvent(new CustomEvent('electronAPIReady'));
    }, 100);
    
    setTimeout(() => {
      console.log('✅ Dispatching delayed electronAPIReady event (500ms)');
      window.dispatchEvent(new CustomEvent('electronAPIReady'));
    }, 500);
    
    setTimeout(() => {
      console.log('✅ Dispatching delayed electronAPIReady event (1000ms)');
      window.dispatchEvent(new CustomEvent('electronAPIReady'));
    }, 1000);
    
    // Also set a global flag that React can check directly
    window.electronAPIFullyReady = true;
    console.log('✅ electronAPIFullyReady flag set to true');
  }
});

function addBackendStatusIndicator() {
  // Simple check for electronAPI
  if (!window.electronAPI) {
    console.log('⚠️ electronAPI not available, running in browser mode');
    return;
  }
  
  console.log('✅ electronAPI available, setting up backend status indicator');

  // Create a backend status indicator
  const statusDiv = document.createElement('div');
  statusDiv.id = 'electron-backend-status';
  statusDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 16px;
    border-radius: 25px;
    font-size: 14px;
    font-weight: bold;
    z-index: 10000;
    transition: all 0.3s ease;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border: 2px solid transparent;
  `;
  
  // Initial status
  updateBackendStatus('checking');
  
  // Add click handler to restart backend
  statusDiv.addEventListener('click', () => {
    console.log('Backend status indicator clicked - restarting backend');
    if (window.electronAPI && window.electronAPI.restartBackend) {
      window.electronAPI.restartBackend();
    } else {
      console.error('❌ restartBackend not available');
    }
  });
  
  // Add to page
  document.body.appendChild(statusDiv);
  console.log('✅ Backend status indicator added to page');
  
  // Listen for status updates from Electron
  if (window.electronAPI && window.electronAPI.onBackendStatus) {
    window.electronAPI.onBackendStatus((event, status) => {
      console.log('🔍 Backend status update received:', status);
      updateBackendStatus(status);
    });
  }
  
  // Also listen for backend ready
  if (window.electronAPI && window.electronAPI.onBackendReady) {
    window.electronAPI.onBackendReady((event) => {
      console.log('🎉 Backend ready signal received!');
      updateBackendStatus('running');
    });
  }
  
  // Also listen for backend error
  if (window.electronAPI && window.electronAPI.onBackendError) {
    window.electronAPI.onBackendError((event, error) => {
      console.log('❌ Backend error received:', error);
      updateBackendStatus('error');
    });
  }
  
  // Direct health check every 3 seconds
  const healthCheckInterval = setInterval(async () => {
    try {
      const health = await window.electronAPI.checkBackendHealth();
      console.log('🏥 Backend health check result:', health);
      
      if (health.status === 'connected') {
        updateBackendStatus('running');
      } else {
        updateBackendStatus('error');
      }
    } catch (error) {
      console.log('❌ Health check failed:', error);
      updateBackendStatus('error');
    }
  }, 3000);
  
  // Initial health check after 2 seconds
  setTimeout(async () => {
    try {
      const health = await window.electronAPI.checkBackendHealth();
      console.log('🏥 Initial backend health check:', health);
      
      if (health.status === 'connected') {
        updateBackendStatus('running');
      }
    } catch (error) {
      console.log('❌ Initial health check failed:', error);
    }
  }, 2000);
  
  function updateBackendStatus(status) {
    console.log('🔄 Updating backend status to:', status);
    let text, color, bgColor, borderColor;
    
    switch (status) {
      case 'starting':
        text = '🔄 Starting Backend...';
        color = '#ffffff';
        bgColor = '#f59e0b';
        borderColor = '#d97706';
        break;
      case 'running':
        text = '✅ Backend Connected!';
        color = '#ffffff';
        bgColor = '#10b981';
        borderColor = '#059669';
        break;
      case 'stopped':
        text = '⏹️ Backend Stopped';
        color = '#ffffff';
        bgColor = '#6b7280';
        borderColor = '#4b5563';
        break;
      case 'error':
        text = '❌ Backend Error';
        color = '#ffffff';
        bgColor = '#ef4444';
        borderColor = '#dc2626';
        break;
      case 'timeout':
        text = '⏰ Backend Timeout';
        color = '#ffffff';
        bgColor = '#f59e0b';
        borderColor = '#d97706';
        break;
      default:
        text = '❓ Checking Backend...';
        color = '#ffffff';
        bgColor = '#6b7280';
        borderColor = '#4b5563';
    }
    
    statusDiv.textContent = text;
    statusDiv.style.color = color;
    statusDiv.style.backgroundColor = bgColor;
    statusDiv.style.borderColor = borderColor;
    
    // Add tooltip
    statusDiv.title = `Click to restart backend (Current: ${status})`;
    
    console.log(`✅ Backend status updated to: ${status}`);
  }
}
