const { ipcMain, dialog, app } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const fs = require('fs');
const https = require('https');
const { exec } = require('child_process');

class UpdateHandler {
  constructor(mainWindow) {
    this.mainWindow = mainWindow;
    this.setupIpcHandlers();
    this.setupAutoUpdater();
  }

  setupIpcHandlers() {
    // Handle manual update check
    ipcMain.handle('check-for-updates', async () => {
      try {
        const result = await autoUpdater.checkForUpdates();
        return result;
      } catch (error) {
        console.error('Error checking for updates:', error);
        throw error;
      }
    });

    // Handle update download
    ipcMain.on('download-update', async (event, updateInfo) => {
      try {
        await this.downloadUpdate(updateInfo);
      } catch (error) {
        console.error('Error downloading update:', error);
        this.mainWindow.webContents.send('update-error', error.message);
      }
    });

    // Handle update installation
    ipcMain.on('install-update', async () => {
      try {
        await this.installUpdate();
      } catch (error) {
        console.error('Error installing update:', error);
        this.mainWindow.webContents.send('update-error', error.message);
      }
    });

    // Handle manual update download from GitHub
    ipcMain.handle('download-github-update', async (event, updateInfo) => {
      try {
        return await this.downloadFromGitHub(updateInfo);
      } catch (error) {
        console.error('Error downloading from GitHub:', error);
        throw error;
      }
    });
  }

  setupAutoUpdater() {
    // Configure auto-updater
    autoUpdater.autoDownload = false;
    autoUpdater.autoInstallOnAppQuit = true;

    // Update events
    autoUpdater.on('checking-for-update', () => {
      this.mainWindow.webContents.send('update-status', 'Checking for updates...');
    });

    autoUpdater.on('update-available', (info) => {
      this.mainWindow.webContents.send('update-available', info);
    });

    autoUpdater.on('update-not-available', () => {
      this.mainWindow.webContents.send('update-status', 'No updates available');
    });

    autoUpdater.on('error', (err) => {
      this.mainWindow.webContents.send('update-error', err.message);
    });

    autoUpdater.on('download-progress', (progressObj) => {
      this.mainWindow.webContents.send('update-progress', {
        percent: progressObj.percent,
        speed: progressObj.bytesPerSecond,
        eta: progressObj.eta
      });
    });

    autoUpdater.on('update-downloaded', (info) => {
      this.mainWindow.webContents.send('update-downloaded', info);
    });

    autoUpdater.on('update-downloaded', (info) => {
      // Prompt user to install update
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: 'Update Ready',
        message: 'Update downloaded successfully. Would you like to install it now?',
        detail: `Version ${info.version} is ready to install.`,
        buttons: ['Install Now', 'Install Later'],
        defaultId: 0
      }).then((result) => {
        if (result.response === 0) {
          autoUpdater.quitAndInstall();
        }
      });
    });
  }

  async downloadUpdate(updateInfo) {
    try {
      // Start download
      await autoUpdater.downloadUpdate();
    } catch (error) {
      throw new Error(`Failed to download update: ${error.message}`);
    }
  }

  async installUpdate() {
    try {
      // Install the downloaded update
      autoUpdater.quitAndInstall();
    } catch (error) {
      throw new Error(`Failed to install update: ${error.message}`);
    }
  }

  async downloadFromGitHub(updateInfo) {
    return new Promise((resolve, reject) => {
      const downloadUrl = updateInfo.downloadUrl;
      const fileName = path.basename(downloadUrl);
      const downloadPath = path.join(app.getPath('temp'), fileName);

      // Create write stream
      const file = fs.createWriteStream(downloadPath);
      
      // Download file
      https.get(downloadUrl, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`Failed to download: ${response.statusCode}`));
          return;
        }

        const totalSize = parseInt(response.headers['content-length'], 10);
        let downloadedSize = 0;

        response.on('data', (chunk) => {
          downloadedSize += chunk.length;
          const progress = (downloadedSize / totalSize) * 100;
          
          this.mainWindow.webContents.send('update-progress', {
            percent: Math.round(progress),
            speed: chunk.length,
            eta: Math.round((totalSize - downloadedSize) / chunk.length)
          });
        });

        response.pipe(file);

        file.on('finish', () => {
          file.close();
          resolve({
            success: true,
            filePath: downloadPath,
            fileName: fileName
          });
        });

        file.on('error', (err) => {
          fs.unlink(downloadPath, () => {}); // Delete the file
          reject(new Error(`File write error: ${err.message}`));
        });
      }).on('error', (err) => {
        reject(new Error(`Download error: ${err.message}`));
      });
    });
  }

  // Check for updates on app start
  async checkForUpdatesOnStart() {
    try {
      // Wait a bit for the app to fully load
      setTimeout(async () => {
        await autoUpdater.checkForUpdates();
      }, 5000);
    } catch (error) {
      console.error('Error checking for updates on start:', error);
    }
  }
}

module.exports = UpdateHandler;
