const { app, BrowserWindow, Menu, ipcMain, shell } = require('electron');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let isBackendConnected = false;
let backendHealthCheckInterval = null;
let backendProcess = null;

// Keep a global reference of the window object
function createWindow() {
  console.log('🚀 Creating main window...');
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.icns'),
    titleBarStyle: 'hiddenInset', // macOS style
    show: true, // Show immediately for testing
    backgroundColor: '#ffffff'
  });

  console.log('✅ BrowserWindow created successfully');

  // Load the app
  if (isDev) {
    console.log('🔧 DEVELOPMENT MODE: Loading from localhost:3000');
    mainWindow.loadURL('http://localhost:3000');
    // Open DevTools in development
    mainWindow.webContents.openDevTools();
  } else {
    console.log('🚀 PRODUCTION MODE: Loading React application...');
    
    // Try multiple paths for the React build files
    const buildPaths = [
      path.join(__dirname, 'build', 'index.html'),  // Standard location
      path.join(process.resourcesPath, 'app', 'build', 'index.html'),  // electron-builder resources
      path.join(__dirname, '..', 'build', 'index.html'),  // Alternative
      path.join(process.cwd(), 'build', 'index.html')  // Current working directory
    ];
    
    console.log('🔍 Checking build paths...');
    let buildFound = false;
    
    for (const buildPath of buildPaths) {
      console.log('🔍 Checking:', buildPath);
      if (fs.existsSync(buildPath)) {
        console.log('✅ Build file found at:', buildPath);
        mainWindow.loadFile(buildPath);
        buildFound = true;
        break;
      }
    }
    
    if (!buildFound) {
      console.log('❌ No build files found, showing debug page');
      showComprehensiveDebugPage();
    }
  }

  // Show window immediately for testing
  mainWindow.show();
  console.log('✅ Window shown');

  // Add debugging for React app loading
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('✅ React app finished loading');
    console.log('🔍 Current URL:', mainWindow.webContents.getURL());
    console.log('🔍 Page title:', mainWindow.webContents.getTitle());
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error('❌ React app failed to load:', {
      errorCode,
      errorDescription,
      validatedURL
    });
  });

  // Automatically start backend when app launches
  console.log('🚀 Auto-starting backend service...');
  setTimeout(() => {
    startBackend();
  }, 1000); // Small delay to ensure window is ready

  // Handle window closed
  mainWindow.on('closed', () => {
    console.log('🔄 Window closed');
    mainWindow = null;
    stopBackendHealthCheck();
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  console.log('✅ Window setup complete');
}

function checkBackendConnection() {
  if (!mainWindow) return;
  
  console.log('🔍 Checking backend connection...');
  mainWindow.webContents.send('backend-status', 'checking');
  
  const options = {
    hostname: '127.0.0.1',
    port: 5002,
    path: '/health',
    method: 'GET'
  };

  const req = http.request(options, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      if (res.statusCode === 200) {
        try {
          const health = JSON.parse(data);
          console.log('✅ Backend connection successful:', health);
          isBackendConnected = true;
          mainWindow.webContents.send('backend-status', 'running');
          mainWindow.webContents.send('backend-ready');
          startBackendHealthCheck();
        } catch (error) {
          console.log('❌ Failed to parse backend response:', error.message);
          isBackendConnected = false;
          mainWindow.webContents.send('backend-status', 'error');
          mainWindow.webContents.send('backend-error', 'Invalid response format');
        }
      } else {
        console.log('❌ Backend health check failed with status:', res.statusCode);
        isBackendConnected = false;
        mainWindow.webContents.send('backend-status', 'error');
        mainWindow.webContents.send('backend-error', `HTTP ${res.statusCode}`);
      }
    });
  });

  req.on('error', (error) => {
    console.log('❌ Backend connection error:', error.message);
    isBackendConnected = false;
    mainWindow.webContents.send('backend-status', 'error');
    mainWindow.webContents.send('backend-error', error.message);
    
    // Try to start the backend if connection fails
    if (!backendProcess) {
      console.log('🔄 Attempting to start backend...');
      startBackend();
    }
  });

  req.end();
}

function startBackend() {
  if (backendProcess) {
    console.log('🔄 Backend already running, stopping...');
    backendProcess.kill();
  }
  
  console.log('🚀 Starting Rust backend...');
  
  // Handle both development and production paths
  let backendPath;
  if (isDev) {
    backendPath = path.join(__dirname, 'backend', 'backend');
  } else {
    // In production, the backend is in the app resources
    backendPath = path.join(process.resourcesPath, 'app', 'backend', 'backend');
  }
  
  console.log('🔍 Backend path:', backendPath);
  console.log('🔍 Resources path:', process.resourcesPath);
  console.log('🔍 Current directory:', __dirname);
  
  // Check if file exists
  if (!fs.existsSync(backendPath)) {
    console.log('❌ Backend binary not found at:', backendPath);
    
    // Try alternative paths
    const altPaths = [
      path.join(__dirname, 'backend', 'backend'),
      path.join(process.resourcesPath, 'backend', 'backend'),
      path.join(process.resourcesPath, 'app.asar.unpacked', 'backend', 'backend')
    ];
    
    for (const altPath of altPaths) {
      if (fs.existsSync(altPath)) {
        console.log('✅ Found backend at alternative path:', altPath);
        backendPath = altPath;
        break;
      }
    }
    
    if (!fs.existsSync(backendPath)) {
      console.log('❌ Backend binary not found at any path');
      if (mainWindow) {
        mainWindow.webContents.send('backend-status', 'error');
        mainWindow.webContents.send('backend-error', 'Backend binary not found');
      }
      return;
    }
  }
  
  console.log('✅ Backend binary found, starting process...');
  
  backendProcess = spawn(backendPath, [], {
    stdio: 'pipe',
    detached: false,
    cwd: path.dirname(backendPath)
  });
  
  backendProcess.stdout.on('data', (data) => {
    console.log('Backend stdout:', data.toString());
  });
  
  backendProcess.stderr.on('data', (data) => {
    console.log('Backend stderr:', data.toString());
  });
  
  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
    backendProcess = null;
    if (mainWindow) {
      mainWindow.webContents.send('backend-status', 'error');
      mainWindow.webContents.send('backend-error', `Backend exited with code ${code}`);
    }
  });
  
  backendProcess.on('error', (error) => {
    console.log('Backend process error:', error.message);
    console.log('Backend process error code:', error.code);
    console.log('Backend process error path:', error.path);
    backendProcess = null;
    if (mainWindow) {
      mainWindow.webContents.send('backend-status', 'error');
      mainWindow.webContents.send('backend-error', `Backend error: ${error.message}`);
    }
  });
  
  // Wait a bit for backend to start
  setTimeout(() => {
    console.log('🔄 Checking backend connection after startup...');
    checkBackendConnection();
  }, 3000);
}

function startBackendHealthCheck() {
  if (backendHealthCheckInterval) {
    clearInterval(backendHealthCheckInterval);
  }
  
  backendHealthCheckInterval = setInterval(() => {
    if (!mainWindow) return;
    
    const options = {
      hostname: '127.0.0.1',
      port: 5002,
      path: '/health',
      method: 'GET'
    };

    const req = http.request(options, (res) => {
      if (res.statusCode === 200) {
        if (!isBackendConnected) {
          console.log('🔄 Backend reconnected!');
          isBackendConnected = true;
          mainWindow.webContents.send('backend-status', 'running');
        }
      } else {
        if (isBackendConnected) {
          console.log('❌ Backend connection lost');
          isBackendConnected = false;
          mainWindow.webContents.send('backend-status', 'error');
        }
      }
    });

    req.on('error', (error) => {
      if (isBackendConnected) {
        console.log('❌ Backend connection error:', error.message);
        isBackendConnected = false;
        mainWindow.webContents.send('backend-status', 'error');
      }
    });

    req.end();
  }, 5000);
}

function stopBackendHealthCheck() {
  if (backendHealthCheckInterval) {
    clearInterval(backendHealthCheckInterval);
    backendHealthCheckInterval = null;
  }
}

function reconnectBackend() {
  console.log('🔄 Reconnecting to backend...');
  checkBackendConnection();
}

// Create application menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'New Project',
          accelerator: 'CmdOrCtrl+N',
          click: () => {
            mainWindow.webContents.send('menu-action', 'new-project');
          }
        },
        {
          label: 'Open Project',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow.webContents.send('menu-action', 'open-project');
          }
        },
        {
          label: 'Save Project',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.send('menu-action', 'save-project');
          }
        },
        { type: 'separator' },
        {
          label: 'Import Data',
          click: () => {
            mainWindow.webContents.send('menu-action', 'import-data');
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectall' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Backend',
      submenu: [
        {
          label: 'Check Connection',
          click: () => {
            checkBackendConnection();
          }
        },
        {
          label: 'Reconnect',
          click: () => {
            reconnectBackend();
          }
        }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Unified Data Studio',
          click: () => {
            mainWindow.webContents.send('menu-action', 'about');
          }
        },
        {
          label: 'Documentation',
          click: () => {
            shell.openExternal('https://github.com/your-username/unified-data-studio');
          }
        }
      ]
    }
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

// This method will be called when Electron has finished

// App event handlers
app.whenReady().then(() => {
  createWindow();
  createMenu();
  // Don't start backend - just check connection

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Clean up backend process
  if (backendProcess) {
    console.log('🔄 Stopping backend process...');
    backendProcess.kill();
    backendProcess = null;
  }
  stopBackendHealthCheck();
});

// IPC handlers for communication with renderer process
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-app-name', () => {
  return app.getName();
});

// Handle backend communication
ipcMain.handle('backend-request', async (event, endpoint, data) => {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(data);
    
    const options = {
      hostname: '127.0.0.1',
      port: 5002,
      path: endpoint,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve(response);
        } catch (error) {
          reject(new Error('Invalid response format'));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    req.write(postData);
    req.end();
  });
});

// Comprehensive debug page for critical failures
function showComprehensiveDebugPage() {
  const debugHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>🚨 CRITICAL ERROR - Unified Data Studio</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          margin: 0;
          padding: 40px;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .debug-container {
          background: rgba(0, 0, 0, 0.8);
          border-radius: 20px;
          padding: 40px;
          max-width: 800px;
          width: 100%;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        .error-header {
          text-align: center;
          margin-bottom: 30px;
        }
        .error-icon {
          font-size: 4rem;
          margin-bottom: 20px;
        }
        .error-title {
          font-size: 2.5rem;
          font-weight: bold;
          margin-bottom: 10px;
          color: #ff6b6b;
        }
        .error-subtitle {
          font-size: 1.2rem;
          opacity: 0.9;
          margin-bottom: 30px;
        }
        .debug-section {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          padding: 20px;
          margin-bottom: 20px;
        }
        .debug-title {
          font-size: 1.3rem;
          font-weight: bold;
          margin-bottom: 15px;
          color: #74b9ff;
        }
        .debug-content {
          font-family: 'Monaco', 'Menlo', monospace;
          font-size: 0.9rem;
          background: rgba(0, 0, 0, 0.5);
          padding: 15px;
          border-radius: 8px;
          overflow-x: auto;
          white-space: pre-wrap;
          word-break: break-all;
        }
        .action-buttons {
          display: flex;
          gap: 15px;
          justify-content: center;
          margin-top: 30px;
        }
        .btn {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
        }
        .btn-primary {
          background: #00b894;
          color: white;
        }
        .btn-primary:hover {
          background: #00a085;
          transform: translateY(-2px);
        }
        .btn-secondary {
          background: #fdcb6e;
          color: #2d3436;
        }
        .btn-secondary:hover {
          background: #f39c12;
          transform: translateY(-2px);
        }
        .status-indicator {
          display: inline-block;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-right: 8px;
        }
        .status-success { background: #00b894; }
        .status-error { background: #e17055; }
        .status-warning { background: #fdcb6e; }
      </style>
    </head>
    <body>
      <div class="debug-container">
        <div class="error-header">
          <div class="error-icon">🚨</div>
          <h1 class="error-title">CRITICAL ERROR</h1>
          <p class="error-subtitle">React application failed to load</p>
        </div>
        
        <div class="debug-section">
          <h2 class="debug-title">🔍 File System Analysis</h2>
          <div class="debug-content">
            <span class="status-indicator status-error"></span>__dirname: ${__dirname}
            <span class="status-indicator status-error"></span>process.cwd(): ${process.cwd()}
            <span class="status-indicator status-error"></span>process.resourcesPath: ${process.resourcesPath}
            <span class="status-indicator status-error"></span>process.execPath: ${process.execPath}
            <span class="status-indicator status-error"></span>process.versions.electron: ${process.versions.electron}
          </div>
        </div>
        
        <div class="debug-section">
          <h2 class="debug-title">📁 Expected File Locations</h2>
          <div class="debug-content">
            <span class="status-indicator status-error"></span>Primary: ${path.join(__dirname, 'build', 'index.html')}
            <span class="status-indicator status-error"></span>Alt 1: ${path.join(process.resourcesPath, 'app', 'build', 'index.html')}
            <span class="status-indicator status-error"></span>Alt 2: ${path.join(__dirname, '..', 'build', 'index.html')}
            <span class="status-indicator status-error"></span>Alt 3: ${path.join(process.cwd(), 'build', 'index.html')}
            <span class="status-indicator status-error"></span>Alt 3: ${path.join(__dirname, '..', '..', 'build', 'index.html')}
            <span class="status-indicator status-error"></span>Alt 4: ${path.join(__dirname, '..', '..', 'build', 'index.html')}
            <span class="status-indicator status-error"></span>Alt 5: ${path.join(process.resourcesPath, 'build', 'index.html')}
          </div>
        </div>
        
        <div class="debug-section">
          <h2 class="debug-title">⚡ Electron Environment</h2>
          <div class="debug-content">
            <span class="status-indicator status-success"></span>Platform: ${process.platform}
            <span class="status-indicator status-success"></span>Architecture: ${process.arch}
            <span class="status-indicator status-success"></span>Node Version: ${process.versions.node}
            <span class="status-indicator status-success"></span>Chrome Version: ${process.versions.chrome}
            <span class="status-indicator status-success"></span>Electron Version: ${process.versions.electron}
          </div>
        </div>
        
        <div class="debug-section">
          <h2 class="debug-title">🔧 Troubleshooting Steps</h2>
          <div class="debug-content">
            1. Check if build/ directory exists in the app bundle
            2. Verify electron-builder configuration in package.json
            3. Ensure React build completed successfully
            4. Check file permissions and paths
            5. Verify extraResources configuration
            6. Check for build script errors
          </div>
        </div>
        
        <div class="action-buttons">
          <button class="btn btn-primary" onclick="window.location.reload()">
            🔄 Retry Loading
          </button>
          <button class="btn btn-secondary" onclick="window.electronAPI?.openDevTools()">
            🛠️ Open DevTools
          </button>
        </div>
      </div>
    </body>
    </html>
  `;
  
  mainWindow.loadURL(`data:text/html,${encodeURIComponent(debugHTML)}`);
}

// IPC handlers for backend status
ipcMain.handle('get-backend-status', () => {
  console.log('🔍 get-backend-status requested, current state:', {
    isBackendConnected,
    mainWindowExists: !!mainWindow
  });
  
  if (isBackendConnected) return 'running';
  return 'stopped';
});

ipcMain.handle('restart-backend', () => {
  reconnectBackend();
  return 'reconnecting';
});

ipcMain.handle('start-backend', () => {
  checkBackendConnection();
  return 'checking';
});

ipcMain.handle('stop-backend', () => {
  // No backend to stop since we're not managing it
  return 'stopped';
});

ipcMain.handle('check-backend-health', async () => {
  console.log('🏥 Manual health check requested from frontend');
  
  return new Promise((resolve) => {
    const options = {
      hostname: '127.0.0.1',
      port: 5002,
      path: '/health',
      method: 'GET'
    };

    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const health = JSON.parse(data);
            console.log('✅ Health check successful:', health);
            resolve({ status: 'healthy', data: health });
          } catch (error) {
            console.log('❌ Health check failed to parse response');
            resolve({ status: 'unhealthy', error: 'Invalid response format' });
          }
        } else {
          console.log('❌ Health check failed with status:', res.statusCode);
          resolve({ status: 'unhealthy', error: `HTTP ${res.statusCode}` });
        }
      });
    });

    req.on('error', (error) => {
      console.log('❌ Health check error:', error.message);
      resolve({ status: 'error', error: error.message });
    });

    req.end();
  });
});
