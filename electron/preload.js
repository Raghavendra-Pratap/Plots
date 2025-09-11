const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  openFile: () => ipcRenderer.invoke('open-file'),
  saveFile: (data) => ipcRenderer.invoke('save-file', data),
  
  // App information
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getAppName: () => ipcRenderer.invoke('get-app-name'),
  
  // Listeners
  onFileOpened: (callback) => ipcRenderer.on('file-opened', callback),
  onSaveAnnotations: (callback) => ipcRenderer.on('save-annotations', callback),
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// Handle window events
window.addEventListener('DOMContentLoaded', () => {
  // Add platform-specific CSS classes
  const platform = process.platform;
  document.body.classList.add(`platform-${platform}`);
  
  // Handle file drops
  document.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
  });
  
  document.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.toLowerCase().endsWith('.csv')) {
        // Trigger file open event
        window.electronAPI.onFileOpened(() => {
          // Handle file in React app
          const event = new CustomEvent('csv-file-dropped', { 
            detail: { file } 
          });
          document.dispatchEvent(event);
        });
      }
    }
  });
}); 