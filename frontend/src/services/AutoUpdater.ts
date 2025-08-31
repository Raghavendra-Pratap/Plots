import { ipcRenderer } from 'electron';

export interface UpdateInfo {
  version: string;
  releaseDate: string;
  downloadUrl: string;
  changelog: string;
  isLatest: boolean;
}

export interface UpdateProgress {
  percent: number;
  speed: number;
  eta: number;
}

export class AutoUpdaterService {
  private static instance: AutoUpdaterService;
  private updateCheckInterval: NodeJS.Timeout | null = null;
  private isChecking = false;

  private constructor() {}

  public static getInstance(): AutoUpdaterService {
    if (!AutoUpdaterService.instance) {
      AutoUpdaterService.instance = new AutoUpdaterService();
    }
    return AutoUpdaterService.instance;
  }

  public startAutoUpdateCheck(intervalMinutes: number = 60): void {
    if (this.updateCheckInterval) {
      clearInterval(this.updateCheckInterval);
    }

    this.updateCheckInterval = setInterval(() => {
      this.checkForUpdates();
    }, intervalMinutes * 60 * 1000);

    this.checkForUpdates();
  }

  public stopAutoUpdateCheck(): void {
    if (this.updateCheckInterval) {
      clearInterval(this.updateCheckInterval);
      this.updateCheckInterval = null;
    }
  }

  public async checkForUpdates(): Promise<UpdateInfo | null> {
    if (this.isChecking) return null;
    this.isChecking = true;

    try {
      const response = await fetch('https://api.github.com/repos/Raghavendra-Pratap/Data_Studio/releases/latest');
      if (!response.ok) throw new Error(`Failed to fetch releases: ${response.statusText}`);

      const release = await response.json();
      const currentVersion = this.getCurrentVersion();
      const latestVersion = release.tag_name.replace('v', '');

      if (this.isNewerVersion(latestVersion, currentVersion)) {
        const updateInfo: UpdateInfo = {
          version: latestVersion,
          releaseDate: release.published_at,
          downloadUrl: release.assets[0]?.browser_download_url || '',
          changelog: release.body || 'No changelog available',
          isLatest: false
        };
        this.notifyUpdateAvailable(updateInfo);
        return updateInfo;
      }
      return null;
    } catch (error) {
      console.error('Error checking for updates:', error);
      return null;
    } finally {
      this.isChecking = false;
    }
  }

  public async downloadUpdate(updateInfo: UpdateInfo): Promise<void> {
    try {
      ipcRenderer.send('download-update', updateInfo);
    } catch (error) {
      console.error('Error downloading update:', error);
      throw error;
    }
  }

  public async installUpdate(): Promise<void> {
    try {
      ipcRenderer.send('install-update');
    } catch (error) {
      console.error('Error installing update:', error);
      throw error;
    }
  }

  private getCurrentVersion(): string {
    return '1.0.0';
  }

  private isNewerVersion(newVersion: string, currentVersion: string): boolean {
    const newParts = newVersion.split('.').map(Number);
    const currentParts = currentVersion.split('.').map(Number);

    for (let i = 0; i < Math.max(newParts.length, currentParts.length); i++) {
      const newPart = newParts[i] || 0;
      const currentPart = currentParts[i] || 0;
      if (newPart > currentPart) return true;
      if (newPart < currentPart) return false;
    }
    return false;
  }

  private notifyUpdateAvailable(updateInfo: UpdateInfo): void {
    const event = new CustomEvent('updateAvailable', { detail: updateInfo });
    window.dispatchEvent(event);

    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Data Studio Update Available', {
        body: `Version ${updateInfo.version} is available for download`,
        icon: '/favicon.ico'
      });
    }
  }

  public onUpdateProgress(callback: (progress: UpdateProgress) => void): void {
    ipcRenderer.on('update-progress', (_, progress: UpdateProgress) => {
      callback(progress);
    });
  }

  public onUpdateComplete(callback: () => void): void {
    ipcRenderer.on('update-complete', () => {
      callback();
    });
  }

  public onUpdateError(callback: (error: string) => void): void {
    ipcRenderer.on('update-error', (_, error: string) => {
      callback(error);
    });
  }
}

export default AutoUpdaterService.getInstance();
